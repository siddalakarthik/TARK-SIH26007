"""Threaded, bounded serial byte transport for the local Pi↔ESP32 link.

It is deliberately independent of FastAPI and the browser. Real opening still
belongs behind ``IdentityGatedESP32UsbTransport`` after identity evidence.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from queue import Empty, Full, Queue
from threading import Event, Lock, Thread
from time import monotonic, sleep
from typing import Callable, Protocol

from .protocol import FrameAccumulator, MAX_FRAME, ProtocolError, TransportCounters, decode_frame


class DuplexSerial(Protocol):
    def read(self,size:int)->bytes: ...
    def write(self,data:bytes)->int|None: ...
    def close(self)->None: ...


@dataclass(frozen=True)
class SerialTransportConfig:
    read_size:int=256; rx_queue_size:int=64; tx_queue_size:int=64; reconnect_delay_s:float=.5
    def __post_init__(self)->None:
        if not 1<=self.read_size<=MAX_FRAME or self.rx_queue_size<1 or self.tx_queue_size<1 or self.reconnect_delay_s<0:raise ValueError("unsafe serial transport configuration")


@dataclass
class SerialTransportDiagnostics:
    protocol:TransportCounters=field(default_factory=TransportCounters); tx_enqueued:int=0; tx_dropped:int=0; tx_written:int=0; io_failures:int=0; starts:int=0; stops:int=0


class BidirectionalSerialTransport:
    """Exactly one reader and one writer; queues and buffers are bounded.

    Callbacks receive complete framed packets in the reader thread and should
    perform only fast handoff work. A malformed input frame is counted and the
    next delimiter boundary is still processed.
    """
    def __init__(self,opener:Callable[[],DuplexSerial],on_frame:Callable[[bytes],None],config:SerialTransportConfig=SerialTransportConfig()):
        self._opener=opener;self._on_frame=on_frame;self.config=config;self.diagnostics=SerialTransportDiagnostics();self._frames=FrameAccumulator(counters=self.diagnostics.protocol)
        self._tx:Queue[bytes]=Queue(maxsize=config.tx_queue_size);self._stop=Event();self._thread:Thread|None=None;self._write_lock=Lock();self._serial:DuplexSerial|None=None
    @property
    def running(self)->bool:return self._thread is not None and self._thread.is_alive()
    def start(self)->None:
        if self.running:raise RuntimeError("serial transport already started")
        self._stop.clear();self.diagnostics.starts+=1;self._thread=Thread(target=self._run,name="tark-esp32-serial",daemon=True);self._thread.start()
    def write(self,frame:bytes)->None:
        if not frame.startswith(b"\0") or not frame.endswith(b"\0") or len(frame)>MAX_FRAME:raise ValueError("only bounded complete protocol frames may be queued")
        try:self._tx.put_nowait(frame);self.diagnostics.tx_enqueued+=1
        except Full:self.diagnostics.tx_dropped+=1;raise RuntimeError("ESP32 transmit queue full")
    def close(self,timeout_s:float=2)->None:
        self._stop.set();thread=self._thread
        if thread:thread.join(timeout_s)
        self._thread=None;self._close_serial();self.diagnostics.stops+=1
    def _close_serial(self)->None:
        with self._write_lock:
            serial,self._serial=self._serial,None
            if serial:
                try:serial.close()
                except Exception:self.diagnostics.io_failures+=1
    def _connect(self)->bool:
        try:self._serial=self._opener();return True
        except Exception:self.diagnostics.io_failures+=1;self.diagnostics.protocol.reconnect_count+=1;return False
    def _run(self)->None:
        while not self._stop.is_set():
            if self._serial is None:
                if not self._connect():self._stop.wait(self.config.reconnect_delay_s);continue
            serial=self._serial
            try:
                # A nonblocking/timeout-bound read keeps TX and shutdown responsive.
                chunk=serial.read(self.config.read_size)
                for frame in self._frames.feed(chunk):
                    self.diagnostics.protocol.frames_received+=1
                    try:
                        decode_frame(frame) # transport rejects corruption before callback handoff
                        self._on_frame(frame);self.diagnostics.protocol.frames_valid+=1
                    except ProtocolError as error:self.diagnostics.protocol.reject(error)
                    except Exception:self.diagnostics.protocol.frames_invalid+=1;self.diagnostics.protocol.header_failures+=1
                try:frame=self._tx.get_nowait()
                except Empty:continue
                with self._write_lock:
                    if self._serial is not serial:continue
                    serial.write(frame);self.diagnostics.tx_written+=1
            except Exception:
                self.diagnostics.io_failures+=1;self._close_serial()
                if not self._stop.is_set():self._stop.wait(self.config.reconnect_delay_s)
