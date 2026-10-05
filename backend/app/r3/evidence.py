"""Bounded observation channel. Qualification is derived, never trusted from a sender."""
from __future__ import annotations
from collections import deque
from copy import deepcopy
from threading import RLock
from app.r3.contracts import HardwareProfile, Identity, Mode, Observation
from app.r3.registry import ClockRegistry, CalibrationRegistry, ConfigurationRegistry


def age_readiness(view:dict, now:int)->dict:
    """Age a detached publication without accepting data or changing a decision.

    Source deadlines can be shorter than the decision-loop interval. Polling a
    cached snapshot must never extend those deadlines. Recorded tick evidence
    remains untouched and is recomputed at its original timestamp.
    """
    result=deepcopy(view)
    elapsed=now-result['timestamp_ns']
    result['view_timestamp_ns']=now
    advisory=result.get('advisory')
    if advisory:
        result.setdefault('reasoning_metrics',{})['decision_publication_age_ns']=max(0,now-advisory['timestamp_ns'])
    if advisory and (now<advisory['timestamp_ns'] or now>advisory['valid_until_ns']):
        stopped=advisory['state']=='STOP'
        action='STOP_ADVISORY' if stopped else 'HOLD_INSUFFICIENT_EVIDENCE'
        advisory.update(state='STOP' if stopped else 'UNKNOWN',advised_speed_mps=0. if stopped else None,advisory=action,limiting_reason='DECISION_PUBLICATION_EXPIRED')
        advisory['explanation'].update(primary_reason='DECISION_PUBLICATION_EXPIRED',action=action)
        advisory['cooperative_context']=[]
        advisory['publication_expired']=True
    for row in result['sources']:
        if elapsed<0:
            row.update(fresh=False,producing=False,time_valid=False,qualified=False,
                       qualified_for=[],clock_state='CLOCK_RESET',fault_reason='HOST_CLOCK_RESET')
            continue
        for key in ('age_bound_ns','arrival_age_ns'):
            if row[key] is not None:row[key]+=elapsed
        limit=row['max_age_ns']
        row['fresh']=row['fresh'] and row['age_bound_ns'] is not None and row['age_bound_ns']<=limit
        row['producing']=row['producing'] and row['arrival_age_ns'] is not None and row['arrival_age_ns']<=limit
        deadline=row['clock_valid_until_ns']
        if deadline is not None and now>deadline:
            row.update(time_valid=False,clock_state='TIME_UNSYNCED')
        if not row['fresh'] or not row['producing'] or not row['time_valid']:
            row.update(qualified=False,qualified_for=[])
            if row['fault_reason'] is None:
                row['fault_reason']='STALE_OR_AGE_UNKNOWN' if not row['fresh'] or not row['producing'] else 'TIME_UNQUALIFIED'
    return result


