"""Phase-1 integrity regressions: fake clocks, memory databases, no devices."""
from contextlib import ExitStack
import asyncio
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.domain.models import RadarDetection, Freshness
from app.hardware.simulators import RadarSimulator
from app.main import DeploymentConfig, create_app
from app.services.pipeline import Pipeline, freshness
from app.services.system import TarkSystem
from runtime_fixtures import ControlledRuntime


BASE = Path(__file__).parents[2] / "config" / "phase1.json"
NOW = 10_000_000_000


def detection(timestamp=NOW):
    return RadarDetection(candidate_id=1, x_m=3, y_m=0, velocity_mps=-1,
                          quality=.9, uncertainty_m=.2, timestamp_ns=timestamp)


def settings():
    return Settings.from_file(BASE)


@pytest.fixture
def isolated(monkeypatch):
    for key in tuple(__import__('os').environ):
        if key.startswith('TARK_'):
            monkeypatch.delenv(key)
    monkeypatch.setenv('TARK_DATABASE_PATH', ':memory:')


def test_si01_queued_old_report_cannot_publish_normal(isolated):
    system = TarkSystem(settings().model_copy(update={'mode': 'real_radar'}))
    system.ld2450_capture = Mock()
    system.ld2450_capture.diagnostics.return_value = {
        'decoded_report_count': 1, 'state': 'ONLINE', 'rejected_frame_count': 0,
        'reason': 'FIXTURE', 'last_timestamp_ns': 1_000_000_000,
    }
    try:
        system.ingest_ld2450_report(1_000_000_000, [detection(1_000_000_000)])
        snapshot = system.tick(NOW)
        assert snapshot['decision']['state'] == 'UNKNOWN'
        assert snapshot['tracks'][0]['last_update_ns'] == 1_000_000_000
        assert snapshot['events'][-1]['timestamp_ns'] == NOW
    finally:
        system.close()


def test_si02_future_cannot_be_fresh():
    assert freshness(NOW + 1, NOW, 250, 1000) != Freshness.FRESH


def test_si03_rest_reads_do_not_advance_decisions(isolated):
    app = create_app(runtime_factory=ControlledRuntime())
    with TestClient(app) as client:
        before = app.state.system.pipeline.sequence
        for path in ('status', 'tracks', 'sensors', 'events'):
            assert client.get('/api/v1/' + path).status_code == 200
        assert app.state.system.pipeline.sequence == before


def test_si04_zero_deceleration_rejected():
    raw = settings().model_dump()
    raw['effective_deceleration_mps2']['value'] = 0
    with pytest.raises(ValidationError):
        Settings.model_validate(raw)


def test_si07_state_names_are_not_silent_aliases():
    # No executable state-scenario contract exists: unsupported names must not
    # silently become the default target fixture.
    with pytest.raises(ValueError):
        RadarSimulator('WARN')


def test_si09_public_recording_mutation_rejected(isolated):
    app = create_app(deployment=DeploymentConfig(environment='public_demo'))
    try:
        client = TestClient(app)
        assert client.post('/api/v1/recordings/start').status_code == 403
        assert client.post('/api/v1/recordings/stop').status_code == 403
        assert app.state.system.recording_sessions() == []
    finally:
        app.state.system.close()


@pytest.mark.parametrize('age_ns,health,state', [
    (0, 'FRESH', 'NORMAL'),
    (100_000_000, 'FRESH', 'NORMAL'),
    (250_000_000, 'FRESH', 'NORMAL'),
    (250_000_001, 'AGING', 'NORMAL'),
    (500_000_000, 'AGING', 'NORMAL'),
    (1_000_000_000, 'AGING', 'NORMAL'),
    (1_000_000_001, 'STALE', 'UNKNOWN'),
    (9_000_000_000, 'STALE', 'UNKNOWN'),
])
def test_freshness_final_time_boundaries(age_ns, health, state):
    pipeline = Pipeline(settings())
    result = pipeline.ingest([detection(NOW-age_ns)], NOW)
    assert pipeline.tracks['ld2450:1'].last_update_ns == NOW-age_ns
    assert pipeline.health(NOW).freshness == health
    assert result.state == state
    command = pipeline.command(result, NOW)
    assert command.permitted_speed_mps == command.left_command == command.right_command == 0


@pytest.mark.parametrize('offset', [1, 1_000_000_000, 10**18])
def test_future_report_rejected_without_upgrading_evidence(offset):
    pipeline = Pipeline(settings())
    pipeline.ingest([detection(NOW)], NOW)
    result = pipeline.ingest([detection(NOW+offset)], NOW)
    assert result.state == 'UNKNOWN'
    assert pipeline.health(NOW).reason == 'INVALID_OBSERVATION_TIMESTAMP'
    assert pipeline.tracks['ld2450:1'].last_update_ns == NOW


