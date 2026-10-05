"""Node B v1 cooperative telemetry over ordinary local Wi-Fi, not vehicle control."""
from __future__ import annotations
import hashlib, hmac, json
from math import isfinite
from typing import Literal
from pydantic import Field, model_validator
from app.r3.adapters import Lg290pFix
from app.r3.contracts import Contract, Count, Token, Mode


class PeerMessage(Contract):
    protocol_version: int = Field(ge=1,le=1)
    node_id: Token
    boot_id: Token
    session_id: Token
    sequence: Count
    source_timestamp_ns: Count | None
    publication_time_ns: Count
    clock_domain: Token
    clock_mapping_id: Token | None
    capture_uncertainty_ns: Count | None
    fix: Lg290pFix
    health: str = Field(pattern=r'^(ONLINE|DEGRADED|FAILED|UNKNOWN)$')
    faults: list[Token] = Field(max_length=16)
    configuration_id: Token
    source_mode: Mode
    correction_state: Literal['UNKNOWN','NOT_REQUIRED','APPLIED','LOST'] = 'UNKNOWN'
    @model_validator(mode='after')
    def source_age(self):
        if self.source_timestamp_ns is not None and self.source_timestamp_ns>self.publication_time_ns: raise ValueError('peer source time after publication')
        if self.capture_uncertainty_ns is not None and self.source_timestamp_ns is None: raise ValueError('uncertainty without time')
        return self


def encode_peer(message:PeerMessage,key:bytes)->bytes:
    if len(key)<32: raise ValueError('peer key must contain at least 32 bytes')
    payload=message.model_dump_json().encode()
    result=json.dumps({'payload':payload.decode(),'hmac_sha256':hmac.new(key,payload,hashlib.sha256).hexdigest()},separators=(',', ':')).encode()
    if len(result)>8192: raise ValueError('peer message too large')
    return result


