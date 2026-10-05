from copy import deepcopy
import json
import pytest
from app.replay.store import RecordingStore
from app.r3.contracts import digest
from app.r3.replay import recompute_advisory
from app.r3.sih_demos import DEMOS, run_demo


@pytest.fixture(scope='module')
def demos(tmp_path_factory):
    root = tmp_path_factory.mktemp('sih')
    return {name: (root / name, run_demo(name, root / name)) for name in DEMOS}


@pytest.mark.parametrize('name', list(DEMOS))
def test_persisted_replay_and_authority(demos, name):
    path, summary = demos[name]
    assert summary['passed'] and summary['replay_isolated']
    assert summary['replay']['result'] == summary['qualification_replay']['result'] == 'MATCH'
    assert summary['replay']['verified_ticks'] == summary['ticks']
    assert summary['raw_media_replay'].startswith('NOT RECOMPUTABLE')
    store = RecordingStore(path / 'recording.db')
    try:
        session, = store.list()
        assert session['status'] == 'COMPLETE'
        assert session['record_count'] == summary['ticks']
        assert list(store.iter_records(session['session_id'])) == json.loads((path / 'records.json').read_text())
    finally:
        store.close()
    for row in summary['rows']:
        assert row['source_mode'] == 'SIMULATION'
        assert row['traction'] == 'DISABLED_PHASE_1'
        assert not row['motion_authority'] and not row['hardware_verified']
        assert not row['observability']['road_clear_claim']
    assert 'SIMULATION / SYNTHETIC EVIDENCE' in (path / 'presentation.svg').read_text()


def test_degradation_and_distinct_sustained_recovery(demos):
    _, summary = demos['degraded-visibility']
    rows = summary['rows']
    ends = [next(r for r in rows if r['sequence'] == s['sequence']) for s in summary['stages']]
    assert [r['state'] for r in ends] == ['NORMAL', 'RESTRICT', 'UNKNOWN', 'NORMAL']
    assert ends[1]['qualified_range_m'] < ends[0]['qualified_range_m']
    assert ends[1]['advised_speed_mps'] < ends[0]['advised_speed_mps']
    assert 'radar-a' in ends[1]['observability']['modality_support']
    assert ends[1]['source_coverage_contributions']['radar-a']['forward_range_m'] == ends[0]['source_coverage_contributions']['radar-a']['forward_range_m']
    assert ends[1]['source_coverage_contributions']['rgb-a']['forward_range_m'] < ends[0]['source_coverage_contributions']['rgb-a']['forward_range_m']
    assert ends[2]['qualified_range_m'] is None and ends[2]['advised_speed_mps'] is None
    restored = [r for r in rows if r['stage'] == 'D_SUSTAINED_RECOVERY']
    assert restored[0]['state'] == 'UNKNOWN' and restored[0]['reason'] == 'RECOVERY_PENDING'
    first_normal = next(r for r in restored if r['state'] == 'NORMAL')
    assert first_normal['timestamp_ns'] - restored[0]['timestamp_ns'] >= 500_000_000
    assert len({r['sequence'] for r in restored}) == len(restored)


def test_collision_corridor_motion_and_why(demos):
    _, summary = demos['collision-risk']
    rows = summary['rows']
    target_rows = [r for r in rows if r['tracks']]
    assert target_rows[0]['tracks'][0]['lifecycle'] == 'NEW'
    assert target_rows[1]['tracks'][0]['lifecycle'] == 'CONFIRMED'
    assert target_rows[0]['tracks'][0]['relevance'] == 'IRRELEVANT'
    assert any(r['tracks'][0]['relevance'] == 'RELEVANT' for r in target_rows)
    assert target_rows[0]['ttc'][0]['value_s'] is None
    valid = next(r for r in target_rows if r['ttc'][0]['valid'])
    track = valid['tracks'][0]
    assert track['velocity_method'] == 'TWO_POSITION_FIXED_BODY_AXES_RESEARCH'
    assert track['radial_velocity_mps'] == 0. and track['relative_velocity_mps'][0] == pytest.approx(-1.)
    assert len(valid['ttc'][0]['input_evidence']) == 2
    restricted = [r for r in rows if r['state'] == 'RESTRICT']
    assert restricted[-1]['advised_speed_mps'] < restricted[0]['advised_speed_mps']
    last = rows[-1]
    assert last['state'] == 'STOP' and last['reason'] == 'STOPPING_REQUIREMENT_NOT_MET'
    assert last['hazards'][0]['range_lower_bound_m'] < last['required_range_m']
    assert last['tracks'][0]['track_id'] in last['why']['track_ids']
    assert set(last['hazards'][0]['evidence_ids']).intersection(last['why']['supporting_evidence'])


def test_peer_conflict_is_not_local_sensing_and_expiry(demos):
    path, summary = demos['blind-curve']
    assert [s['observed'] for s in summary['stages']] == ['NORMAL', 'RESTRICT', 'UNKNOWN']
    for row in summary['rows']:
        assert row['tracks'] == [] and row['hazards'] == []
    fresh = [r for r in summary['rows'] if r['stage'] == 'B_FRESH_PEER_CONFLICT'][-1]
    assert fresh['cooperative_context'] and fresh['reason'] == 'COOPERATIVE_CONFLICT'
    assert summary['rows'][-1]['cooperative_context'] == []
    assert summary['rows'][-1]['advised_speed_mps'] is None
    records = json.loads((path / 'records.json').read_text())
    b = next(o for o in records[10]['payload']['r3_evidence']['observations'] if o['identity']['source_id'] == 'gnss-b')
    assert b['identity']['node_id'] == 'B' and b['identity']['session_id']
    assert b['integrity']['sequence_number'] > 0
    assert b['time']['estimated_capture_time'] > 0
    assert b['measurement']['payload']['fix_type'] == 'RTK_FIXED'
    assert b['measurement']['payload']['horizontal_uncertainty_m'] > 0
    assert b['measurement']['payload']['correction_age_s'] == 0.
    assert b['provenance']['mode'] == 'SIMULATION'


def test_repeatable_decisions_and_preserve_existing_outputs(demos, tmp_path):
    path, summary = demos['collision-risk']
    second = run_demo('collision-risk', tmp_path / 'repeat')
    assert digest(summary['rows']) == digest(second['rows'])
    before = (path / 'metadata.json').read_bytes()
    with pytest.raises(FileExistsError):run_demo('collision-risk', path)
    assert (path / 'metadata.json').read_bytes() == before
    with pytest.raises(ValueError):run_demo('unapproved-fourth-demo', tmp_path / 'bad')
    assert not (tmp_path / 'bad').exists()


def test_replay_rejects_altered_decision(demos):
    path, _ = demos['collision-risk']
    metadata = json.loads((path / 'metadata.json').read_text())
    records = json.loads((path / 'records.json').read_text())
    tampered = deepcopy(records)
    tampered[20]['payload']['r3_readiness']['advisory']['limiting_reason'] = 'ALTERED'
    result = recompute_advisory(iter(tampered), metadata['r3'], metadata['software_fingerprint'])
    assert result['result'] == 'MISMATCH' and result['first_divergence'] == 21
