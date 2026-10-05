from copy import deepcopy
import json
from pathlib import Path
import pytest
from app.config import Settings
from app.domain.models import RadarDetection
from app.replay.engine import ReplayFormatError, ReplayConfigurationError, replay_recording, replay_timeline, recording_metadata
from app.services.system import TarkSystem

SETTINGS = Settings.from_file(Path(__file__).parents[2]/"config/phase1.json")

class Capture:
    def close(self): pass
    def diagnostics(self):
        return dict(decoded_report_count=1,state="ONLINE",reason="TEST_FIXTURE",last_timestamp_ns=1,rejected_frame_count=0)

@pytest.fixture
def system(monkeypatch):
    for name in tuple(__import__('os').environ):
        if name.startswith('TARK_'): monkeypatch.delenv(name)
    monkeypatch.setenv('TARK_DATABASE_PATH', ':memory:')
    s=TarkSystem(SETTINGS.model_copy(update={'mode':'real_radar'}))
    s.ld2450_capture=Capture()
    yield s
    s.close()

def target(t, number=1, distance=3):
    return RadarDetection(candidate_id=number,x_m=0,y_m=distance,velocity_mps=-1,quality=.9,uncertainty_m=.2,timestamp_ns=t)

def recorded(system, scenario):
    if scenario=='mid_run':
        system.ingest_ld2450_report(1_000_000_000,[target(1_000_000_000)])
        system.tick(1_000_000_000)
    system.start_recording(1)
    if scenario in {'empty','missing','mixed','future','same_time','stale'}:
        system.ingest_ld2450_report(1_000_000_000,[target(1_000_000_000)])
        system.tick(1_000_000_000)
        if scenario!='missing':
            system.ingest_ld2450_report(2_100_000_000,[])
        system.tick(2_100_000_000)
        if scenario=='mixed':
            system.tick(2_200_000_000)
            system.ingest_ld2450_report(2_300_000_000,[target(2_300_000_000,2,.4)])
            system.tick(2_300_000_000)
        if scenario=='future':
            system.ingest_ld2450_report(3_000_000_001,[target(3_000_000_001)])
            system.tick(3_000_000_000)
        if scenario=='same_time':
            system.ingest_ld2450_report(2_100_000_000,[])
            system.tick(2_100_000_000)
        if scenario=='stale': system.tick(9_000_000_000)
    elif scenario=='batch':
        system.ingest_ld2450_report(1_000_000_000,[target(1_000_000_000,1,.4)])
        system.ingest_ld2450_report(1_010_000_000,[target(1_010_000_000,2,3)])
        system.tick(1_100_000_000)
    else: system.tick(1_200_000_000)
    session=system.stop_recording(10_000_000_000)
    return session,system.recording_records(session['session_id'])

@pytest.mark.parametrize('scenario',['empty','missing','batch','mid_run','mixed','future','same_time','stale','initial'])
def test_semantics_reconstruct_actual_runtime(system,scenario,monkeypatch):
    session,records=recorded(system,scenario)
    live_sequence=system.pipeline.sequence
    # Offline replay must not call either the live tick or a transport.
    def forbidden(*args,**kwargs): raise AssertionError('replay invoked live authority')
    monkeypatch.setattr(system,'tick',forbidden)
    monkeypatch.setattr(system.esp32_client,'submit',forbidden)
    result=replay_recording(iter(records),system.settings,session)
    assert result.result=='MATCH' and result.verified_records==session['record_count']
    assert system.pipeline.sequence==live_sequence
    assert all(d['permitted_speed_mps']==0 for d in result.decisions)
    if scenario=='batch': assert len(records[0]['payload']['observations'])==2
    if scenario=='empty': assert records[-1]['payload']['observations'][0]['detections']==[]
    if scenario=='missing': assert records[-1]['payload']['observations']==[]
    timeline=replay_timeline(iter(records),session,system.settings)
    assert timeline['complete'] and timeline['source_mode']=='REPLAY'

@pytest.mark.parametrize('mutation',['software','config','format','missing_header','missing_checkpoint','source','checkpoint_nan','duplicate_track'])
def test_identity_and_checkpoint_rejected(system,mutation):
    session,records=recorded(system,'mid_run')
    changed=deepcopy(session)
    if mutation=='software':changed['metadata']['software_id']='other'
    elif mutation=='config':changed['metadata']['configuration_fingerprint']='other'
    elif mutation=='format':changed['metadata']['format_version']=999
    elif mutation=='missing_header':changed['metadata']=None
    elif mutation=='missing_checkpoint':changed['metadata'].pop('checkpoint')
    elif mutation=='source':changed['metadata']['source_mode']='SIMULATION'
    elif mutation=='checkpoint_nan':changed['metadata']['checkpoint']['tracks'][0]['x_m']=float('nan')
    else:changed['metadata']['checkpoint']['tracks']*=2
    with pytest.raises(ReplayFormatError):replay_recording(records,system.settings,changed)

