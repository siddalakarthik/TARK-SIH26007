"""Single Pi/ESP32 codec and session contract; V2 rejects legacy V1 frames.

No browser authority. No physical identity or actuation is established by ACK.
"""
from __future__ import annotations
import struct
import time
import uuid
from copy import deepcopy
from collections import deque
from dataclasses import dataclass
from math import isfinite
from threading import RLock
from typing import Any, Protocol
import cbor2
from app.domain.models import BoundedCommand, CommandResult

MAGIC=0x544B; VERSION=2
COMMAND=1; ACK=2; NACK=3; HEARTBEAT=4; STATUS=5; SESSION_OPEN=6; SESSION_READY=7
MESSAGE_NAMES={COMMAND:'COMMAND',ACK:'ACK',NACK:'NACK',HEARTBEAT:'HEARTBEAT',STATUS:'STATUS',SESSION_OPEN:'SESSION_OPEN',SESSION_READY:'SESSION_READY'}
MAX_SEQUENCE=0xFFFFFFFF; MAX_UINT64=0xFFFFFFFFFFFFFFFF
MAX_PAYLOAD=512; MAX_FRAME=640; HEADER=struct.Struct('!HBBIQQ')
MAX_COMMAND_LIFETIME_NS=500_000_000; MAX_PENDING=64
OUTPUT_STATE='DISABLED_PHASE_1'
COMMAND_FIELDS={'protocol_version','sequence','timestamp_ns','valid_until_ns','state','permitted_speed_mps','left_command','right_command','heartbeat','reason_code','configuration_hash','session_id'}
REJECTION_REASONS=frozenset({'DUPLICATE_SEQUENCE','OLD_SEQUENCE','OUT_OF_ORDER_SEQUENCE','COMMAND_EXPIRED','HEARTBEAT_TIMEOUT','CONFIGURATION_MISMATCH','SESSION_MISMATCH','INVALID_PAYLOAD','INVALID_VERSION','INVALID_CRC','INVALID_LENGTH','INVALID_LIFETIME','NOT_ENABLED','INTERNAL_FAULT','UNEXPECTED_MESSAGE'})

class ProtocolError(ValueError):
    def __init__(self,reason:str): super().__init__(reason); self.reason=reason
class FrameTransport(Protocol):
    def write(self,frame:bytes)->None: ...
@dataclass
class TransportCounters:
    frames_received:int=0;frames_valid:int=0;frames_invalid:int=0;crc_failures:int=0;cobs_failures:int=0;header_failures:int=0;length_failures:int=0;unknown_message_count:int=0;bytes_received:int=0;reconnect_count:int=0
    def reject(self,error:ProtocolError)->None:
        self.frames_invalid+=1
        if error.reason=='CRC32C mismatch':self.crc_failures+=1
        elif error.reason=='invalid COBS frame':self.cobs_failures+=1
        elif error.reason in {'frame too short','payload too large','header validation failed','frame too large'}:self.length_failures+=1
        elif error.reason in {'unknown message type','unsupported protocol version'}:self.unknown_message_count+=1
        else:self.header_failures+=1
@dataclass(frozen=True)
class ESP32Feedback:
    message_type:int;sequence:int;timestamp_ns:int;accepted:bool;reason:str;output_state:str;payload:dict[str,Any];correlation:str='MATCHED'
@dataclass(frozen=True)
class PendingCommand:
    deadline_ns:int; timestamp_ns:int; session_id:str; configuration_hash:str; message_type:int

def crc32c(data:bytes)->int:
    crc=0xFFFFFFFF
    for byte in data:
        crc^=byte
        for _ in range(8):crc=(crc>>1)^0x82F63B78 if crc&1 else crc>>1
    return (~crc)&0xFFFFFFFF

def cobs_encode(data:bytes)->bytes:
    out=bytearray([0]); index=0; code=1
    for byte in data:
        if byte==0:out[index]=code;index=len(out);out.append(0);code=1
        else:
            out.append(byte);code+=1
            if code==255:out[index]=code;index=len(out);out.append(0);code=1
    out[index]=code
    return bytes(out)