class EvidenceChannel:
    def __init__(self,profile:HardwareProfile,host_epoch:str,*,channel='LIVE',allowed_modes=('REAL','SIMULATION')):
        if channel not in {'LIVE','REPLAY','RECOMPUTATION'}: raise ValueError('unknown channel')
        self.profile=profile; self.host_epoch=host_epoch; self.channel=channel
        self.allowed_modes=set(allowed_modes); self.profiles={s.source_id:s for s in profile.sources}
        self.clocks=ClockRegistry(); self.calibrations=CalibrationRegistry(); self.configurations=ConfigurationRegistry()
        self._lock=RLock(); self.sessions={}; self.latest={}; self.queues={s.source_id:deque(maxlen=s.max_queue) for s in profile.sources}
        self.counters={s.source_id:{'accepted':0,'duplicates':0,'out_of_order':0,'drops':0,'history_evictions':0,'invalid':0,'restarts':0} for s in profile.sources}
        self.timeline=deque(maxlen=100)
        self._last_states={}

    def begin_source(self,identity:Identity,mode:Mode,*,detected=False,identity_verified=False):
        """Local adapter lifecycle hook, NOT a browser/wire authorization endpoint."""
        with self._lock:
            p=self.profiles.get(identity.source_id)
            if not p or (p.node_id,p.device_class,p.manufacturer,p.part_number)!=(identity.node_id,identity.device_class,identity.manufacturer,identity.part_number):
                raise ValueError('unexpected R3 identity; legacy drivers are not substitutes')
            if (self.channel=='LIVE' and mode=='REPLAY') or (self.channel=='REPLAY' and mode!='REPLAY') or mode not in self.allowed_modes:
                raise ValueError('channel provenance boundary')
            if identity_verified and (mode!='REAL' or not (identity.asset_id or identity.serial_number)):
                raise ValueError('physical identity requires an identified real asset')
            previous=self.sessions.get(identity.source_id)
            if previous and previous['identity']==identity:
                raise ValueError('duplicate lifecycle session; do not refresh evidence')
            if previous: self.counters[identity.source_id]['restarts']+=1
            self.sessions[identity.source_id]={'identity':identity.model_copy(deep=True),'mode':mode,'detected':detected,'identity_verified':identity_verified,'running':True,'fault':None}
            self.latest.pop(identity.source_id,None); self.queues[identity.source_id].clear()

    def stop_source(self,source_id:str,reason='NOT_CONNECTED'):
        with self._lock:
            if source_id in self.sessions: self.sessions[source_id].update(running=False,detected=False,fault=reason[:128])

    def accept(self,observation:Observation,now_ns:int)->bool:
        # Revalidation catches mutable nested objects even on a frozen model.
        observation=Observation.model_validate_json(observation.model_dump_json())
        source=observation.identity.source_id
        with self._lock:
            session=self.sessions.get(source)
            if session is None or not session['running']: raise ValueError('source session not running')
            counts=self.counters[source]
            if session['identity']!=observation.identity or session['mode']!=observation.provenance.mode:
                counts['invalid']+=1; raise ValueError('identity/session/provenance mismatch')
            if observation.time.host_epoch!=self.host_epoch or observation.time.publication_time>now_ns:
                counts['invalid']+=1; raise ValueError('host epoch/future publication')
            self.configurations.require(observation)
            previous=self.latest.get(source)
            if previous:
                q,old=observation.integrity.sequence_number,previous.integrity.sequence_number
                if q<=old:
                    counts['duplicates' if q==old else 'out_of_order']+=1; return False
                if observation.time.host_monotonic_arrival<previous.time.host_monotonic_arrival:
                    counts['out_of_order']+=1; return False
                # Source counter/native clock reset requires explicit lifecycle restart.
                a,b=observation.integrity.source_counter,previous.integrity.source_counter
                if a is not None and b is not None and a<=b:
                    counts['duplicates' if a==b else 'out_of_order']+=1; return False
                a,b=observation.time.native_timestamp,previous.time.native_timestamp
                if a is not None and b is not None and a<b:
                    session['fault']='CLOCK_RESET'; counts['invalid']+=1; return False
                counts['drops']+=max(0,q-old-1)
            queue=self.queues[source]
            # This deque is a retained rate/history window, not an unconsumed
            # work queue. Trimming history must not claim a transport loss.
            if len(queue)==queue.maxlen: counts['history_evictions']+=1
            queue.append(observation); self.latest[source]=observation; counts['accepted']+=1
            self.timeline.append({'source_id':source,'observation_id':observation.observation_id,'arrival_ns':observation.time.host_monotonic_arrival,'mode':observation.provenance.mode,'event':'OBSERVATION_ACCEPTED'})
            return True

    def readiness(self,source_id:str,now:int)->dict:
        with self._lock:
            p=self.profiles[source_id]; s=self.sessions.get(source_id); o=self.latest.get(source_id)
            row={'source_id':source_id,'part_number':p.part_number,'expected':True,'detected':bool(s and s['detected']),
                 'identity_verified':bool(s and s['identity_verified']),'driver_ready':bool(s and s['running']),
                 'producing':False,'fresh':False,'plausible':False,'time_valid':False,'calibration_valid':False,
                 'qualified':False,'qualified_for':[],'mode':s['mode'] if s else 'UNAVAILABLE',
                 'maturity':'HARDWARE_UNVERIFIED','rate_hz':None,'age_bound_ns':None,'arrival_age_ns':None,
                 'max_age_ns':p.max_age_ns,'clock_valid_until_ns':None,
                 'clock_state':'TIME_UNSYNCED','calibration_state':'MISSING','fault_reason':s['fault'] if s and s['fault'] else 'NO_DATA',
                 'connection_state':'UNKNOWN','health_state':'UNKNOWN','evidence_origin':None,'uncertainty':None,
                 'queue_depth':0,'history_depth':len(self.queues[source_id]),'counters':dict(self.counters[source_id]),'observation_id':None}
            if not o: return row
            t=o.time; q=o.qualification
            row['observation_id']=o.observation_id
            if now<t.publication_time or t.host_epoch!=self.host_epoch:
                row['clock_state']='CLOCK_RESET'; row['fault_reason']='HOST_CLOCK_RESET'; return row
            row['arrival_age_ns']=now-t.host_monotonic_arrival
            row['connection_state']=q.connection_state
            row['health_state']=q.health_state
            row['evidence_origin']=o.provenance.evidence_origin
            row['uncertainty']=deepcopy(q.uncertainty)
            row['producing']=bool(s['running'] and q.production_state=='PRODUCING' and row['arrival_age_ns']<=p.max_age_ns)
            row['plausible']=q.plausibility_state=='PLAUSIBLE'
            if t.estimated_capture_time is not None and t.capture_time_uncertainty is not None:
                row['age_bound_ns']=now-t.estimated_capture_time+t.capture_time_uncertainty
                row['fresh']=row['age_bound_ns']<=p.max_age_ns
            mapped,uncertainty,state=self.clocks.capture(t.clock_mapping_version or '',t.native_timestamp if t.native_timestamp is not None else -1,
                source_id=source_id,boot_id=o.identity.boot_id,host_epoch=t.host_epoch,now=t.publication_time)
            mapping=self.clocks.records.get(t.clock_mapping_version or '')
            row['clock_valid_until_ns']=mapping.valid_until_ns if mapping else None
            if mapping and mapping.clock_domain!=t.native_clock_domain: state='TIMESTAMP_INVALID'
            if mapping and now>mapping.valid_until_ns: state='TIME_UNSYNCED'
            row['clock_state']=state
            row['time_valid']=bool(state=='TIME_VALID' and mapped==t.estimated_capture_time and uncertainty is not None and
                t.capture_time_uncertainty is not None and uncertainty<=t.capture_time_uncertainty<=p.max_time_uncertainty_ns)
            bundle=self.configurations.require(o)
            keys=bundle.calibration_bundle.get(source_id,[])
            row['calibration_valid']=all(any(self.calibrations.valid(key,kind=kind,asset_id=o.identity.asset_id or o.identity.serial_number,mount_revision=bundle.mounts.get(source_id)) for key in keys) for kind in p.required_calibrations)
            row['calibration_state']='VALID' if row['calibration_valid'] else 'MISSING_OR_INVALID'
            integrity_ok=not o.integrity.transport_error and not o.integrity.parse_error and o.integrity.check_result!='FAIL'
            uncertainty_known=bool(q.uncertainty) and q.uncertainty_origin is not None
            identity_ok=row['identity_verified'] if o.provenance.mode=='REAL' else o.provenance.mode in {'SIMULATION','REPLAY'}
            flags={'SOURCE_UNAVAILABLE':row['producing'],'IDENTITY_UNVERIFIED':identity_ok,'IMPLAUSIBLE':row['plausible'],
                   'NOT_CONNECTED':q.connection_state=='CONNECTED','HEALTH_UNQUALIFIED':q.health_state=='ONLINE' and q.fault_reason is None,
                   'TIME_UNQUALIFIED':row['time_valid'],'STALE_OR_AGE_UNKNOWN':row['fresh'],'CALIBRATION_UNQUALIFIED':row['calibration_valid'],
                   'INTEGRITY_FAILURE':integrity_ok,'UNCERTAINTY_UNAVAILABLE':uncertainty_known,'SOURCE_FAULT':not s['fault']}
            row['qualified']=all(flags.values())
            row['qualified_for']=[p.allowed_purpose] if row['qualified'] else []
            row['fault_reason']=next((reason for reason,ok in flags.items() if not ok),None)
            queue=self.queues[source_id]
            if len(queue)>1:
                dt=queue[-1].time.host_monotonic_arrival-queue[0].time.host_monotonic_arrival
                if dt>0: row['rate_hz']=(len(queue)-1)*1e9/dt
            return row

    def snapshot(self,now:int):
        with self._lock:
            rows=[self.readiness(source,now) for source in self.profiles]
            for row in rows:
                state=(row['producing'],row['fresh'],row['time_valid'],row['calibration_valid'],row['qualified'],row['fault_reason'])
                if self._last_states.get(row['source_id'])!=state:
                    self.timeline.append({'source_id':row['source_id'],'arrival_ns':now,'mode':row['mode'],
                        'event':'QUALIFICATION_CHANGED','clock_state':row['clock_state'],'calibration_state':row['calibration_state'],
                        'qualified':row['qualified'],'fault_reason':row['fault_reason']})
                    self._last_states[row['source_id']]=state
            modes={r['mode'] for r in rows if r['mode']!='UNAVAILABLE'}
            mode=next(iter(modes)) if len(modes)==1 else 'MIXED' if modes else 'UNAVAILABLE'
            return {'schema_version':'TARK_READINESS_1','profile_id':self.profile.profile_id,'host_epoch':self.host_epoch,
                    'source_mode':mode,'hardware_claim':'HARDWARE_UNVERIFIED','traction':'DISABLED_PHASE_1',
                    'timestamp_ns':now,'sources':rows,'timeline':deepcopy(list(self.timeline))}

    def record(self):
        with self._lock:
            return {'schema_version':'TARK_EVIDENCE_RECORD_1','host_epoch':self.host_epoch,'channel':self.channel,
                    'sessions':[{**s,'identity':s['identity'].model_dump(mode='json')} for s in self.sessions.values()],
                    'counters':deepcopy(self.counters),
                    'observations':[o.model_dump(mode='json') for o in self.latest.values()],
                    'clocks':self.clocks.snapshot(),'calibrations':self.calibrations.snapshot(),
                    'configurations':[b.model_dump(mode='json') for b in self.configurations.records.values()]}
