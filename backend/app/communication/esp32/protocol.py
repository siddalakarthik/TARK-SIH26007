"""The sole TARK Pi↔ESP32 Protocol V1 implementation.

The browser never imports or calls this module. Its command input is the
locally-created BoundedCommand; malformed frames are rejected before they can
become a simulator command. See docs/ESP32_PROTOCOL_V1.md.
"""
from __future__ import annotations
import struct
from collections import deque
from dataclasses import dataclass
from math import isfinite
from typing import Any, Protocol
import cbor2
from app.domain.models import BoundedCommand, CommandResult

MAGIC=0x544B; VERSION=1
COMMAND=1; ACK=2; NACK=3; HEARTBEAT=4; STATUS=5
MESSAGE_NAMES={COMMAND:"COMMAND",ACK:"ACK",NACK:"NACK",HEARTBEAT:"HEARTBEAT",STATUS:"STATUS"}
MAX_SEQUENCE=0xFFFFFFFF; MAX_PAYLOAD=512; MAX_FRAME=640; HEADER=struct.Struct("!HBBIQQ")
REJECTION_REASONS=frozenset({"DUPLICATE_SEQUENCE","OLD_SEQUENCE","OUT_OF_ORDER_SEQUENCE","COMMAND_EXPIRED","HEARTBEAT_TIMEOUT","CONFIGURATION_MISMATCH","INVALID_PAYLOAD","INVALID_VERSION","INVALID_CRC","INVALID_LENGTH","NOT_ENABLED","INTERNAL_FAULT","UNEXPECTED_MESSAGE"})

class ProtocolError(ValueError):
    """A rejected byte-stream object, never a recoverable command."""
    def __init__(self,reason:str):super().__init__(reason);self.reason=reason
class FrameTransport(Protocol):
    def write(self,frame:bytes)->None: ...
@dataclass
class TransportCounters:
    frames_received:int=0;frames_valid:int=0;frames_invalid:int=0;crc_failures:int=0;cobs_failures:int=0;header_failures:int=0;length_failures:int=0;unknown_message_count:int=0;bytes_received:int=0;reconnect_count:int=0
    def reject(self,error:ProtocolError)->None:
        self.frames_invalid+=1
        if error.reason=="CRC32C mismatch":self.crc_failures+=1
        elif error.reason=="invalid COBS frame":self.cobs_failures+=1
        elif error.reason in {"frame too short","payload too large","header validation failed","frame too large"}:self.length_failures+=1
        elif error.reason in {"unknown message type","unsupported protocol version"}:self.unknown_message_count+=1
        else:self.header_failures+=1
@dataclass(frozen=True)
class ESP32Feedback:
    """Transport telemetry; ACK does not prove a physical output or movement."""
    message_type:int;sequence:int;timestamp_ns:int;accepted:bool;reason:str;output_state:str;payload:dict[str,Any];correlation:str="UNSOLICITED"

def crc32c(data:bytes)->int:
    crc=0xFFFFFFFF
    for byte in data:
        crc^=byte
        for _ in range(8):crc=(crc>>1)^0x82F63B78 if crc&1 else crc>>1
    return (~crc)&0xFFFFFFFF
def cobs_encode(data:bytes)->bytes:
    out=bytearray();code_index=0;out.append(0);code=1
    for b in data:
        if b==0:out[code_index]=code;code_index=len(out);out.append(0);code=1
        else:
            out.append(b);code+=1
            if code==0xFF:out[code_index]=code;code_index=len(out);out.append(0);code=1
    out[code_index]=code;return bytes(out)
def cobs_decode(data:bytes)->bytes:
    out=bytearray();i=0
    while i<len(data):
        code=data[i]
        if code==0 or i+code>len(data)+1:raise ProtocolError("invalid COBS frame")
        i+=1;out.extend(data[i:i+code-1]);i+=code-1
        if code<0xFF and i<len(data):out.append(0)
    return bytes(out)
def encode_message(message_type:int,sequence:int,timestamp_ns:int,payload_data:dict[str,Any])->bytes:
    if message_type not in MESSAGE_NAMES:raise ValueError("unknown message type")
    if not 0<=sequence<=MAX_SEQUENCE or timestamp_ns<0:raise ValueError("invalid protocol sequence or timestamp")
    payload=cbor2.dumps(payload_data,canonical=True)
    if len(payload)>MAX_PAYLOAD:raise ValueError("payload too large")
    body=HEADER.pack(MAGIC,VERSION,message_type,len(payload),sequence,timestamp_ns)+payload
    frame=b"\x00"+cobs_encode(body+struct.pack("!I",crc32c(body)))+b"\x00"
    if len(frame)>MAX_FRAME:raise ValueError("frame too large")
    return frame