def cobs_decode(data:bytes)->bytes:
    if not data:raise ProtocolError('invalid COBS frame')
    out=bytearray();i=0
    while i<len(data):
        code=data[i]
        if code==0 or i+code>len(data) or 0 in data[i+1:i+code]:raise ProtocolError('invalid COBS frame')
        i+=1;out.extend(data[i:i+code-1]);i+=code-1
        if code<255 and i<len(data):out.append(0)
    return bytes(out)

def uint(value:Any,maximum:int=MAX_UINT64)->bool:return type(value) is int and 0<=value<=maximum
def token(value:Any,maximum:int=127)->bool:return isinstance(value,str) and 0<len(value)<=maximum and all(32<=ord(c)<=126 for c in value)
def hex_token(value:Any,length:int)->bool:return isinstance(value,str) and len(value)==length and all(c in '0123456789abcdef' for c in value)
def number(value:Any)->bool:
    return type(value) in {int,float} and (type(value) is not int or -1-MAX_UINT64<=value<=MAX_UINT64) and isfinite(value)
def command_number(value:Any)->bool:
    return number(value) and (type(value) is not int or float(value)==value)

def _flat_payload(payload:Any)->bool:
    if not isinstance(payload,dict) or len(payload)>24:return False
    for key,value in payload.items():
        if not token(key,31):return False
        if value is None or type(value) is bool:continue
        if token(value) or number(value):continue
        return False
    return True

def encode_message(message_type:int,sequence:int,timestamp_ns:int,payload_data:dict[str,Any])->bytes:
    if message_type not in MESSAGE_NAMES:raise ValueError('unknown message type')
    if not uint(sequence,MAX_SEQUENCE) or not uint(timestamp_ns):raise ValueError('invalid protocol sequence or timestamp')
    if not _flat_payload(payload_data):raise ValueError('invalid protocol payload profile')
    payload=cbor2.dumps(payload_data,canonical=True)
    if len(payload)>MAX_PAYLOAD:raise ValueError('payload too large')
    body=HEADER.pack(MAGIC,VERSION,message_type,len(payload),sequence,timestamp_ns)+payload
    frame=b'\0'+cobs_encode(body+struct.pack('!I',crc32c(body)))+b'\0'
    if len(frame)>MAX_FRAME:raise ValueError('frame too large')
    return frame

def encode_command(command:BoundedCommand,session_id:str)->bytes:
    return encode_message(COMMAND,command.sequence,command.timestamp_ns,{**command.model_dump(mode='json'),'session_id':session_id})

def encode_heartbeat(sequence:int,timestamp_ns:int,configuration_hash:str,session_id:str)->bytes:
    return encode_message(HEARTBEAT,sequence,timestamp_ns,{'configuration_hash':configuration_hash,'protocol_version':VERSION,'session_id':session_id})

def decode_frame(frame:bytes)->tuple[int,dict[str,Any]]:
    if len(frame)>MAX_FRAME:raise ProtocolError('frame too large')
    if not frame.startswith(b'\0') or not frame.endswith(b'\0'):raise ProtocolError('missing delimiter')
    decoded=cobs_decode(frame[1:-1])
    if len(decoded)<HEADER.size+4:raise ProtocolError('frame too short')
    body,supplied=decoded[:-4],struct.unpack('!I',decoded[-4:])[0]
    if crc32c(body)!=supplied:raise ProtocolError('CRC32C mismatch')
    magic,version,message,length,sequence,timestamp=HEADER.unpack(body[:HEADER.size])
    if magic!=MAGIC:raise ProtocolError('bad magic')
    if version!=VERSION:raise ProtocolError('unsupported protocol version')
    if message not in MESSAGE_NAMES:raise ProtocolError('unknown message type')
    if length>MAX_PAYLOAD:raise ProtocolError('payload too large')
    if length!=len(body)-HEADER.size or sequence>MAX_SEQUENCE:raise ProtocolError('header validation failed')
    raw=body[HEADER.size:]
    try:
        payload=cbor2.loads(raw)
        # Canonical round-trip rejects duplicate keys, trailing objects,
        # overlong integers, indefinite forms and non-shortest float encodings.
        if not _flat_payload(payload) or cbor2.dumps(payload,canonical=True)!=raw:
            raise ValueError('noncanonical/unsupported CBOR')
    except Exception as error:raise ProtocolError('invalid canonical CBOR payload') from error
    return message,{'sequence':sequence,'timestamp_ns':timestamp,'payload':payload}