@pytest.mark.parametrize('stamp', [-1, True, 1.5])
def test_invalid_observation_timestamp_rejected(stamp):
    with pytest.raises(ValidationError):
        detection(stamp)
    pipeline = Pipeline(settings())
    pipeline.observe([], stamp, NOW)
    assert pipeline.decision(NOW).state == 'UNKNOWN'


def test_missing_now_zero_and_out_of_order_evidence():
    pipeline = Pipeline(settings())
    assert pipeline.decision(0).state == 'UNKNOWN'
    assert pipeline.ingest([detection(0)], 0).state == 'NORMAL'
    pipeline.ingest([detection(NOW)], NOW)
    pipeline.observe([detection(NOW-1)], NOW-1, NOW)
    assert pipeline.tracks['ld2450:1'].last_update_ns == NOW


def test_fresh_report_does_not_make_its_stale_detection_eligible():
    pipeline = Pipeline(settings())
    pipeline.observe([detection(NOW-1_000_000_001)], NOW, NOW)
    assert pipeline.health(NOW).freshness == 'FRESH'
    assert pipeline.decision(NOW).state != 'NORMAL'


@pytest.mark.parametrize('name', ['reaction_bound_s', 'margin_m', 'effective_deceleration_mps2', 'hard_cap_mps'])
@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf'), -1])
def test_invalid_numeric_configuration_rejected_before_start(name, value):
    raw = settings().model_dump()
    if name == 'hard_cap_mps': raw[name] = value
    else: raw[name]['value'] = value
    with pytest.raises(ValidationError):
        Settings.model_validate(raw)


def test_zero_is_valid_for_non_divisor_parameters():
    raw = settings().model_dump()
    for name in ('reaction_bound_s', 'margin_m'): raw[name]['value'] = 0
    raw['hard_cap_mps'] = 0
    assert Settings.model_validate(raw).margin_m.value == 0


@pytest.mark.parametrize('name', sorted(RadarSimulator.SCENARIOS))
def test_retained_scenario_input_and_actual_decision(name):
    pipeline = Pipeline(settings())
    observations = RadarSimulator(name).read_detections(NOW)
    result = pipeline.ingest(observations, NOW) if observations else pipeline.decision(NOW)
    assert result.state == ('UNKNOWN' if name in {'RADAR_LOSS', 'RADAR_STALE'} else 'NORMAL')
    if name == 'FAST_TARGET_APPROACH': assert observations[0].velocity_mps == -3
    if name == 'TARGET_RECEDING': assert observations[0].velocity_mps == 1
    if name == 'MULTI_TARGET': assert len(observations) == 2
    assert pipeline.command(result, NOW).left_command == 0


@pytest.mark.parametrize('name', ['NORMAL', 'WARN', 'RESTRICT', 'UNKNOWN', 'STOP', 'NOT_A_SCENARIO'])
def test_undefined_state_scenarios_fail_explicitly(name):
    with pytest.raises(ValueError, match='Unsupported'):
        RadarSimulator(name)


@pytest.mark.parametrize('name', ['RADAR_LOSS', 'RADAR_STALE'])
def test_loss_scenario_follows_actual_freshness(name):
    pipeline = Pipeline(settings())
    pipeline.ingest(RadarSimulator().read_detections(NOW), NOW)
    assert RadarSimulator(name).read_detections(NOW+1) == []
    assert pipeline.decision(NOW+250_000_001).state == 'NORMAL'
    assert pipeline.decision(NOW+1_000_000_001).state == 'UNKNOWN'


@pytest.mark.parametrize('observers', ['none', 'rest', 'repeated_rest', 'websocket', 'multiple_websockets', 'reconnect_storm'])
def test_observer_independence_and_zero_output_red_team(isolated, observers):
    controlled = ControlledRuntime()
    app = create_app(runtime_factory=controlled)
    with TestClient(app) as client:
        system = app.state.system
        tick = Mock(wraps=system.tick)
        system.tick = tick
        trace = []
        for index, delta in enumerate((250_000_000, 1_000_000_001, 250_000_000)):
            if index == 1: system.radar.active = False
            snapshot = client.portal.call(controlled.step, delta)
            before = (system.pipeline.sequence, len(system.pipeline.events), system._location_step)
            if observers in {'rest', 'repeated_rest'}:
                for _ in range(1 if observers == 'rest' else 20):
                    for path in ('status', 'tracks', 'sensors', 'events', 'vehicle-location'):
                        assert client.get('/api/v1/' + path).status_code == 200
            if observers in {'websocket', 'multiple_websockets', 'reconnect_storm'}:
                for _ in range(8 if observers == 'reconnect_storm' else 1):
                    with ExitStack() as stack:
                        sockets = [stack.enter_context(client.websocket_connect('/api/v1/ws')) for _ in range(3 if observers == 'multiple_websockets' else 1)]
                        for socket in sockets:
                            assert socket.receive_json()['payload']['command']['sequence'] == snapshot['command']['sequence']
                            assert socket.receive_json()['type'] == 'location_update'
            assert before == (system.pipeline.sequence, len(system.pipeline.events), system._location_step)
            assert len(system.persisted_events()) == before[0]
            assert snapshot['traction'] == 'DISABLED_PHASE_1'
            assert snapshot['command']['left_command'] == snapshot['command']['right_command'] == snapshot['decision']['permitted_speed_mps'] == 0
            assert snapshot['measurement_status'] == {'vehicle_speed': 'UNAVAILABLE', 'ttc': 'NOT_COMPUTED'}
            trace.append((snapshot['command']['sequence'], snapshot['decision']['state']))
        assert trace == [(2, 'NORMAL'), (3, 'UNKNOWN'), (4, 'UNKNOWN')]
        assert tick.call_count == 3
        detached = controlled.owner.latest()
        detached['decision']['state'] = 'STOP'
        assert controlled.owner.latest()['decision']['state'] == 'UNKNOWN'
        task = controlled.owner.task
    assert task.done() and controlled.owner.closed