def encode_command(command:BoundedCommand)->bytes:return encode_message(COMMAND,command.sequence,command.timestamp_ns,command.model_dump(mode="json"))
def encode_heartbeat(sequence:int,timestamp_ns:int,configuration_hash:str)->bytes:return encode_message(HEARTBEAT,sequence,timestamp_ns,{"configuration_hash":configuration_hash,"protocol_version":VERSION})
def decode_frame(frame:bytes)->tuple[int,dict[str,Any]]:
    if len(frame)>MAX_FRAME:raise ProtocolError("frame too large")
    if not frame.startswith(b"\x00") or not frame.endswith(b"\x00"):raise ProtocolError("missing delimiter")
    decoded=cobs_decode(frame[1:-1])
    if len(decoded)<HEADER.size+4:raise ProtocolError("frame too short")
    body,supplied=decoded[:-4],struct.unpack("!I",decoded[-4:])[0]
    if crc32c(body)!=supplied:raise ProtocolError("CRC32C mismatch")
    magic,version,message,length,sequence,timestamp=HEADER.unpack(body[:HEADER.size])
    if magic!=MAGIC:raise ProtocolError("bad magic")
    if version!=VERSION:raise ProtocolError("unsupported protocol version")
    if message not in MESSAGE_NAMES:raise ProtocolError("unknown message type")
    if length>MAX_PAYLOAD:raise ProtocolError("payload too large")
    if length!=len(body)-HEADER.size:raise ProtocolError("header validation failed")
    try:payload=cbor2.loads(body[HEADER.size:])
    except Exception as error:raise ProtocolError("invalid CBOR payload") from error
    if not isinstance(payload,dict):raise ProtocolError("payload must be a CBOR map")
    return message,{"sequence":sequence,"timestamp_ns":timestamp,"payload":payload}
class FrameAccumulator:
    """Bounded delimiter-based recovery for an arbitrary serial byte stream."""
    def __init__(self,max_frame:int=MAX_FRAME,counters:TransportCounters|None=None):self.max_frame=max_frame;self.counters=counters or TransportCounters();self._inside=False;self._buffer=bytearray()
    def feed(self,data:bytes)->list[bytes]:
        self.counters.bytes_received+=len(data);frames=[]
        for byte in data:
            if byte==0:
                if self._inside and self._buffer:frames.append(b"\x00"+bytes(self._buffer)+b"\x00");self._buffer.clear();self._inside=True
                else:self._inside=True;self._buffer.clear()
                continue
            if not self._inside:continue
            if len(self._buffer)>=self.max_frame-2:self.counters.frames_received+=1;self.counters.frames_invalid+=1;self.counters.length_failures+=1;self._inside=False;self._buffer.clear();continue
            self._buffer.append(byte)
        return frames
    def decode(self,data:bytes)->list[tuple[int,dict[str,Any]]]:
        values=[]
        for frame in self.feed(data):
            self.counters.frames_received+=1
            try:values.append(decode_frame(frame));self.counters.frames_valid+=1
            except ProtocolError as error:self.counters.reject(error)
        return values
def validate_command_payload(payload:dict[str,Any],sequence:int,timestamp_ns:int,now_ns:int,configuration_hash:str)->str|None:
    required={"protocol_version","sequence","timestamp_ns","valid_until_ns","state","permitted_speed_mps","left_command","right_command","heartbeat","reason_code","configuration_hash"}
    if not required.issubset(payload) or payload.get("sequence")!=sequence or payload.get("timestamp_ns")!=timestamp_ns:return "INVALID_PAYLOAD"
    if payload.get("protocol_version")!=VERSION or not isinstance(payload.get("configuration_hash"),str):return "INVALID_VERSION"
    if payload["configuration_hash"]!=configuration_hash:return "CONFIGURATION_MISMATCH"
    if not isinstance(payload["valid_until_ns"],int) or payload["valid_until_ns"]<=now_ns:return "COMMAND_EXPIRED"
    if payload.get("state") not in {"NORMAL","WARN","RESTRICT","UNKNOWN","STOP"}:return "INVALID_PAYLOAD"
    if not isinstance(payload.get("reason_code"),str) or not isinstance(payload.get("heartbeat"),int):return "INVALID_PAYLOAD"
    for name in ("permitted_speed_mps","left_command","right_command"):
        value=payload.get(name)
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not isfinite(value):return "INVALID_PAYLOAD"
    if payload["permitted_speed_mps"]<0 or abs(payload["left_command"])>1 or abs(payload["right_command"])>1:return "INVALID_PAYLOAD"
    return None
