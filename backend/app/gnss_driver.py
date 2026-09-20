"""Threaded, read-only GNSS serial boundary. Optional pyserial is required only for real USB I/O."""
from __future__ import annotations
import threading, time
from pathlib import Path
from collections import deque
from dataclasses import dataclass
from typing import Callable, Protocol
from app.gnss import GnssFix, distance_m, parse_nmea

class SerialPort(Protocol):
    def read(self, size:int=1)->bytes: ...
    def close(self)->None: ...

@dataclass
class ReaderDiagnostics:
    state:str="NO_RECEIVER"; transport_connected:bool=False; identity:str="UNVERIFIED"; raw_sentences:int=0; rmc_count:int=0; gga_count:int=0; gsa_count:int=0; checksum_failures:int=0; reconnect_count:int=0; last_byte_ns:int|None=None; last_valid_ns:int|None=None; parser_latency_ms:float|None=None; reason:str="NOT STARTED"

def discover_candidates(path_override:str="")->list[dict]:
    if path_override:return [{"path":path_override,"identity":"UNVERIFIED","selected":True}]
    try:
        from serial.tools import list_ports
        return [{"path":p.device,"identity":"UNVERIFIED","description":p.description,"selected":False} for p in list_ports.comports()]
    except ImportError:return []

class NmeaAggregator:
    """Combines compatible RMC/GGA fields; never fabricates missing fields."""
    def __init__(self, window_ns:int=2_000_000_000):self.window_ns=window_ns;self.rmc:GnssFix|None=None;self.gga:GnssFix|None=None;self.gsa:GnssFix|None=None
    def add(self, fix:GnssFix)->GnssFix:
        if fix.quality.startswith("GSA_MODE_"):
            self.gsa=fix
            return fix
        is_rmc=fix.speed_mps is not None and fix.altitude_m is None
        if is_rmc:self.rmc=fix
        else:self.gga=fix
        other=self.gga if is_rmc else self.rmc
        dimension=self.gsa if self.gsa and abs(fix.timestamp_ns-self.gsa.timestamp_ns)<=self.window_ns else None
        if other and abs(fix.timestamp_ns-other.timestamp_ns)<=self.window_ns and fix.source==other.source and distance_m(fix,other)<=30:
            return GnssFix(fix.vehicle_id,fix.timestamp_ns,fix.source,fix.latitude_deg,fix.longitude_deg,altitude_m=self.gga.altitude_m if self.gga else None,speed_mps=self.rmc.speed_mps if self.rmc else None,heading_deg=self.rmc.heading_deg if self.rmc else None,horizontal_accuracy_m=fix.horizontal_accuracy_m,vertical_accuracy_m=fix.vertical_accuracy_m,fix_type=dimension.fix_type if dimension else (self.gga.fix_type if self.gga else fix.fix_type),satellites=self.gga.satellites if self.gga else fix.satellites,quality=fix.quality,status=dimension.status if dimension else fix.status)
        if dimension:
            return GnssFix(fix.vehicle_id,fix.timestamp_ns,fix.source,fix.latitude_deg,fix.longitude_deg,altitude_m=fix.altitude_m,speed_mps=fix.speed_mps,heading_deg=fix.heading_deg,horizontal_accuracy_m=fix.horizontal_accuracy_m,vertical_accuracy_m=fix.vertical_accuracy_m,fix_type=dimension.fix_type,satellites=fix.satellites,quality=fix.quality,status=dimension.status,measurement_time_utc=fix.measurement_time_utc,received_monotonic_ns=fix.received_monotonic_ns)
        return fix

