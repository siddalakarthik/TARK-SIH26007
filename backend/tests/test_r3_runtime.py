from copy import deepcopy
import hashlib
from pathlib import Path
from unittest.mock import Mock
import pytest
from app.config import Settings
from app.services.system import TarkSystem
from app.r3.runtime import R3Runtime, r3_software_fingerprint
from app.r3.evidence import age_readiness
from app.r3.replay import recompute_evidence
from app.r3.experiments import Experiment, ExperimentStore
from app.r3.inference import *
from app.replay.engine import replay_recording
from test_r3_evidence import setup_channel, mutate, NOW

ROOT=Path(__file__).parents[2]

@pytest.fixture
def settings(monkeypatch,tmp_path):
    for key in list(__import__('os').environ):
        if key.startswith('TARK_'):monkeypatch.delenv(key)
    monkeypatch.setenv('TARK_DATABASE_PATH',str(tmp_path/'r3.db'))
    return Settings.from_file(ROOT/'config/phase1.json')

def r3_fixture(monkeypatch):
    monkeypatch.setenv('TARK_HARDWARE_PROFILE','R3_PI5_ADVISORY')
    monkeypatch.setenv('TARK_R3_FIXTURE_PATH',str(ROOT/'data/fixtures/r3_sources_v1.json'))

def test_default_is_legacy_without_fabricated_r3_data(settings):
    system=TarkSystem(settings)
    try:
        view=system.tick(NOW)['r3']
        assert view['active_profile']=='LEGACY_SMALL_SCALE' and view['source_mode']=='UNAVAILABLE'
        assert all(not s['producing'] and not s['qualified'] and not s['detected'] for s in view['sources'])
    finally:system.close()

def test_r3_fixture_lifecycle_no_motor_submission_and_replay(settings,monkeypatch):
    r3_fixture(monkeypatch);system=TarkSystem(settings)
    system.esp32_client.submit=Mock(side_effect=AssertionError('no R3 motor command'))
    try:
        session=system.start_recording(NOW)
        first=system.tick(NOW+10_000)
        second=system.tick(NOW+20_000)
        stopped=system.stop_recording(NOW+30_000)
        assert first['r3']['source_mode']=='SIMULATION' and len(first['r3']['sources'])==8
        assert all(not row['identity_verified'] and row['evidence_origin']=='SYNTHETIC_FIXTURE' for row in first['r3']['sources'])
        assert first['traction']=='DISABLED_PHASE_1' and first['command']['left_command']==first['command']['right_command']==0
        assert first['protocol']['submission']['reason']=='R3_ADVISORY_NO_COMMAND_SUBMISSION'
        records=system.recording_records(session['session_id'])
        assert replay_recording(records,settings,stopped).result=='MATCH'
        verified=recompute_evidence(records,stopped['metadata']['r3'],r3_software_fingerprint())
        assert verified['result']=='MATCH',verified
        assert verified['verified_ticks']==2 and verified['raw_inference_result']=='NOT RECOMPUTABLE'
        records[0]['payload']['r3_readiness']['sources'][0]['qualified']=True
        assert recompute_evidence(records,stopped['metadata']['r3'],r3_software_fingerprint())['result']=='MISMATCH'
        assert system.r3.channel.latest['radar-a'].provenance.mode=='SIMULATION'
        assert second['r3']['sources'][0]['counters']['accepted']==2
    finally:system.close()
    assert all(not s['running'] for s in system.r3.channel.sessions.values())

def test_r3_non_simulation_never_constructs_legacy_workers(settings,monkeypatch):
    monkeypatch.setenv('TARK_HARDWARE_PROFILE','R3_PI5_ADVISORY')
    for method in ('_start_configured_gnss','_start_configured_camera','_select_configured_esp32','_start_configured_ld2450_raw_capture','_start_configured_i2c_sensors'):
        monkeypatch.setattr(TarkSystem,method,Mock(side_effect=AssertionError('legacy device must not open')))
    system=TarkSystem(settings.model_copy(update={'mode':'real_radar'}))
    try:
        system.gnss_simulator.fix=Mock(side_effect=AssertionError('no GNSS simulation'))
        assert system.tick(NOW)['r3']['source_mode']=='UNAVAILABLE'
    finally:system.close()

def test_fixture_refused_outside_explicit_profile_and_simulation(settings,monkeypatch,tmp_path):
    monkeypatch.setenv('TARK_R3_FIXTURE_PATH',str(ROOT/'data/fixtures/r3_sources_v1.json'))
    with pytest.raises(ValueError): R3Runtime(settings,tmp_path/'a.db')
    with pytest.raises(ValueError): R3Runtime(settings.model_copy(update={'mode':'real_radar'}),tmp_path/'b.db',active_profile='R3_PI5_ADVISORY')

