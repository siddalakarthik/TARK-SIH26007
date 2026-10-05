from copy import deepcopy
import pytest
from app.r3.reasoning_fixtures import ReasoningFixture
from app.r3.replay import recompute_advisory,recompute_evidence
from app.r3.reasoning_scenarios import SCENARIOS,run_scenario

@pytest.mark.parametrize('name,expected',SCENARIOS)
def test_required_scenario(name,expected):
    d=run_scenario(name)
    assert d['state']==expected, d['limiting_reason']
    assert d['traction']=='DISABLED_PHASE_1' and not d['motion_authority']
    assert d['observability']['road_clear_claim'] is False

def recorded_fixture():
    f=ReasoningFixture()
    for _ in range(10):f.feed()
    metadata=f.metadata();records=[]
    for i in range(30):
        d=f.feed(peer=i>=10,omit=('rgb-a',) if 15<=i<23 else ())
        records.append(f.record(d))
    return f,metadata,records

def test_replay_match_and_no_live_mutation():
    f,metadata,records=recorded_fixture();before=deepcopy(f.channel.record());checkpoint=f.engine.checkpoint()
    result=recompute_advisory(iter(records),metadata,'FIXTURE_SOFTWARE')
    assert result['result']=='MATCH',result
    assert result['verified_ticks']==30 and result['computation_ns']>0
    assert recompute_evidence(iter(records),metadata,'FIXTURE_SOFTWARE')['result']=='MATCH'
    assert before==f.channel.record() and checkpoint==f.engine.checkpoint()

def test_first_divergence_and_corrupt_records():
    _,metadata,records=recorded_fixture()
    records[3]['payload']['r3_readiness']['advisory']['limiting_reason']='ALTERED'
    r=recompute_advisory(iter(records),metadata,'FIXTURE_SOFTWARE')
    assert r['result']=='MISMATCH' and r['first_divergence']==records[3]['sequence']
    records[3]['payload']['r3_readiness']['advisory']['advised_speed_mps']=float('nan')
    assert recompute_advisory(iter(records),metadata,'FIXTURE_SOFTWARE')['result']=='NOT RECOMPUTABLE'

@pytest.mark.parametrize('corruption',['fingerprint','checkpoint','config','order','environment'])
def test_replay_refuses_incompatible_inputs(corruption):
    _,metadata,records=recorded_fixture()
    if corruption=='fingerprint':metadata['software_fingerprint']='OLD'
    if corruption=='checkpoint':metadata['reasoning']['checkpoint']['counter']=-1
    if corruption=='config':metadata['reasoning']['configuration']['corridor_half_width_m']=2.
    if corruption=='order':records[1]['sequence']=records[0]['sequence']
    if corruption=='environment':records[0]['payload']['r3_evidence'].pop('reasoning_environment')
    assert recompute_advisory(iter(records),metadata,'FIXTURE_SOFTWARE')['result']=='NOT RECOMPUTABLE'