def test_runtime_restart_duplicate_start_and_stale_cache(isolated):
    controlled = ControlledRuntime()
    app = create_app(runtime_factory=controlled)
    assert TestClient(app).get('/api/v1/status').status_code == 503
    tasks = []
    for _ in range(2):
        with TestClient(app) as client:
            tasks.append(controlled.owner.task)
            with pytest.raises(RuntimeError, match='already started'):
                client.portal.call(controlled.owner.start)
            assert client.get('/ready').status_code == 200
            with pytest.raises(RuntimeError, match='already started'):
                with TestClient(app):
                    pass
            assert client.get('/ready').status_code == 200
            controlled.now += 1_000_000_001
            assert client.get('/api/v1/status').status_code == 503
            assert client.get('/ready').status_code == 503
            assert client.get('/health').json()['status'] == 'unavailable'
        assert tasks[-1].done()
    assert tasks[0] is not tasks[1]


def test_publication_cannot_extend_normal_evidence_past_boundary(isolated):
    controlled = ControlledRuntime()
    controlled.now = NOW
    app = create_app(runtime_factory=controlled)
    app.state.system.radar.read_detections = Mock(return_value=[detection(NOW-1_000_000_000)])
    with TestClient(app) as client:
        assert client.get('/api/v1/status').json()['decision']['state'] == 'NORMAL'
        sequence = app.state.system.pipeline.sequence
        controlled.now += 1
        assert client.get('/api/v1/status').status_code == 503
        assert app.state.system.pipeline.sequence == sequence
        assert client.portal.call(controlled.step)['decision']['state'] == 'UNKNOWN'


def test_worker_failure_is_unavailable_and_not_suppressed(isolated):
    controlled = ControlledRuntime()
    app = create_app(runtime_factory=controlled)
    with pytest.raises(RuntimeError, match='fixture storage failure'):
        with TestClient(app) as client:
            app.state.system.tick = Mock(side_effect=RuntimeError('fixture storage failure'))
            async def fail_step():
                await controlled.queue.put(controlled.now+250_000_000)
                for _ in range(100):
                    await asyncio.sleep(0)
                    if controlled.owner.task.done(): return
                raise AssertionError('runtime did not fail')
            client.portal.call(fail_step)
            assert client.get('/api/v1/status').status_code == 503
            assert client.get('/ready').status_code == 503
    assert controlled.owner.closed


def test_queued_batch_creates_one_final_event_and_command(isolated):
    system = TarkSystem(settings().model_copy(update={'mode':'real_radar'}))
    system.ld2450_capture = Mock()
    system.ld2450_capture.diagnostics.return_value = {'decoded_report_count':2,'state':'ONLINE','rejected_frame_count':0,'reason':'FIXTURE','last_timestamp_ns':NOW}
    try:
        system.ingest_ld2450_report(NOW-9_000_000_000,[detection(NOW-9_000_000_000)])
        system.ingest_ld2450_report(NOW,[detection(NOW)])
        snapshot = system.tick(NOW)
        assert snapshot['decision']['state'] == 'NORMAL'
        assert snapshot['command']['sequence'] == len(system.pipeline.events) == len(system.persisted_events()) == 1
        system.ingest_ld2450_report(NOW+2,[detection(NOW+2)])
        assert system.tick(NOW+1)['decision']['state'] == 'UNKNOWN'
    finally:
        system.close()


@pytest.mark.parametrize('environment,auth', [('development','public_demo'), ('edge','authenticated')])
def test_non_public_recording_workflow_remains_authorized(isolated, environment, auth):
    app = create_app(deployment=DeploymentConfig(environment=environment, auth_mode=auth, access_token='fixture-token'), runtime_factory=ControlledRuntime())
    with TestClient(app) as client:
        if auth == 'authenticated':
            assert client.post('/api/v1/recordings/start').status_code == 401
            client.headers['Authorization'] = 'Bearer fixture-token'
        assert client.post('/api/v1/recordings/start').status_code == 200
        assert client.post('/api/v1/recordings/stop').status_code == 200