@pytest.mark.parametrize('mutation',['duplicate','missing','reverse','invalid_order','wrong_kind','missing_decision','nan','source'])
def test_corrupt_records_are_explicit_failure(system,mutation):
    session,records=recorded(system,'mixed')
    if mutation=='duplicate':records[1]['sequence']=1
    elif mutation=='missing':records.pop()
    elif mutation=='reverse':records.reverse()
    elif mutation=='invalid_order':records[0]['payload']['observations'][0]['order']=1
    elif mutation=='wrong_kind':records[0]['kind']='invented'
    elif mutation=='missing_decision':records[0]['payload']['decision']={}
    elif mutation=='nan':records[0]['payload']['decision']['D_env_m']=float('nan')
    else:records[0]['source_mode']='SIMULATION'
    with pytest.raises(ReplayFormatError):replay_recording(records,system.settings,session)

def test_actual_configuration_values_not_only_label(system):
    session,records=recorded(system,'empty')
    changed=system.settings.model_copy(update={'fresh_age_ms':251})
    assert changed.configuration_hash==system.settings.configuration_hash
    with pytest.raises(ReplayConfigurationError,match='configuration values'):
        replay_recording(records,changed,session)

def test_full_session_beyond_10000_last_mismatch_found_and_memory_bounded(system,monkeypatch):
    # Generate deterministic evidence using the production pipeline; insert in
    # one test transaction, avoiding 10,001 per-record disk commits.
    store=system.recording_store
    session=store.start(timestamp_ns=0,source_mode='REAL_RADAR',configuration_hash=system.settings.configuration_hash,
                        max_records=20000,metadata=recording_metadata(system.pipeline))
    rows=[]
    for i in range(1,10002):
        decision=system.pipeline.decision(i)
        command=system.pipeline.command(decision,i)
        payload={'schema_version':2,'observations':[], 'decision':decision.model_dump(mode='json'),
                 'radar_health':system.pipeline.health(i).model_dump(mode='json'),
                 'command':command.model_dump(mode='json'),'event':system.pipeline.events[-1].model_dump(mode='json')}
        if i==10001:payload['decision']['D_env_m']=99
        rows.append((session['session_id'],i,i,'REAL_RADAR','OBSERVATION_TICK_V2',json.dumps(payload)))
    store.db.executemany('INSERT INTO recording_records VALUES (?,?,?,?,?,?)',rows)
    store.db.execute('UPDATE recording_sessions SET record_count=10001 WHERE id=?',(session['session_id'],));store.db.commit()
    session=store.stop(timestamp_ns=10002)
    result=replay_recording(store.iter_records(session['session_id']),system.settings,session)
    assert result.result=='MISMATCH' and result.first_divergence==10000
    assert result.verified_records==10001 and result.verified_decisions==10001
    assert result.first_sequence==1 and result.last_sequence==10001 and len(result.decisions)==100
    import app.main as main
    monkeypatch.setattr(main,'TarkSystem',lambda settings:system)
    app=main.create_app(settings=system.settings)
    verify=next(route.endpoint for route in app.routes if route.path=='/api/v1/replay/sessions/{session_id}/verify')
    response=verify(session['session_id'])
    assert response['result']=='MISMATCH' and response['first_divergence']==10000
    assert response['complete'] and response['verified_records']==response['total_records']==10001
    assert len(response['replayed_decisions'])==response['decisions_preview_limit']==100

def test_legacy_never_claims_deterministic_match(system):
    session,records=recorded(system,'empty')
    session['metadata']=None
    with pytest.raises(ReplayConfigurationError,match='LEGACY_NONDETERMINISTIC'):
        replay_recording(records,system.settings,session)

def test_real_source_recording_replays_offline_without_hardware_mode(system):
    session,records=recorded(system,'mixed')
    assert session['source_mode']=='REAL_RADAR'
    assert replay_recording(records,SETTINGS,session).result=='MATCH'

def test_altered_input_is_a_mismatch_not_a_false_match(system):
    session,records=recorded(system,'mixed')
    records[0]['payload']['observations'][0]['detections'][0]['y_m']=.3
    result=replay_recording(records,system.settings,session)
    assert result.result=='MISMATCH' and result.first_divergence==0

def test_corrupt_metadata_and_payload_produce_api_errors_not_server_crash(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import create_app
    from runtime_fixtures import ControlledRuntime
    monkeypatch.setenv('TARK_DATABASE_PATH',':memory:')
    app=create_app(runtime_factory=ControlledRuntime())
    with TestClient(app) as client:
        session=client.post('/api/v1/recordings/start').json()
        client.post('/api/v1/recordings/stop')
        app.state.system.recording_store.db.execute('UPDATE recording_sessions SET metadata=? WHERE id=?',('not-json',session['session_id']))
        app.state.system.recording_store.db.commit()
        for path in ('/api/v1/runs','/api/v1/replay/sessions',f'/api/v1/replay/sessions/{session["session_id"]}/timeline'):
            assert client.get(path).status_code==409
        assert client.get('/health').status_code==200
