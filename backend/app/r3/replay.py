"""Isolated evidence qualification recomputation; never attaches to live runtime.

This is NOT raw-media inference replay. Its scope is explicit in every result.
Existing legacy decision MATCH remains a separate comparison.
"""
from app.r3.contracts import HardwareProfile, Identity, Observation, digest
from app.r3.registry import ClockMapping, Calibration, ConfigurationBundle
from app.r3.evidence import EvidenceChannel
from app.r3.reasoning import R3Reasoner
from app.r3.reasoning_models import ReasoningConfig, Environment, R3Decision
import time

FIELDS=('source_id','producing','identity_verified','fresh','plausible','time_valid',
        'calibration_valid','qualified','qualified_for','mode','clock_state',
        'calibration_state','fault_reason','age_bound_ns','arrival_age_ns')


def advisory_preview(payload):
    saved=payload.get('r3_readiness',{}).get('advisory')
    if saved is None:return None
    try:
        value=R3Decision.model_validate(saved)
        return {key:getattr(value,key) for key in ('state','limiting_reason','source_mode')}
    except (ValueError,TypeError):
        return {'state':'UNAVAILABLE','limiting_reason':'CORRUPT_R3_ADVISORY','source_mode':'UNKNOWN'}


def restore_channel(data,profile,bundle,timestamp_ns):
    """One isolated reconstruction boundary shared by both comparisons."""
    if data.get('schema_version')!='TARK_EVIDENCE_RECORD_1':raise ValueError('INCOMPATIBLE_EVIDENCE')
    channel=EvidenceChannel(profile,data['host_epoch'],channel='RECOMPUTATION')
    for key,limit in [('configurations',64),('clocks',256),('sessions',32),('observations',32)]:
        if len(data[key])>limit:raise ValueError('RECORD_LIMIT')
    if len(data['calibrations']['records'])>256 or len(data['calibrations']['invalid'])>256:raise ValueError('RECORD_LIMIT')
    for value in data['configurations']:channel.configurations.register(ConfigurationBundle.model_validate(value))
    if channel.configurations.records.get(bundle.bundle_id)!=bundle:raise ValueError('CONFIGURATION_DIFFERENCE')
    for value in data['clocks']:channel.clocks.register(ClockMapping.model_validate(value))
    for value in data['calibrations']['records']:channel.calibrations.register(Calibration.model_validate(value))
    for key,reason in data['calibrations']['invalid'].items():channel.calibrations.invalidate(key,reason)
    sessions={}
    for value in data['sessions']:
        identity=Identity.model_validate(value['identity']);source=identity.source_id
        if source in sessions:raise ValueError('DUPLICATED_SOURCE_SESSION')
        sessions[source]=value
        channel.begin_source(identity,value['mode'],detected=value['detected'],identity_verified=value['identity_verified'])
    for value in data['observations']:
        observation=Observation.model_validate(value)
        if observation.identity.source_id in channel.latest:raise ValueError('DUPLICATED_OBSERVATION')
        if not channel.accept(observation,timestamp_ns):raise ValueError('INVALID_RECORDED_OBSERVATION')
    for source,value in sessions.items():
        if not value['running']:channel.stop_source(source,value['fault'] or 'NOT_CONNECTED')
        channel.sessions[source]['fault']=value['fault']
    return channel


def checked_metadata(metadata,software_fingerprint):
    if not isinstance(metadata,dict) or metadata.get('version')!='TARK_R3_PROVENANCE_1':raise ValueError('MISSING_R3_PROVENANCE')
    if metadata.get('software_fingerprint')!=software_fingerprint:raise ValueError('SOFTWARE_VERSION_UNAVAILABLE')
    profile=HardwareProfile.model_validate(metadata['profile'])
    if digest(profile.model_dump(mode='json'))!=metadata['profile_hash']:raise ValueError('PROFILE_DIFFERENCE')
    bundle=ConfigurationBundle.model_validate(metadata['configuration'])
    if bundle.content_hash!=metadata['configuration_hash']:raise ValueError('CONFIGURATION_DIFFERENCE')
    return profile,bundle