class FrameAccumulator:
    def __init__(self,max_frame:int=MAX_FRAME,counters:TransportCounters|None=None):
        self.max_frame=max_frame;self.counters=counters or TransportCounters();self.reset()
    def reset(self):self._inside=False;self._buffer=bytearray()
    def feed(self,data:bytes)->list[bytes]:
        self.counters.bytes_received+=len(data);frames=[]
        for byte in data:
            if byte==0:
                if self._inside and self._buffer:frames.append(b'\0'+bytes(self._buffer)+b'\0')
                self._buffer.clear();self._inside=True;continue
            if not self._inside:continue
            if len(self._buffer)>=self.max_frame-2:
                self.counters.frames_received+=1;self.counters.frames_invalid+=1;self.counters.length_failures+=1;self.reset();continue
            self._buffer.append(byte)
        return frames
    def decode(self,data:bytes)->list[tuple[int,dict[str,Any]]]:
        values=[]
        for frame in self.feed(data):
            self.counters.frames_received+=1
            try:values.append(decode_frame(frame));self.counters.frames_valid+=1
            except ProtocolError as error:self.counters.reject(error)
        return values

def validate_command_payload(payload:dict[str,Any],sequence:int,timestamp_ns:int,now_ns:int,configuration_hash:str,session_id:str)->str|None:
    if not COMMAND_FIELDS.issubset(payload) or set(payload)-COMMAND_FIELDS-{'checksum'}:return 'INVALID_PAYLOAD'
    if not uint(sequence,MAX_SEQUENCE) or not uint(timestamp_ns) or not uint(now_ns):return 'INVALID_PAYLOAD'
    if not uint(payload['sequence'],MAX_SEQUENCE) or payload['sequence']!=sequence or not uint(payload['timestamp_ns']) or payload['timestamp_ns']!=timestamp_ns:return 'INVALID_PAYLOAD'
    if type(payload['protocol_version']) is not int or payload['protocol_version']!=VERSION:return 'INVALID_VERSION'
    if not token(payload['configuration_hash']):return 'INVALID_PAYLOAD'
    if payload['configuration_hash']!=configuration_hash:return 'CONFIGURATION_MISMATCH'
    if not hex_token(payload['session_id'],48) or payload['session_id']!=session_id:return 'SESSION_MISMATCH'
    until=payload['valid_until_ns']
    if not uint(until) or until<=timestamp_ns:return 'COMMAND_EXPIRED'
    ttl=until-timestamp_ns
    if ttl>MAX_COMMAND_LIFETIME_NS or now_ns>MAX_UINT64-ttl:return 'INVALID_LIFETIME'
    if not isinstance(payload['state'],str) or payload['state'] not in {'NORMAL','WARN','RESTRICT','UNKNOWN','STOP'} or not token(payload['reason_code'],31) or not uint(payload['heartbeat'],MAX_SEQUENCE):return 'INVALID_PAYLOAD'
    if any(not command_number(payload[k]) for k in ('permitted_speed_mps','left_command','right_command')):return 'INVALID_PAYLOAD'
    if payload['permitted_speed_mps']<0 or abs(payload['left_command'])>1 or abs(payload['right_command'])>1:return 'INVALID_PAYLOAD'
    if payload.get('checksum') is not None:return 'INVALID_PAYLOAD'
    return None

