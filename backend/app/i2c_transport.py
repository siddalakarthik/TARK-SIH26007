"""Shared read-only Linux I²C transport; SMBus is optional for simulation installs."""
from __future__ import annotations
import threading
import time
from dataclasses import dataclass
from typing import Protocol

class I2cBus(Protocol):
    def read_byte_data(self,address:int,register:int)->int: ...
    def read_i2c_block_data(self,address:int,register:int,length:int)->list[int]: ...
    def write_byte_data(self,address:int,register:int,value:int)->None: ...
    def close(self)->None: ...

@dataclass(frozen=True)
class I2cIdentity:
    bus:int; address:int|None; manufacturer:str|None=None; product:str|None=None; chip_id:str|None=None; revision:str|None=None; serial_number:str|None=None; identity_state:str="UNVERIFIED"; verification_source:str="NONE"

class I2cTransport:
    """One selected bus/address. An ACK alone is deliberately not verified identity."""
    def __init__(self,bus_number:int,address:int|None,bus_factory=None,retries:int=2):
        self.bus_number,self.address,self.bus_factory,self.retries=bus_number,address,bus_factory,max(0,retries);self._bus:I2cBus|None=None;self._lock=threading.Lock();self.errors=0
    def open(self)->bool:
        if self._bus is not None:return True
        if self.address is None:return False
        try:
            if self.bus_factory:self._bus=self.bus_factory(self.bus_number)
            else:
                from smbus2 import SMBus
                self._bus=SMBus(self.bus_number)
            return True
        except Exception:self.errors+=1;self._bus=None;return False
    def close(self)->None:
        with self._lock:
            if self._bus:
                try:self._bus.close()
                except Exception:pass
            self._bus=None
    def _attempt(self,operation):
        if not self.open():raise OSError("I2C transport unavailable")
        for attempt in range(self.retries+1):
            try:return operation(self._bus)
            except Exception:
                self.errors+=1
                if attempt==self.retries:self.close();raise
    def read_byte(self,register:int)->int:return self._attempt(lambda bus:bus.read_byte_data(self.address,register))
    def read_block(self,register:int,length:int)->bytes:return bytes(self._attempt(lambda bus:bus.read_i2c_block_data(self.address,register,length)))
    def write_byte(self,register:int,value:int)->None:self._attempt(lambda bus:bus.write_byte_data(self.address,register,value))
    def candidate_identity(self)->I2cIdentity:return I2cIdentity(self.bus_number,self.address,identity_state="UNVERIFIED",verification_source="CONFIGURATION_ONLY")

class I2cSensorWorker:
    """Single bounded reader for an already-verified device. Never starts itself."""
    def __init__(self,read_once, on_value, interval_s:float, reconnect_s:float=.5):
        self.read_once,self.on_value=read_once,on_value;self.interval_s=max(.01,interval_s);self.reconnect_s=max(.1,reconnect_s);self.stop_event=threading.Event();self.thread:threading.Thread|None=None;self.read_count=0;self.valid_count=0;self.error_count=0;self.reconnect_count=0;self.last_error:str|None=None
    def start(self)->bool:
        if self.thread is not None:return False
        self.stop_event.clear();self.thread=threading.Thread(target=self._run,name="tark-i2c-sensor",daemon=True);self.thread.start();return True
    def stop(self)->None:
        self.stop_event.set()
        if self.thread:self.thread.join(timeout=2)
        self.thread=None
    def _run(self)->None:
        while not self.stop_event.is_set():
            try:
                value=self.read_once();self.read_count+=1;self.on_value(value);self.valid_count+=1
                if self.stop_event.wait(self.interval_s):return
            except Exception as error:
                self.error_count+=1;self.reconnect_count+=1;self.last_error=type(error).__name__
                if self.stop_event.wait(self.reconnect_s):return