class GnssReader:
    def __init__(self, opener:Callable[[],SerialPort], on_fix:Callable[[GnssFix],None], reconnect_s:float=.5, max_line_bytes:int=1024, raw_limit:int=200, raw_log_path:str|None=None, on_state:Callable[[str,str],None]|None=None):
        self.opener,self.on_fix,self.reconnect_s,self.max_line_bytes=opener,on_fix,max(.1,reconnect_s),max(64,max_line_bytes);self.on_state=on_state;self.diag=ReaderDiagnostics();self.raw:deque[tuple[int,bytes]]=deque(maxlen=max(1,raw_limit));self.raw_log_path=Path(raw_log_path) if raw_log_path else None;self._stop=threading.Event();self._thread:threading.Thread|None=None;self._port:SerialPort|None=None;self._buffer=bytearray();self._aggregate=NmeaAggregator()
    def start(self)->bool:
        if self._thread and self._thread.is_alive():return False
        self._stop.clear();self._thread=threading.Thread(target=self._run,name="tark-gnss-reader",daemon=True);self._thread.start();return True
    def close(self)->None:
        self._stop.set()
        if self._port:
            try:self._port.close()
            except OSError:pass
        if self._thread:self._thread.join(timeout=2)
        self.diag.state="NO_RECEIVER";self.diag.transport_connected=False
    def feed(self,data:bytes,now_ns:int|None=None)->None:
        now=now_ns or time.monotonic_ns();self.diag.last_byte_ns=now;self._buffer.extend(data)
        if len(self._buffer)>self.max_line_bytes and b"\n" not in self._buffer:self._buffer.clear();self.diag.reason="OVERSIZED GNSS LINE DROPPED";return
        while b"\n" in self._buffer:
            line,_,rest=self._buffer.partition(b"\n");self._buffer=bytearray(rest);line=line.rstrip(b"\r");self.raw.append((now,line));self._persist_raw(now,line);self.diag.raw_sentences+=1;started=time.monotonic_ns();fix=parse_nmea(line,now)
            self.diag.parser_latency_ms=(time.monotonic_ns()-started)/1e6
            if not fix:self.diag.checksum_failures+=1;continue
            if b"RMC" in line:self.diag.rmc_count+=1
            if b"GGA" in line:self.diag.gga_count+=1
            if b"GSA" in line:self.diag.gsa_count+=1
            normalized=self._aggregate.add(fix);self.on_fix(normalized);self.diag.last_valid_ns=now;self.diag.state=normalized.status;self.diag.reason="VALID NMEA STREAM"
    def _run(self)->None:
        while not self._stop.is_set():
            try:
                self.diag.state="SEARCHING";self.on_state and self.on_state("SEARCHING","OPENING CONFIGURED GNSS DEVICE");self._port=self.opener();self.diag.transport_connected=True;self.diag.identity="UNVERIFIED";self.diag.state="NO_FIX";self.diag.reason="SERIAL CONNECTED; IDENTITY UNVERIFIED; AWAITING FIX";self.on_state and self.on_state("NO_FIX",self.diag.reason)
                while not self._stop.is_set():
                    data=self._port.read(256)
                    if data:self.feed(data)
            except Exception as error:
                self.diag.state="ERROR";self.diag.reason=f"SERIAL ERROR: {type(error).__name__}";self.on_state and self.on_state("ERROR",self.diag.reason);self.diag.reconnect_count+=1
                if self._stop.wait(self.reconnect_s):break
            finally:
                if self._port:
                    try:self._port.close()
                    except Exception:pass
                    self._port=None
                self.diag.transport_connected=False
    def _persist_raw(self, timestamp_ns:int, line:bytes)->None:
        if not self.raw_log_path:return
        try:
            self.raw_log_path.parent.mkdir(parents=True,exist_ok=True)
            with self.raw_log_path.open("ab") as output: output.write(f"{timestamp_ns} ".encode()+line+b"\n")
        except OSError:self.diag.reason="RAW LOG WRITE FAILED"

def pyserial_opener(path:str,baud:int,timeout_s:float)->Callable[[],SerialPort]:
    def open_port()->SerialPort:
        import serial
        return serial.Serial(path,baudrate=baud,timeout=timeout_s)
    return open_port