class ESP32Client:
    """Thread-safe bounded correlation; only timely session-bound ACKs are ONLINE."""
    def __init__(self,transport:FrameTransport|None=None,response_timeout_ns:int=MAX_COMMAND_LIFETIME_NS,*,clock=time.monotonic_ns,nonce_factory=lambda:uuid.uuid4().hex):
        if not 0<response_timeout_ns<=MAX_COMMAND_LIFETIME_NS:raise ValueError('invalid response timeout')
        self.transport=transport;self.response_timeout_ns=response_timeout_ns;self.clock=clock;self.nonce_factory=nonce_factory
        self._lock=RLock();self.pending:dict[int,PendingCommand]={};self.terminal=deque(maxlen=256)
        self.seen_feedback=deque(maxlen=256);self.configuration_hash=None;self.invalid_feedback=0
        self.reset_session()
    def reset_session(self)->None:
        with self._lock:
            for sequence in self.pending:self.terminal.append((sequence,'SUPERSEDED'))
            self.pending.clear();self.session_id=None;self.request_id=None;self.request_timestamp_ns=None;self.request_deadline_ns=None
            self.last_sequence=-1;self.last_feedback=None;self.last_exchange_ns=None;self.last_status_timestamp_ns=None
    def expire_pending(self,now_ns:int)->list[int]:
        with self._lock:
            expired=[q for q,p in self.pending.items() if p.deadline_ns<=now_ns]
            for q in expired:self.pending.pop(q);self.terminal.append((q,'EXPIRED'))
            if expired and self.session_id is not None and (self.last_exchange_ns is None or now_ns-self.last_exchange_ns>=self.response_timeout_ns):
                # Receiver reboot need not cause a serial disconnect. Loss of
                # correlated replies retires this session and forces a new
                # challenge before any subsequent command can be queued.
                self.reset_session()
            if self.request_deadline_ns is not None and now_ns>=self.request_deadline_ns:
                self.request_id=None;self.request_deadline_ns=None
            return expired
    def _open_session(self,now:int)->None:
        if self.request_id is not None:return
        if self.transport is None:raise ProtocolError('TRANSPORT_UNAVAILABLE')
        if not uint(now,MAX_UINT64-self.response_timeout_ns):raise ProtocolError('INVALID_LIFETIME')
        request=self.nonce_factory()
        if not hex_token(request,32):raise ProtocolError('INVALID_SESSION_NONCE')
        self.request_id=request;self.request_timestamp_ns=now;self.request_deadline_ns=now+self.response_timeout_ns
        self.transport.write(encode_message(SESSION_OPEN,0,now,{'request_id':request,'configuration_hash':self.configuration_hash}))
        # Only the explicit in-process simulator offers synchronous replies.
        if isinstance(self.transport,ESP32ProtocolSimulator) and self.transport.last_response:
            self.receive(self.transport.last_response,now)
    def submit(self,command:BoundedCommand,now_ns:int)->CommandResult:
        def rejected(reason):return CommandResult(accepted=False,reason=reason,sequence=command.sequence)
        with self._lock:
            self.expire_pending(now_ns)
            if not uint(command.sequence,MAX_SEQUENCE):return rejected('COMMAND_SEQUENCE_OUT_OF_RANGE')
            if not uint(now_ns) or not 0<=command.timestamp_ns<=now_ns or command.valid_until_ns<=now_ns:return rejected('COMMAND_EXPIRED')
            if not 0<command.valid_until_ns-command.timestamp_ns<=MAX_COMMAND_LIFETIME_NS:return rejected('INVALID_LIFETIME')
            values=(command.permitted_speed_mps,command.left_command,command.right_command)
            if not all(number(v) for v in values) or values[0]<0 or abs(values[1])>1 or abs(values[2])>1:return rejected('COMMAND_OUT_OF_RANGE')
            if self.configuration_hash is None:self.configuration_hash=command.configuration_hash
            if self.configuration_hash!=command.configuration_hash:return rejected('CONFIGURATION_MISMATCH')
            try:
                if self.session_id is None:self._open_session(now_ns)
            except Exception:
                self.reset_session();return rejected('TRANSPORT_WRITE_FAILED')
            if self.session_id is None:return rejected('SESSION_PENDING')
            if command.sequence<=self.last_sequence:return rejected('COMMAND_OUT_OF_ORDER')
            reason=validate_command_payload({**command.model_dump(mode='json'),'session_id':self.session_id},command.sequence,command.timestamp_ns,now_ns,self.configuration_hash,self.session_id)
            if reason:return rejected(reason)
            while len(self.pending)>=MAX_PENDING:
                oldest=next(iter(self.pending));self.pending.pop(oldest);self.terminal.append((oldest,'SUPERSEDED'))
            self.last_sequence=command.sequence
            self.pending[command.sequence]=PendingCommand(min(command.valid_until_ns,now_ns+self.response_timeout_ns),command.timestamp_ns,self.session_id,self.configuration_hash,COMMAND)
            try:self.transport.write(encode_command(command,self.session_id))
            except Exception:
                self.pending.pop(command.sequence,None);self.terminal.append((command.sequence,'PROTOCOL_ERROR'));return rejected('TRANSPORT_WRITE_FAILED')
            return CommandResult(accepted=True,reason='QUEUED_FOR_ESP32',sequence=command.sequence)
    def receive(self,frame:bytes,now_ns:int|None=None)->ESP32Feedback|None:
        now=self.clock() if now_ns is None else now_ns
        with self._lock:
            self.expire_pending(now)
            try:return self._receive(frame,now)
            except (ProtocolError,ValueError,TypeError):self.invalid_feedback+=1;raise
    def submit_heartbeat(self,sequence:int,now_ns:int)->None:
        with self._lock:
            self.expire_pending(now_ns)
            if self.session_id is None or not uint(sequence,MAX_SEQUENCE) or sequence<=self.last_sequence or not uint(now_ns,MAX_UINT64-self.response_timeout_ns):
                raise ProtocolError('INVALID_HEARTBEAT_SUBMISSION')
            while len(self.pending)>=MAX_PENDING:
                oldest=next(iter(self.pending));self.pending.pop(oldest);self.terminal.append((oldest,'SUPERSEDED'))
            self.last_sequence=sequence
            self.pending[sequence]=PendingCommand(now_ns+self.response_timeout_ns,now_ns,self.session_id,self.configuration_hash,HEARTBEAT)
            try:self.transport.write(encode_heartbeat(sequence,now_ns,self.configuration_hash,self.session_id))
            except Exception:
                self.pending.pop(sequence,None);self.terminal.append((sequence,'PROTOCOL_ERROR'));raise
    def _receive(self,frame:bytes,now:int)->ESP32Feedback|None:
        message,envelope=decode_frame(frame);p=envelope['payload'];q=envelope['sequence']
        source='SIMULATION' if isinstance(self.transport,ESP32ProtocolSimulator) else 'REAL'
        if message==SESSION_READY:
            if (set(p)!={'request_id','session_id','configuration_hash','source_mode'} or self.request_id is None
                or p['request_id']!=self.request_id or q!=0 or envelope['timestamp_ns']!=self.request_timestamp_ns
                or p['configuration_hash']!=self.configuration_hash or p['source_mode']!=source or not hex_token(p['session_id'],48)):
                raise ProtocolError('INVALID_SESSION_RESPONSE')
            self.session_id=p['session_id'];self.request_id=None;self.request_deadline_ns=None;return None
        if message not in {ACK,NACK,STATUS}:raise ProtocolError('unexpected ESP32 feedback message')
        fields={'reason','output_state','source_mode','session_id','configuration_hash'}
        if message in {ACK,NACK}:fields|={'accepted','applied_left','applied_right'}
        if set(p)!=fields or not token(p.get('reason'),63) or p.get('output_state')!=OUTPUT_STATE:raise ProtocolError('INVALID_RESPONSE_SCHEMA')
        if self.session_id is None or p['session_id']!=self.session_id or p['configuration_hash']!=self.configuration_hash or p['source_mode']!=source:raise ProtocolError('RESPONSE_IDENTITY_MISMATCH')
        if message==STATUS:
            if p['reason'] not in REJECTION_REASONS|{'NONE'}:raise ProtocolError('INVALID_STATUS_REASON')
            if self.last_feedback is None or q!=self.last_feedback.sequence:raise ProtocolError('UNSOLICITED_STATUS')
            if self.last_status_timestamp_ns is not None and envelope['timestamp_ns']<=self.last_status_timestamp_ns:raise ProtocolError('OLD_STATUS')
            self.last_status_timestamp_ns=envelope['timestamp_ns']
            # STATUS is telemetry, not evidence of a timely command round-trip.
            return ESP32Feedback(message,q,envelope['timestamp_ns'],False,p['reason'],p['output_state'],p,'TELEMETRY')
        if type(p['accepted']) is not bool or p['accepted']!=(message==ACK) or any(not number(p[k]) or p[k]!=0 for k in ('applied_left','applied_right')):raise ProtocolError('INVALID_RESPONSE_SCHEMA')
        pending=self.pending.get(q)
        if pending is None:raise ProtocolError('UNKNOWN_DUPLICATE_OR_LATE_RESPONSE')
        if pending.timestamp_ns!=envelope['timestamp_ns'] or pending.session_id!=self.session_id:raise ProtocolError('RESPONSE_IDENTITY_MISMATCH')
        if message==NACK and p['reason'] not in REJECTION_REASONS:raise ProtocolError('INVALID_REJECTION_REASON')
        expected_reason='HEARTBEAT_ACCEPTED' if pending.message_type==HEARTBEAT else 'COMMAND_ACCEPTED_DISABLED_PHASE_1'
        if message==ACK and p['reason']!=expected_reason:raise ProtocolError('INVALID_ACCEPTANCE_REASON')
        self.pending.pop(q);self.terminal.append((q,'ACKNOWLEDGED' if message==ACK else 'REJECTED'));self.seen_feedback.append((self.session_id,q))
        self.last_feedback=ESP32Feedback(message,q,envelope['timestamp_ns'],message==ACK,p['reason'],p['output_state'],p)
        self.last_exchange_ns=now
        return self.last_feedback
    def health(self,now_ns:int)->dict:
        with self._lock:
            self.expire_pending(now_ns)
            age=None if self.last_exchange_ns is None else now_ns-self.last_exchange_ns
            state='NOT_CONNECTED' if age is None else 'STALE' if not 0<=age<self.response_timeout_ns else 'ONLINE' if self.last_feedback.accepted else 'DEGRADED'
            return {'state':state,'timestamp_ns':self.last_exchange_ns,'age_ms':None if age is None else max(0,age)/1e6,'reason':'NO_VALIDATED_EXCHANGE' if age is None else 'PHASE_1 OUTPUTS DISABLED','pending_count':len(self.pending)}
    def feedback_snapshot(self,now_ns:int)->dict|None:
        with self._lock:
            if self.health(now_ns)['state'] not in {'ONLINE','DEGRADED'}:return None
            return deepcopy(self.last_feedback.__dict__)