class PeerReceiver:
    """Replay resistance uses an explicitly admitted boot/session, not an arbitrary
    new boot string in a datagram. Trust/session admission is never automatic.
    Clock conversion is an injected, independently qualified mapping.
    """
    def __init__(self,*,node_id:str,configuration_id:str,key:bytes,max_age_ns:int,max_uncertainty_ns:int,mode:Mode,max_position_uncertainty_m:float=0.,require_corrections:bool=False):
        if len(key)<32 or max_age_ns<=0 or max_uncertainty_ns<0: raise ValueError('invalid peer configuration')
        if not isfinite(max_position_uncertainty_m) or max_position_uncertainty_m<0: raise ValueError('invalid position bound')
        self.node_id=node_id; self.configuration_id=configuration_id; self.key=key
        self.max_age_ns=max_age_ns; self.max_uncertainty_ns=max_uncertainty_ns; self.mode=mode
        self.max_position_uncertainty_m=max_position_uncertainty_m;self.require_corrections=require_corrections
        self.session=None; self.latest=None; self.last_arrival=None; self.last_sequence=None; self.capture=None; self.uncertainty=None
        self.drops=0; self.duplicates=0; self.rejections=0
    def admit_session(self,boot_id:str,session_id:str):
        if self.session==(boot_id,session_id): raise ValueError('session already admitted')
        self.session=(boot_id,session_id); self.latest=None; self.last_arrival=None; self.last_sequence=None; self.capture=None; self.uncertainty=None
    def receive(self,raw:bytes,now:int,clock_mapper)->bool:
        try:
            if len(raw)>8192: raise ValueError('peer message too large')
            envelope=json.loads(raw)
            if not isinstance(envelope,dict) or set(envelope)!={'payload','hmac_sha256'} or not isinstance(envelope['payload'],str) or not isinstance(envelope['hmac_sha256'],str): raise ValueError('invalid peer envelope')
            if not hmac.compare_digest(envelope['hmac_sha256'],hmac.new(self.key,envelope['payload'].encode(),hashlib.sha256).hexdigest()): raise ValueError('peer authentication failed')
            message=PeerMessage.model_validate_json(envelope['payload'])
            if (message.node_id,message.configuration_id,message.source_mode)!=(self.node_id,self.configuration_id,self.mode) or self.session!=(message.boot_id,message.session_id): raise ValueError('peer identity/session/mode mismatch')
            if self.last_sequence is not None and message.sequence<=self.last_sequence:
                self.duplicates+=1; return False
            if self.last_arrival is not None and now<self.last_arrival: raise ValueError('host clock reset')
            capture,uncertainty=clock_mapper(message,now)
            if capture is not None and (type(capture) is not int or capture<0 or capture>now or type(uncertainty) is not int or uncertainty<0): raise ValueError('invalid mapped peer clock')
            if self.last_sequence is not None: self.drops+=message.sequence-self.last_sequence-1
            self.last_sequence=message.sequence; self.last_arrival=now; self.latest=message; self.capture=capture; self.uncertainty=uncertainty
            return True
        except (ValueError,TypeError,KeyError,UnicodeError) as error:
            self.rejections+=1; raise ValueError('peer rejected: '+str(error)[:120]) from error
    def status(self,now:int):
        if self.latest is None:return {'state':'NOT_CONNECTED','source_mode':self.mode,'evidence_kind':'COOPERATIVE','position':None}
        age=None if self.capture is None or self.uncertainty is None else now-self.capture+self.uncertainty
        timely=age is not None and 0<=age<=self.max_age_ns and self.uncertainty<=self.max_uncertainty_ns
        fresh_receipt=self.last_arrival<=now<=self.last_arrival+self.max_age_ns
        position_bound=self.latest.fix.horizontal_uncertainty_m
        good=timely and fresh_receipt and self.latest.health=='ONLINE' and not self.latest.faults and self.latest.fix.fix_type not in {'NO_FIX','UNKNOWN'} and position_bound is not None and self.max_position_uncertainty_m>0 and position_bound<=self.max_position_uncertainty_m and (not self.require_corrections or self.latest.correction_state=='APPLIED')
        return {'state':'QUALIFIED_COOPERATIVE_CONTEXT' if good else 'UNQUALIFIED','source_mode':self.mode,'evidence_kind':'COOPERATIVE',
                'age_bound_ns':age,'position':self.latest.fix.model_dump(mode='json') if good else None,'sequence':self.last_sequence,
                'drops':self.drops,'duplicates':self.duplicates,'rejections':self.rejections,'local_observation':False,'unequipped_target_detection':False}

class DatagramPeerWorker:
    """Nonblocking, bounded ordinary-Wi-Fi datagram boundary with injected socket.

    No automatic network/device discovery. A commissioning owner supplies the
    bound nonblocking socket factory, authenticated peer address and clock mapper.
    """
    def __init__(self,receiver,peer_address,socket_factory,clock_mapper,*,retry_ns=1_000_000_000):
        if retry_ns<=0: raise ValueError('invalid retry interval')
        self.receiver=receiver;self.peer_address=peer_address;self.factory=socket_factory;self.clock_mapper=clock_mapper
        self.retry_ns=retry_ns;self.next_retry=0;self.socket=None;self.closed=False;self.state='NOT_CONNECTED';self.rejected=0
    def pump(self,now):
        if self.closed or now<self.next_retry:return
        try:
            if self.socket is None:self.socket=self.factory();self.socket.setblocking(False);self.state='LISTENING_UNVERIFIED'
            for _ in range(32):
                try:raw,address=self.socket.recvfrom(8193)
                except BlockingIOError:break
                if address!=self.peer_address:self.rejected+=1;continue
                try:self.receiver.receive(raw,now,self.clock_mapper)
                except ValueError:self.rejected+=1
        except OSError:
            if self.socket:self.socket.close()
            self.socket=None;self.state='NETWORK_UNAVAILABLE';self.next_retry=now+self.retry_ns
            # No replacement or simulated position is inserted on network failure.
    def close(self):
        self.closed=True
        if self.socket:self.socket.close()
        self.socket=None;self.state='NOT_CONNECTED'