class ESP32Client:
    """Pi-side command correlation boundary. It owns neither motor authority nor USB identity."""
    def __init__(self,transport:FrameTransport|None=None,response_timeout_ns:int=500_000_000):self.transport=transport;self.last_sequence=-1;self.response_timeout_ns=response_timeout_ns;self.pending:dict[int,int]={};self.seen_feedback:deque[int]=deque(maxlen=256);self.last_feedback:ESP32Feedback|None=None
    def submit(self,command:BoundedCommand,now_ns:int)->CommandResult:
        if command.valid_until_ns<=now_ns:return CommandResult(accepted=False,reason="COMMAND_EXPIRED",sequence=command.sequence)
        if command.sequence>MAX_SEQUENCE:return CommandResult(accepted=False,reason="COMMAND_SEQUENCE_OUT_OF_RANGE",sequence=command.sequence)
        if command.sequence<=self.last_sequence:return CommandResult(accepted=False,reason="COMMAND_OUT_OF_ORDER",sequence=command.sequence)
        values=(command.permitted_speed_mps,command.left_command,command.right_command)
        if not all(isfinite(value) for value in values) or command.permitted_speed_mps<0 or abs(command.left_command)>1 or abs(command.right_command)>1:return CommandResult(accepted=False,reason="COMMAND_OUT_OF_RANGE",sequence=command.sequence)
        self.last_sequence=command.sequence;self.pending[command.sequence]=now_ns+self.response_timeout_ns
        try:
            if self.transport is not None:self.transport.write(encode_command(command))
        except Exception:self.pending.pop(command.sequence,None);return CommandResult(accepted=False,reason="TRANSPORT_WRITE_FAILED",sequence=command.sequence)
        return CommandResult(accepted=True,reason="QUEUED_FOR_ESP32",sequence=command.sequence)
    def expire_pending(self,now_ns:int)->list[int]:
        expired=[sequence for sequence,deadline in self.pending.items() if deadline<=now_ns]
        for sequence in expired:self.pending.pop(sequence,None)
        return expired
    def receive(self,frame:bytes,now_ns:int|None=None)->ESP32Feedback:
        message,envelope=decode_frame(frame)
        if message not in {ACK,NACK,STATUS}:raise ProtocolError("unexpected ESP32 feedback message")
        payload=envelope["payload"];accepted=message==ACK and bool(payload.get("accepted",True));sequence=envelope["sequence"]
        correlation="MATCHED" if sequence in self.pending else ("DUPLICATE" if sequence in self.seen_feedback else "UNKNOWN_OR_LATE")
        self.pending.pop(sequence,None);self.seen_feedback.append(sequence)
        feedback=ESP32Feedback(message,sequence,envelope["timestamp_ns"],accepted,str(payload.get("reason","UNSPECIFIED")),str(payload.get("output_state","UNKNOWN")),payload,correlation);self.last_feedback=feedback;return feedback
class ESP32ProtocolSimulator:
    """A deterministic endpoint—not proof of firmware, USB, output, or motion."""
    def __init__(self,configuration_hash:str):self.configuration_hash=configuration_hash;self.last_sequence=-1;self.last_response:bytes|None=None;self.output_state="DISABLED_PHASE_1"
    def _respond(self,kind:int,sequence:int,timestamp_ns:int,accepted:bool,reason:str)->None:self.last_response=encode_message(kind,sequence,timestamp_ns,{"accepted":accepted,"applied_left":0.0,"applied_right":0.0,"output_state":self.output_state,"reason":reason,"source_mode":"SIMULATION"})
    def write(self,frame:bytes)->None:
        try:message,envelope=decode_frame(frame)
        except ProtocolError:return
        payload=envelope["payload"];now_ns=envelope["timestamp_ns"]
        if message==HEARTBEAT:
            valid=isinstance(payload.get("configuration_hash"),str) and payload.get("configuration_hash")==self.configuration_hash and payload.get("protocol_version")==VERSION
            self._respond(ACK if valid else NACK,envelope["sequence"],now_ns,valid,"HEARTBEAT_ACCEPTED" if valid else "CONFIGURATION_MISMATCH");return
        if message!=COMMAND:self._respond(NACK,envelope["sequence"],now_ns,False,"UNEXPECTED_MESSAGE");return
        reason=validate_command_payload(payload,envelope["sequence"],envelope["timestamp_ns"],now_ns,self.configuration_hash)
        if reason is None and envelope["sequence"]<=self.last_sequence:reason="DUPLICATE_SEQUENCE" if envelope["sequence"]==self.last_sequence else "OLD_SEQUENCE"
        if reason is None:self.last_sequence=envelope["sequence"];self._respond(ACK,envelope["sequence"],now_ns,True,"COMMAND_ACCEPTED_DISABLED_PHASE_1")
        else:self._respond(NACK,envelope["sequence"],now_ns,False,reason)