@pytest.mark.parametrize('field,value',[('health_state','FAILED'),('health_state','UNKNOWN'),('production_state','FAILED'),('connection_state','NOT_CONNECTED'),('fault_reason','CORRECTION_LOST')])
def test_health_flags_do_not_become_qualified(field,value):
    channel,f=setup_channel();channel.accept(mutate(f(),['qualification',field],value),NOW+2000)
    assert not channel.readiness('gnss-base',NOW+2000)['qualified']

def test_replay_missing_software_configuration_or_corrupt_records(settings,monkeypatch):
    r3_fixture(monkeypatch);system=TarkSystem(settings)
    try:
        session=system.start_recording(NOW);system.tick(NOW+1);stopped=system.stop_recording(NOW+2)
        records=system.recording_records(session['session_id']);metadata=stopped['metadata']['r3']
        assert recompute_evidence(records,metadata,'wrong')['reason']=='SOFTWARE_VERSION_UNAVAILABLE'
        bad=deepcopy(metadata);bad['configuration']['network_profile']='changed'
        assert recompute_evidence(records,bad,r3_software_fingerprint())['reason']=='CONFIGURATION_DIFFERENCE'
        records[0]['payload']['r3_evidence']['observations'][0]['time']['publication_time']=NOW+999
        assert recompute_evidence(records,metadata,r3_software_fingerprint())['result']=='NOT RECOMPUTABLE'
    finally:system.close()

def experiment(runtime):
    return Experiment(experiment_id='exp-1',title='Synthetic qualification',scenario='BLIND_CURVE_FIXTURE',operator='Test',date='2026-10-04',
        hardware_profile=runtime.profile.profile_id,configuration_bundle=runtime.bundle.bundle_id,calibration_bundle=[],software_version=runtime.bundle.software_version,
        expected_sources=['gnss-b'],visibility_condition='SYNTHETIC_NOT_MEASURED',notes='No physical evidence')

def test_experiment_record_attach_single_session_and_restart(settings,monkeypatch):
    r3_fixture(monkeypatch);system=TarkSystem(settings)
    system.r3.experiments.start(experiment(system.r3));session=system.start_recording(NOW)
    assert system.r3.experiments.current()['recording_id']==session['session_id']
    system.tick(NOW+1);system.stop_recording(NOW+2)
    with pytest.raises(ValueError,match='One recording'):system.start_recording(NOW+3)
    system.close()
    import os
    store=ExperimentStore(Path(os.environ['TARK_DATABASE_PATH']))
    assert store.list()[0]['status']=='INTERRUPTED' and store.current() is None;store.close()

def test_inference_fixture_provenance_latency_and_bounds():
    clock=iter([100,130,200,260]).__next__
    provider=FixtureInferenceProvider({'f':[{'label':'fixture','confidence':.8,'xyxy_normalized':[0.,0.,1.,1.]}]},
        model_name='fixture',model_version='1',model_sha256='0'*64,postprocessing_version='1',clock=clock)
    with pytest.raises(ValueError):provider.infer('f','f',source_mode='REAL')
    result=provider.infer('f','f',source_mode='SIMULATION',capture_time_ns=90,capture_uncertainty_ns=5)
    assert result.latency_ns==30 and result.input_frame_id=='f' and result.source_mode=='SIMULATION'
    provider.infer('f','f',source_mode='REPLAY')
    assert provider.metrics()['p95_latency_ns']==60
    provider.busy.acquire()
    with pytest.raises(RuntimeError,match='BUSY'):provider.infer('f','f',source_mode='SIMULATION')
    provider.busy.release();assert provider.metrics()['dropped_frames']==1

def test_hailo_binding_checks_model_and_calls_owned_sdk_only(tmp_path):
    # Test-generated model file, no real accelerator or proprietary model.
    path=tmp_path/'fixture.hef';path.write_bytes(b'SYNTHETIC MODEL HASH TEST')
    sdk=Mock();sdk.infer.return_value=[]
    provider=HailoProvider.bind(path,hashlib.sha256(path.read_bytes()).hexdigest(),model_name='fixture',model_version='1',postprocessing_version='test',
        infer_vstreams=sdk,input_name='input',preprocess=lambda x:x,postprocess=lambda x:x)
    assert provider.infer('f',b'frame',source_mode='SIMULATION').detections==[]
    sdk.infer.assert_called_once_with({'input':b'frame'})
    with pytest.raises(ValueError):HailoProvider.bind(path,'0'*64,model_name='fixture',model_version='1',postprocessing_version='test',
        infer_vstreams=sdk,input_name='input',preprocess=lambda x:x,postprocess=lambda x:x)