class ESP32ProtocolSimulator:
    """Explicit software endpoint with independent clock and reboot identity."""
    def __init__(self,configuration_hash:str,*,clock=time.monotonic_ns,boot_id:str|None=None):
        self.configuration_hash=configuration_hash;self.clock=clock;self.boot_id=boot_id or uuid.uuid4().hex
        if not hex_token(self.boot_id,32):raise ValueError('invalid boot identity')
        self.generation=0;self.session_id=None;self.last_sequence=-1;self.last_response=None;self.output_state=OUTPUT_STATE;self.local_expiry_ns=None;self.last_reason='NOT_ENABLED';self.last_tick_ns=None
    def _respond(self,kind,q,stamp,reason):
        if kind==NACK:self.local_expiry_ns=None;self.last_reason=reason
        self.last_response=encode_message(kind,q,stamp,{'accepted':kind==ACK,'applied_left':0.0,'applied_right':0.0,'output_state':OUTPUT_STATE,'reason':reason,'source_mode':'SIMULATION','configuration_hash':self.configuration_hash,'session_id':self.session_id})
    def tick(self,now_ns:int)->None:
        if not uint(now_ns) or self.last_tick_ns is not None and now_ns<self.last_tick_ns:
            self.last_reason='INTERNAL_FAULT';self.local_expiry_ns=None;return
        self.last_tick_ns=now_ns
        if self.local_expiry_ns is not None and now_ns>=self.local_expiry_ns:
            self.last_reason='COMMAND_EXPIRED';self.local_expiry_ns=None
    def write(self,frame:bytes)->None:
        self.last_response=None
        try:message,e=decode_frame(frame)
        except ProtocolError:self.local_expiry_ns=None;self.last_reason='INVALID_PAYLOAD';return
        p=e['payload'];now=self.clock()
        rollback=not uint(now) or self.last_tick_ns is not None and now<self.last_tick_ns
        self.tick(now)
        if rollback:return
        if message==SESSION_OPEN:
            if set(p)!={'request_id','configuration_hash'} or not hex_token(p.get('request_id'),32) or p.get('configuration_hash')!=self.configuration_hash or e['sequence']!=0 or self.generation==MAX_UINT64:
                self.local_expiry_ns=None;self.last_reason='INVALID_PAYLOAD';return
            self.generation+=1;self.session_id=self.boot_id+f'{self.generation:016x}';self.last_sequence=-1;self.local_expiry_ns=None;self.last_reason='NOT_ENABLED'
            self.last_response=encode_message(SESSION_READY,0,e['timestamp_ns'],{'request_id':p['request_id'],'session_id':self.session_id,'configuration_hash':self.configuration_hash,'source_mode':'SIMULATION'});return
        if self.session_id is None:return
        if message==HEARTBEAT:
            if set(p)!={'protocol_version','configuration_hash','session_id'} or type(p.get('protocol_version')) is not int or p['protocol_version']!=VERSION or p.get('configuration_hash')!=self.configuration_hash or p.get('session_id')!=self.session_id:
                self._respond(NACK,e['sequence'],e['timestamp_ns'],'INVALID_PAYLOAD');return
            if e['sequence']<=self.last_sequence:
                self._respond(NACK,e['sequence'],e['timestamp_ns'],'OLD_SEQUENCE');return
            self.last_sequence=e['sequence'];self._respond(ACK,e['sequence'],e['timestamp_ns'],'HEARTBEAT_ACCEPTED');return
        if message!=COMMAND:
            self._respond(NACK,e['sequence'],e['timestamp_ns'],'UNEXPECTED_MESSAGE');return
        reason=validate_command_payload(p,e['sequence'],e['timestamp_ns'],now,self.configuration_hash,self.session_id)
        if reason is None and e['sequence']<=self.last_sequence:reason='DUPLICATE_SEQUENCE' if e['sequence']==self.last_sequence else 'OLD_SEQUENCE'
        if reason is None:
            self.last_sequence=e['sequence'];self.local_expiry_ns=now+p['valid_until_ns']-p['timestamp_ns'];self.last_reason='NONE'
            self._respond(ACK,e['sequence'],e['timestamp_ns'],'COMMAND_ACCEPTED_DISABLED_PHASE_1')
        else:self._respond(NACK,e['sequence'],e['timestamp_ns'],reason)
