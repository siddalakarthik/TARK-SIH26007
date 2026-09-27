"""Bounded byte transport; connection generations never carry queued authority."""
from __future__ import annotations
from dataclasses import dataclass, field
from queue import Empty, Full, Queue
from threading import Event, Lock, Thread
from time import monotonic_ns
from typing import Callable, Protocol
from .protocol import COMMAND, FrameAccumulator, MAX_FRAME, MAX_COMMAND_LIFETIME_NS, ProtocolError, TransportCounters, decode_frame, uint

class DuplexSerial(Protocol):
    def read(self,size:int)->bytes: ...
    def write(self,data:bytes)->int: ...
    def close(self)->None: ...

@dataclass(frozen=True)
class SerialTransportConfig:
    read_size:int=256;rx_queue_size:int=64;tx_queue_size:int=64;reconnect_delay_s:float=.5
    def __post_init__(self):
        if not 1<=self.read_size<=MAX_FRAME or not 1<=self.rx_queue_size<=64 or not 1<=self.tx_queue_size<=64 or not 0<=self.reconnect_delay_s<=60:
            raise ValueError('unsafe serial transport configuration')

@dataclass
class SerialTransportDiagnostics:
    protocol:TransportCounters=field(default_factory=TransportCounters)
    tx_enqueued:int=0;tx_dropped:int=0;tx_written:int=0;io_failures:int=0;starts:int=0;stops:int=0

class BidirectionalSerialTransport:
    def __init__(self,opener:Callable[[],DuplexSerial],on_frame:Callable[[bytes],None],config:SerialTransportConfig=SerialTransportConfig(),*,on_reset:Callable[[],None]=lambda:None,clock=monotonic_ns):
        self._opener=opener;self._on_frame=on_frame;self._on_reset=on_reset;self.config=config;self.clock=clock
        self.diagnostics=SerialTransportDiagnostics();self._frames=FrameAccumulator(counters=self.diagnostics.protocol)
        self._tx:Queue[tuple[bytes,int,int]]=Queue(maxsize=config.tx_queue_size)
        self._stop=Event();self._thread:Thread|None=None;self._state_lock=Lock();self._serial=None;self._generation=0
    @property
    def running(self):return self._thread is not None and self._thread.is_alive()
    @property
    def connected(self):
        with self._state_lock:return self._serial is not None
    def start(self):
        if self.running:raise RuntimeError('serial transport already started')
        self._stop.clear();self.diagnostics.starts+=1;self._thread=Thread(target=self._run,name='tark-esp32-serial',daemon=True);self._thread.start()
    def write(self,frame:bytes):
        message,envelope=decode_frame(frame);now=self.clock()
        deadline=now+MAX_COMMAND_LIFETIME_NS
        if message==COMMAND:
            until=envelope['payload'].get('valid_until_ns')
            if not uint(until) or until<=now:raise ProtocolError('COMMAND_EXPIRED')
            deadline=min(deadline,until)
        with self._state_lock:
            if self._serial is None or self._stop.is_set():raise RuntimeError('serial transport not connected')
            try:self._tx.put_nowait((frame,deadline,self._generation));self.diagnostics.tx_enqueued+=1
            except Full:self.diagnostics.tx_dropped+=1;raise RuntimeError('ESP32 transmit queue full')
    def _flush(self):
        while True:
            try:self._tx.get_nowait();self.diagnostics.tx_dropped+=1
            except Empty:break
        self._frames.reset()
    def _close_serial(self):
        with self._state_lock:
            serial,self._serial=self._serial,None;self._generation+=1;self._flush()
        # Never acquire client callback locks while holding transport locks.
        try:self._on_reset()
        except Exception:self.diagnostics.io_failures+=1
        if serial is not None:
            try:serial.close()
            except Exception:self.diagnostics.io_failures+=1
    def close(self,timeout_s:float=2):
        self._stop.set();self._close_serial();thread=self._thread
        if thread:thread.join(timeout_s)
        if thread and thread.is_alive():raise RuntimeError('ESP32 worker did not terminate within shutdown bound')
        self._thread=None;self.diagnostics.stops+=1
    def _connect(self)->bool:
        serial=None
        try:
            serial=self._opener()
            if serial is None:raise RuntimeError('opener returned no transport')
            self._on_reset()
            with self._state_lock:
                if self._stop.is_set():serial.close();return False
                self._flush();self._generation+=1;self._serial=serial
            return True
        except Exception:
            if serial is not None:
                try:serial.close()
                except Exception:self.diagnostics.io_failures+=1
            self.diagnostics.io_failures+=1;self.diagnostics.protocol.reconnect_count+=1;return False
    def _write_one(self,serial):
        try:frame,deadline,generation=self._tx.get_nowait()
        except Empty:return False
        if deadline<=self.clock() or generation!=self._generation:
            self.diagnostics.tx_dropped+=1;return True
        offset=0
        while offset<len(frame):
            if self._stop.is_set() or deadline<=self.clock() or self._serial is not serial or generation!=self._generation:
                raise RuntimeError('frame expired/interrupted during write')
            count=serial.write(frame[offset:])
            if type(count) is not int or not 0<count<=len(frame)-offset:raise RuntimeError('serial made no valid write progress')
            offset+=count
        self.diagnostics.tx_written+=1;return True
    def _run(self):
        while not self._stop.is_set():
            if self._serial is None and not self._connect():self._stop.wait(self.config.reconnect_delay_s);continue
            serial=self._serial
            try:
                chunk=serial.read(self.config.read_size)
                if self._stop.is_set():break
                for frame in self._frames.feed(chunk):
                    self.diagnostics.protocol.frames_received+=1
                    try:
                        decode_frame(frame);self._on_frame(frame);self.diagnostics.protocol.frames_valid+=1
                    except ProtocolError as error:self.diagnostics.protocol.reject(error)
                    except Exception:self.diagnostics.protocol.frames_invalid+=1
                written=self._write_one(serial)
                if not chunk and not written:self._stop.wait(.001)
            except Exception:
                self.diagnostics.io_failures+=1;self._close_serial()
                if not self._stop.is_set():self._stop.wait(self.config.reconnect_delay_s)