def test_r3_api_experiment_recording_replay_and_no_authority(settings,monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import create_app,DeploymentConfig
    from runtime_fixtures import ControlledRuntime
    r3_fixture(monkeypatch); clock=ControlledRuntime();app=create_app(settings,DeploymentConfig(),runtime_factory=clock)
    with TestClient(app) as client:
        view=client.get('/api/v2/r3/readiness').json()
        assert view['source_mode']=='SIMULATION' and view['explanation']['motion_authority'] is False
        item=experiment(app.state.system.r3).model_dump(mode='json')
        assert client.post('/api/v2/r3/experiments',json=item).status_code==200
        session=client.post('/api/v1/recordings/start').json()
        assert client.post('/api/v2/r3/experiments/finish').status_code==409
        client.portal.call(clock.step)
        assert client.post('/api/v1/recordings/stop').status_code==200
        verified=client.post(f"/api/v1/replay/sessions/{session['session_id']}/verify").json()
        assert verified['result']=='MATCH' and verified['r3_evidence']['result']=='MATCH'
        assert verified['r3_advisory']['result']=='MATCH', verified['r3_advisory']
        assert client.get('/api/v2/r3/advisory').json()['advisory']['traction']=='DISABLED_PHASE_1'
        timeline=client.get(f"/api/v1/replay/sessions/{session['session_id']}/timeline").json()
        assert timeline['items'][0]['r3_advisory']['state']=='UNKNOWN'
        finished=client.post('/api/v2/r3/experiments/finish')
        assert finished.status_code==200,finished.text
        assert finished.json()['summary']['replay_result']['result']=='MATCH'
        assert len(client.get('/api/v2/r3/experiments').json())==1
        assert client.post('/api/v2/r3/observations',json={}).status_code in {404,405}

def test_r3_public_demo_write_rejected(settings,monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import create_app,DeploymentConfig
    from runtime_fixtures import ControlledRuntime
    app=create_app(settings,DeploymentConfig(environment='public_demo'),runtime_factory=ControlledRuntime())
    with TestClient(app) as client:
        assert client.post('/api/v2/r3/experiments',json=experiment(app.state.system.r3).model_dump(mode='json')).status_code==403
        assert client.post('/api/v2/r3/experiments/finish').status_code==403
        assert client.get('/api/v2/r3/readiness').status_code==200

def test_readiness_publication_expires_without_refresh_or_record_mutation(settings,monkeypatch):
    r3_fixture(monkeypatch);system=TarkSystem(settings)
    try:
        snapshot=system.tick(NOW);original=deepcopy(snapshot)
        row=next(x for x in snapshot['r3']['sources'] if x['source_id']=='gnss-base')
        assert row['qualified']
        aged=age_readiness(snapshot['r3'],NOW+row['max_age_ns']+1)
        expired=next(x for x in aged['sources'] if x['source_id']=='gnss-base')
        assert not expired['qualified'] and not expired['fresh'] and expired['qualified_for']==[]
        assert expired['age_bound_ns']==row['age_bound_ns']+row['max_age_ns']+1
        assert snapshot==original
        assert system.r3.channel.counters['gnss-base']['accepted']==1
        from app.services.runtime import RuntimeOwner
        runtime=RuntimeOwner(system,clock=lambda:NOW+201_000_000)
        runtime._snapshot=snapshot;runtime.task=Mock();runtime.task.done.return_value=False
        # Actual REST/WebSocket publication boundary uses the projection and
        # does not tick the system or mutate its recording checkpoint.
        published=runtime.latest()
        radar=next(x for x in published['r3']['sources'] if x['source_id']=='radar-a')
        assert not radar['fresh'] and not radar['producing']
        assert published['decision']==snapshot['decision'] and published['command']==snapshot['command']
        assert runtime._snapshot==original
        reset=age_readiness(snapshot['r3'],NOW-1)
        assert all(not x['qualified'] and x['clock_state']=='CLOCK_RESET' for x in reset['sources'])
    finally:system.close()

def test_readiness_publication_honors_clock_deadline(settings,monkeypatch):
    r3_fixture(monkeypatch);system=TarkSystem(settings)
    try:
        view=system.tick(NOW)['r3'];row=next(x for x in view['sources'] if x['source_id']=='gnss-base')
        row['clock_valid_until_ns']=NOW+5
        aged=age_readiness(view,NOW+6)
        expired=next(x for x in aged['sources'] if x['source_id']=='gnss-base')
        assert expired['fresh'] and not expired['time_valid'] and not expired['qualified']
        assert expired['fault_reason']=='TIME_UNQUALIFIED'
    finally:system.close()