def recompute_advisory(records,metadata,software_fingerprint):
    result={'result':'NOT RECOMPUTABLE','scope':'R3_ADVISORY','reason':None,'verified_ticks':0,
            'first_divergence':None,'view_mode':'REPLAY','hardware_verified':False}
    start=time.perf_counter_ns()
    try:
        profile,bundle=checked_metadata(metadata,software_fingerprint)
        config=ReasoningConfig.model_validate(metadata['reasoning']['configuration'])
        if config.content_hash!=metadata['reasoning']['configuration_hash']:raise ValueError('REASONING_CONFIGURATION_DIFFERENCE')
        engine=R3Reasoner(config,software_fingerprint);engine.restore(metadata['reasoning']['checkpoint'])
        previous_time=-1;previous_sequence=-1
        for index,record in enumerate(records):
            if index>=50_000:raise ValueError('RECORD_LIMIT')
            if record['kind']=='RAW_FRAME_V1':continue
            if record['kind']!='OBSERVATION_TICK_V2':raise ValueError('INCOMPATIBLE_RECORD')
            if record['timestamp_ns']<previous_time or record['sequence']<=previous_sequence:raise ValueError('RECORD_ORDER')
            previous_time=record['timestamp_ns'];previous_sequence=record['sequence']
            payload=record['payload'];data=payload['r3_evidence']
            saved=R3Decision.model_validate(payload['r3_readiness']['advisory']).model_dump(mode='json')
            channel=restore_channel(data,profile,bundle,record['timestamp_ns'])
            environment=Environment.model_validate(data['reasoning_environment'])
            actual=engine.step(channel,record['timestamp_ns'],environment)
            if actual!=saved:
                result.update(result='MISMATCH',reason='R3_DECISION_DIFFERS',first_divergence=record['sequence']);break
            result['verified_ticks']+=1
        else:
            if not result['verified_ticks']:raise ValueError('NO_ADVISORY_TICKS')
            result.update(result='MATCH',reason='Normalized evidence reproduces the recorded R3 advisory; not raw inference or physical validation.')
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as error:
        result.update(result='NOT RECOMPUTABLE',reason=str(error)[:256])
    result['computation_ns']=time.perf_counter_ns()-start
    return result

def experiment_summary(records):
    """Recorded counts only. No fleet productivity or physical KPI inference."""
    sources=set();faults={};modes={};transitions=0;warnings=0;ticks=0;first={};last={}
    for record in records:
        if ticks>=50_000:raise ValueError('RECORD_LIMIT')
        if record['kind']!='OBSERVATION_TICK_V2':continue
        ticks+=1;rows=record['payload'].get('r3_readiness',{}).get('sources',[])
        warning=False
        for row in rows:
            source=row['source_id'];mode=row['mode']
            if row['producing']:sources.add(source)
            if source in modes and modes[source]!=mode:transitions+=1
            modes[source]=mode
            first.setdefault(source,row['counters'].get('drops',0));last[source]=row['counters'].get('drops',0)
            if row['fault_reason']:
                key=source+':'+row['fault_reason'];faults[key]=faults.get(key,0)+1;warning=True
        warnings+=int(warning)
    return {'recorded_ticks':ticks,'sources_present':sorted(sources),'fault_tick_counts':faults,
            'warning_ticks':warnings,'mode_transitions':transitions,
            'observed_drop_counter_increase':sum(max(0,last[s]-first[s]) for s in first)}

def recompute_evidence(records,metadata,software_fingerprint):
    result={'result':'NOT RECOMPUTABLE','scope':'R3_NORMALIZED_EVIDENCE_QUALIFICATION',
            'reason':None,'verified_ticks':0,'first_divergence':None,'view_mode':'REPLAY',
            'raw_inference_result':'NOT RECOMPUTABLE',
            'raw_inference_reason':'No released model/raw-media reconstruction pipeline is claimed.',
            'hardware_verified':False}
    try:
        profile,bundle=checked_metadata(metadata,software_fingerprint)
        for index,record in enumerate(records):
            if index>=50_000: raise ValueError('RECORD_LIMIT')
            if record['kind']=='RAW_FRAME_V1': continue
            payload=record['payload']; data=payload.get('r3_evidence'); saved=payload.get('r3_readiness')
            if not isinstance(data,dict) or not isinstance(saved,dict): raise ValueError('MISSING_NORMALIZED_EVIDENCE')
            channel=restore_channel(data,profile,bundle,record['timestamp_ns'])
            actual=channel.snapshot(record['timestamp_ns'])['sources']
            if len(saved['sources'])!=len(actual): raise ValueError('CORRUPT_READINESS')
            expected=[{k:row[k] for k in FIELDS} for row in saved['sources']]
            computed=[{k:row[k] for k in FIELDS} for row in actual]
            if computed!=expected:
                result.update(result='MISMATCH',reason='QUALIFICATION_DIFFERS',first_divergence=record['sequence']);return result
            result['verified_ticks']+=1
        if not result['verified_ticks']: raise ValueError('NO_EVIDENCE_TICKS')
        result.update(result='MATCH',reason='Recorded normalized evidence reproduces qualification; not physical validation.')
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as error:
        result.update(result='NOT RECOMPUTABLE',reason=str(error)[:256])
    return result
