from __future__ import annotations
import os
import time
from pathlib import Path
from threading import Lock
from typing import Callable
from dataclasses import dataclass, field
from app.config import Settings
from app.hardware.simulators import RadarSimulator, ESP32Simulator, EncoderSimulator, MotorDriverSimulator
from app.camera import PiUvcCameraAdapter
from app.imu import Bno055Adapter, Bno055Sensor, ImuConfig, create_bno055_sensor
from app.thermal import Mlx90640Adapter, Mlx90640Sensor, ThermalConfig, create_mlx90640_sensor
from app.services.pipeline import Pipeline
from app.gnss import GnssFix, GnssLocationService, GnssSimulator
from app.gnss_driver import GnssReader, pyserial_opener
from app.communication.esp32.protocol import ESP32Client, ESP32ProtocolSimulator
from app.communication.esp32.serial_transport import BidirectionalSerialTransport, SerialTransportConfig
from app.communication.esp32.usb import Esp32UsbConfig, IdentityGatedESP32UsbTransport
from app.logging.store import EventStore
from app.replay.store import RecordingStore, RecordingError
from app.sensors.ld2450.adapter import LD2450Adapter, LD2450RawCaptureConfig, LD2450RawCaptureWorker


def _configured_esp32() -> Esp32UsbConfig:
    raw_baud = os.getenv("TARK_ESP32_BAUD", "").strip()
    try:
        baudrate = int(raw_baud) if raw_baud else None
    except ValueError:
        baudrate = None
    try:
        timeout_s = float(os.getenv("TARK_ESP32_SERIAL_TIMEOUT_S", "0.5"))
    except ValueError:
        timeout_s = 0.5
    return Esp32UsbConfig(os.getenv("TARK_ESP32_DEVICE_PATH", "").strip(), baudrate, max(0.1, timeout_s))

