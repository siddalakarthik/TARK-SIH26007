"""Identity-gated Pi-to-ESP32 USB transport.

Discovery is read-only. Opening a serial port is intentionally impossible
until an operator records evidence for the specific purchased board and has
provided the selected path and serial settings. This module does not infer an
ESP32-S3 identity from a COM port name, VID, PID, or a successful open.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Callable, Protocol

from app.sensor_identity import DeviceIdentity


class SerialPort(Protocol):
    def read(self, size: int) -> bytes: ...
    def write(self, data: bytes) -> int | None: ...
    def close(self) -> None: ...


@dataclass(frozen=True)
class Esp32UsbConfig:
    device_path: str = ""
    baudrate: int | None = None
    timeout_s: float = 0.5


@dataclass(frozen=True)
class Esp32UsbCandidate:
    device_path: str
    manufacturer: str | None
    product: str | None
    serial_number: str | None
    vendor_id: str | None
    product_id: str | None

    def identity(self) -> DeviceIdentity:
        return DeviceIdentity("USB_SERIAL", self.device_path, self.manufacturer, self.product, serial_number=self.serial_number, vendor_id=self.vendor_id, product_id=self.product_id)


class IdentityGatedESP32UsbTransport:
    """A transport for a later reviewed physical connection, never auto-enabled."""
    def __init__(self, config: Esp32UsbConfig, opener: Callable[..., SerialPort] | None = None):
        self.config=config
        self._opener=opener
        self._serial: SerialPort | None=None
        self._lock=Lock()
        self.identity=DeviceIdentity("USB_SERIAL", config.device_path or "UNSELECTED")

    @staticmethod
    def discover(list_ports: Callable[[], object] | None = None) -> list[Esp32UsbCandidate]:
        if list_ports is None:
            try:
                from serial.tools import list_ports as pyserial_list_ports
            except ImportError:
                return []
            list_ports=pyserial_list_ports.comports
        return [Esp32UsbCandidate(str(port.device), getattr(port,"manufacturer",None), getattr(port,"product",None), getattr(port,"serial_number",None), f"{port.vid:04X}" if getattr(port,"vid",None) is not None else None, f"{port.pid:04X}" if getattr(port,"pid",None) is not None else None) for port in list_ports()]

    def record_verified_identity(self, candidate: Esp32UsbCandidate, evidence_source: str) -> None:
        if candidate.device_path != self.config.device_path:
            raise ValueError("candidate path does not match selected ESP32 device path")
        self.identity=candidate.identity().verified(evidence_source)

    def open(self) -> "IdentityGatedESP32UsbTransport":
        if self.identity.state != "VERIFIED": raise RuntimeError("ESP32 USB identity is not verified")
        if not self.config.device_path or self.config.baudrate is None: raise RuntimeError("ESP32 USB path and reviewed baudrate are required")
        with self._lock:
            if self._serial is not None: return self
            if self._opener is None:
                try:
                    import serial
                except ImportError as error:
                    raise RuntimeError("pyserial is required for a verified ESP32 USB connection") from error
                self._opener=serial.Serial
            self._serial=self._opener(self.config.device_path, self.config.baudrate, timeout=self.config.timeout_s)
        return self

    def read(self, size: int) -> bytes:
        if size < 1: raise ValueError("serial read size must be positive")
        with self._lock:
            if self._serial is None: raise RuntimeError("ESP32 USB transport is not open")
            return self._serial.read(size)

    def write(self, frame: bytes) -> None:
        with self._lock:
            if self._serial is None: raise RuntimeError("ESP32 USB transport is not open")
            self._serial.write(frame)

    def close(self) -> None:
        with self._lock:
            if self._serial is not None: self._serial.close(); self._serial=None