@dataclass
class TarkSystem:
    """Owns simulation plus explicitly selected, non-actuating adapters."""
    settings: Settings
    pipeline: Pipeline = field(init=False)
    gnss: GnssLocationService = field(default_factory=GnssLocationService)
    gnss_simulator: GnssSimulator = field(default_factory=GnssSimulator)
    radar: RadarSimulator = field(default_factory=RadarSimulator)
    esp32: ESP32Simulator = field(default_factory=ESP32Simulator)
    encoders: EncoderSimulator = field(default_factory=EncoderSimulator)
    motor: MotorDriverSimulator = field(default_factory=MotorDriverSimulator)
    camera: PiUvcCameraAdapter = field(default_factory=PiUvcCameraAdapter)
    thermal: Mlx90640Adapter = field(default_factory=Mlx90640Adapter)
    imu: Bno055Adapter = field(default_factory=Bno055Adapter)
    gnss_opener_factory: Callable[[str, int, float], Callable] = pyserial_opener
    ld2450_factory: Callable[..., LD2450Adapter] = LD2450Adapter
    esp32_usb_factory: Callable[[Esp32UsbConfig], IdentityGatedESP32UsbTransport] = IdentityGatedESP32UsbTransport
    imu_sensor_factory: Callable[[ImuConfig], Bno055Sensor] = create_bno055_sensor
    thermal_sensor_factory: Callable[[ThermalConfig], Mlx90640Sensor] = create_mlx90640_sensor
    esp32_endpoint: ESP32ProtocolSimulator = field(init=False)
    esp32_client: ESP32Client = field(init=False)
    event_store: EventStore = field(init=False)
    recording_store: RecordingStore = field(init=False)
    gnss_reader: GnssReader | None = field(default=None, init=False)
    esp32_usb: IdentityGatedESP32UsbTransport | None = field(default=None, init=False)
    esp32_transport: BidirectionalSerialTransport | None = field(default=None, init=False)
    ld2450_capture: LD2450RawCaptureWorker | None = field(default=None, init=False)
    _location_step: int = field(default=0, init=False)
    _location_lock: Lock = field(default_factory=Lock, init=False, repr=False)

    @property
    def hardware_runtime_requested(self) -> bool:
        """Replay is offline; only the reviewed hardware-capable mode may open adapters."""
        return self.settings.mode == "real_radar"
    def __post_init__(self):
        self.pipeline=Pipeline(self.settings)
        # This deterministic in-process endpoint is the only current runtime
        # transport. It exists to exercise Protocol V1—not to represent USB,
        # ESP32 hardware, PWM, motor motion, or a physical acknowledgement.
        self.esp32_endpoint=ESP32ProtocolSimulator(self.settings.configuration_hash)
        self.esp32_client=ESP32Client(self.esp32_endpoint)
        database_path=Path(os.getenv("TARK_DATABASE_PATH","data/database/tark.db"))
        self.event_store=EventStore(database_path)
        self.recording_store=RecordingStore(database_path)
        # Simulation is the default and never opens a physical device.  In the
        # explicit real-radar runtime, each configured boundary remains separate
        # and failure-tolerant; no adapter has motor authority.
        if self.hardware_runtime_requested:
            self._start_configured_gnss()
            self._start_configured_camera()
            self._select_configured_esp32()
            self._start_configured_ld2450_raw_capture()
            self._start_configured_i2c_sensors()

    def _start_configured_gnss(self) -> None:
        config = self.gnss.config
        if not config.device_path:
            return
        opener = self.gnss_opener_factory(config.device_path, config.baud, config.serial_timeout_s)
        self.gnss_reader = GnssReader(
            opener, self.ingest_gnss_fix,
            reconnect_s=config.reconnect_interval_s,
            max_line_bytes=config.max_line_bytes,
            raw_log_path=config.raw_log_path if config.raw_log_enabled else None,
            on_state=self.update_gnss_receiver_state,
        )
        self.gnss_reader.start()

    def _start_configured_camera(self) -> None:
        if self.camera.config.device_path:
            self.camera.start()

    def _start_configured_i2c_sensors(self) -> None:
        """Start only configured sensors with previously recorded identity.

        An I²C address is merely a candidate location.  The optional driver is
        not imported or instantiated until the adapter is identity-verified,
        so default and simulation startup cannot probe an I²C bus.
        """
        self._start_configured_imu()
        self._start_configured_thermal()

    def _start_configured_imu(self) -> bool:
        if not self.hardware_runtime_requested or not self.imu.config.address:
            return False
        if self.imu.identity.state != "VERIFIED":
            return False
        if self.imu.worker is not None:
            return False
        try:
            return self.imu.start_verified_sensor(self.imu_sensor_factory(self.imu.config))
        except Exception as error:
            self.imu.report_startup_error(error)
            return False

    def _start_configured_thermal(self) -> bool:
        if not self.hardware_runtime_requested or not self.thermal.config.address:
            return False
        if self.thermal.identity.state != "VERIFIED":
            return False
        if self.thermal.worker is not None:
            return False
        try:
            return self.thermal.start_verified_sensor(self.thermal_sensor_factory(self.thermal.config))
        except Exception as error:
            self.thermal.report_startup_error(error)
            return False

    def start_verified_configured_i2c_sensors(self) -> dict[str, bool]:
        """Commissioning hook after external evidence records sensor identity.

        It neither discovers nor probes devices and has no control authority.
        """
        return {"imu": self._start_configured_imu(), "thermal": self._start_configured_thermal()}

    def _select_configured_esp32(self) -> None:
        config = _configured_esp32()
        if config.device_path and config.baudrate is not None:
            # Configuration selects a boundary. It cannot open until external,
            # operator-recorded identity evidence is provided to that boundary.
            self.esp32_usb = self.esp32_usb_factory(config)

    def start_verified_esp32_transport(self) -> bool:
        """Start the bounded worker only after identity is already verified.

        This does not discover a port, establish identity, or change the
        Phase-1 zero-output state.
        """
        if self.esp32_usb is None or self.esp32_usb.identity.state != "VERIFIED":
            return False
        if self.esp32_transport is not None and self.esp32_transport.running:
            return False
        self.esp32_transport = BidirectionalSerialTransport(
            self.esp32_usb.open, self._receive_esp32_frame, SerialTransportConfig()
        )
        self.esp32_client = ESP32Client(self.esp32_transport)
        # Install the client before its reader thread can dispatch feedback.
        self.esp32_transport.start()
        return True

    def _receive_esp32_frame(self, frame: bytes) -> None:
        try:
            self.esp32_client.receive(frame)
        except Exception:
            # Corrupt feedback is intentionally transport diagnostics only.
            return

    def _start_configured_ld2450_raw_capture(self) -> None:
        config = LD2450RawCaptureConfig.from_environment()
        if not config.port:
            return
        adapter = self.ld2450_factory(config.port, config.baudrate, self.record_ld2450_raw)
        self.ld2450_capture = LD2450RawCaptureWorker(adapter, config.reconnect_s)
        self.ld2450_capture.start()
    def ingest_gnss_fix(self, fix: GnssFix, now_ns: int | None = None) -> bool:
        """Future reader callback boundary; it remains observational only."""
        return self.gnss.accept(fix, now_ns)
    def update_gnss_receiver_state(self, state: str, reason: str) -> None:
        """Future reader lifecycle callback; it does not affect control authority."""
        self.gnss.set_receiver_state(state, reason)  # type: ignore[arg-type]
    def vehicle_location(self, now_ns: int | None = None) -> dict:
        with self._location_lock:
            now_ns=now_ns or time.monotonic_ns()
            # API requests and WebSocket publication can overlap.  This applies
            # only to the local simulator's receipt timestamp; a real reader's
            # out-of-order fix remains rejected by GnssLocationService.
            if self.gnss.last and now_ns<=self.gnss.last.timestamp_ns: now_ns=self.gnss.last.timestamp_ns+1
            # Feed simulation only in explicitly selected simulation mode. In every
            # other mode, this method is read-only with respect to GNSS state so a
            # real reader callback remains the authoritative source.
            if self.settings.mode == "simulation":
                self._location_step+=1
                self.gnss.accept(self.gnss_simulator.fix(self._location_step, now_ns), now_ns)
            return self.gnss.response(now_ns)
    def tick(self,now_ns:int|None=None)->dict:
        now_ns=now_ns or time.monotonic_ns(); observations=self.radar.read_detections(now_ns)
        decision=self.pipeline.ingest(observations,now_ns) if observations else self.pipeline.decision(now_ns)
        event=self.pipeline.events[-1]; self.event_store.append(event)
        command=self.pipeline.command(decision,now_ns)
        self.recording_store.append_observation_tick(
            timestamp_ns=now_ns, source_mode=self.settings.mode.upper(), payload={
                "schema_version":1,
                "radar_detections":[item.model_dump(mode="json") for item in observations],
                "decision":decision.model_dump(mode="json"),
                "event":event.model_dump(mode="json"),
                "command":command.model_dump(mode="json"),
            },
        )
        submission=self.esp32_client.submit(command,now_ns); feedback=None
        if self.esp32_transport is None and submission.accepted and self.esp32_endpoint.last_response is not None:
            feedback=self.esp32_client.receive(self.esp32_endpoint.last_response).__dict__
        elif self.esp32_client.last_feedback is not None:
            feedback=self.esp32_client.last_feedback.__dict__
        runtime_mode=self.settings.mode.upper()
        transport_mode="CONFIGURED_SERIAL" if self.esp32_transport else "SIMULATION"
        return {"mode":runtime_mode,"traction":"DISABLED_PHASE_1","decision":decision.model_dump(),"command":command.model_dump(),"protocol":{"submission":submission.model_dump(),"feedback":feedback,"source_mode":runtime_mode,"transport_source_mode":transport_mode},"tracks":[t.model_dump() for t in self.pipeline.tracks.values()],"sensors":self.sensor_snapshot(now_ns),"vehicle_location":self.vehicle_location(now_ns),"events":[e.model_dump() for e in self.pipeline.events[-100:] ]}
    def persisted_events(self,limit:int=100)->list[dict]:
        return self.event_store.recent(limit)
    def start_recording(self, now_ns:int|None=None)->dict:
        now_ns=now_ns or time.monotonic_ns()
        max_records=int(os.getenv("TARK_RECORDING_MAX_RECORDS","10000"))
        return self.recording_store.start(timestamp_ns=now_ns,source_mode=self.settings.mode.upper(),configuration_hash=self.settings.configuration_hash,max_records=max_records)
    def stop_recording(self, now_ns:int|None=None)->dict:
        return self.recording_store.stop(timestamp_ns=now_ns or time.monotonic_ns())
    def recording_sessions(self)->list[dict]:
        return self.recording_store.list()
    def recording_session(self, session_id:str)->dict:
        return self.recording_store.get(session_id)
    def recording_records(self, session_id:str, limit:int=1_000)->list[dict]:
        return self.recording_store.records(session_id,limit=limit)
    def record_ld2450_raw(self, timestamp_ns:int, raw:bytes)->bool:
        """Optional real-adapter sink; raw bytes remain undecoded until verified."""
        return self.recording_store.append_raw_frame(timestamp_ns=timestamp_ns,source_mode="REAL_LD2450_RAW",raw=raw,metadata={"decoder":"NOT_VERIFIED"})
    def close(self)->None:
        if self.gnss_reader:self.gnss_reader.close()
        if self.ld2450_capture:self.ld2450_capture.close()
        if self.esp32_transport:self.esp32_transport.close()
        if self.esp32_usb:self.esp32_usb.close()
        self.camera.stop(); self.thermal.stop(); self.imu.stop()
        self.event_store.close(); self.recording_store.close()
    def sensor_snapshot(self,now_ns:int)->list[dict]:
        radar=self.pipeline.health(now_ns).model_dump(); radar["device_id"]=radar.pop("sensor_id"); radar["source_mode"]="SIMULATION"
        raw_capture=None
        if self.ld2450_capture:
            diagnostic=self.ld2450_capture.diagnostics()
            # Raw bytes and normalized simulator detections are different
            # sources. Never relabel simulated tracks as a real radar result.
            raw_capture={"device_id":"ld2450_raw_capture","source_mode":"REAL_LD2450_RAW","state":diagnostic["state"],"reason":diagnostic["reason"],"timestamp_ns":diagnostic["last_timestamp_ns"],"age_ms":None,"quality":None}
        if self.esp32_transport:
            esp32={"device_id":"esp32","source_mode":"CONFIGURED_SERIAL","state":"ONLINE" if self.esp32_transport.running else "CONNECTING","timestamp_ns":now_ns,"age_ms":0.0,"quality":None,"reason":"PHASE_1 OUTPUTS DISABLED"}
        elif self.esp32_usb:
            esp32={"device_id":"esp32","source_mode":"NOT_CONNECTED_PHASE_2","state":"NOT_CONNECTED","timestamp_ns":None,"age_ms":None,"quality":None,"reason":"ESP32 IDENTITY EVIDENCE REQUIRED BEFORE SERIAL OPEN"}
        else: esp32=self.esp32.status(now_ns).__dict__
        result=[radar,esp32,self.motor.status(now_ns).__dict__,self.camera.health(now_ns).__dict__,self.thermal.health(now_ns).__dict__,self.imu.health(now_ns).__dict__,{"device_id":"encoders","source_mode":"SIMULATION","state":"DISABLED_PHASE_1","timestamp_ns":now_ns,"age_ms":0.0,"quality":None,"reason":"SOFTWARE_INTERFACE_READY_WHEEL_RESPONSE_NOT_GROUND_SPEED"}]
        if raw_capture: result.append(raw_capture)
        return result
