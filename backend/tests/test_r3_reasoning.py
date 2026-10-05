from copy import deepcopy
import pytest
from app.r3.reasoning_models import *
from app.r3.reasoning import *
from app.r3.reasoning_fixtures import ReasoningFixture,demo_config,novelty_demo

def warm(fixture,**kwargs):
    for _ in range(10):decision=fixture.feed(**kwargs)
    return decision

def test_unknown_default_and_no_empty_frame_clear_claim():
    f=ReasoningFixture(ReasoningConfig())
    d=warm(f)
    assert d['state']=='UNKNOWN' and d['advised_speed_mps'] is None
    assert d['observability']['road_clear_claim'] is False
    assert not d['hardware_verified'] and not d['motion_authority']

def test_novelty_sequence_and_no_ghost_peer():
    rows=novelty_demo()
    end=lambda name:[r for r in rows['novelty'] if r['stage']==name][-1]
    assert end('HEALTHY')['state']=='NORMAL'
    assert end('RGB_FOG')['state']=='RESTRICT' and end('RGB_FOG')['speed']>0
    assert end('GEOMETRY_LOSS')['state']=='UNKNOWN'
    assert end('RECOVERY')['state']=='NORMAL'
    peer=[r for r in rows['blind_curve'] if r['stage']=='PEER_APPROACH'][-1]
    assert peer['state']=='RESTRICT' and peer['peers'][0]['potential_conflict']
    assert rows['blind_curve'][-1]['peers']==[]
    assert all(not p['local_observation'] for r in rows['blind_curve'] for p in r['peers'])

@pytest.mark.parametrize('uncertainty',[.01,.05,.1,.3,.8,1.5,3.])
def test_worse_uncertainty_never_increases_capability(uncertainty):
    f=ReasoningFixture();before=warm(f);after=f.feed(uncertainty=uncertainty)
    assert (after['advised_speed_mps'] or 0)<=before['advised_speed_mps']
    assert ORDER[after['state']]>=ORDER[before['state']]

@pytest.mark.parametrize('source',['radar-a','rgb-a','thermal-a','imu-a','encoders-a','gnss-a','gnss-b'])
def test_loss_does_not_increase_capability(source):
    f=ReasoningFixture();warm(f,peer=True);before=f.engine.previous['cap']
    for _ in range(15):d=f.feed(omit=(source,),peer=True)
    assert (d['advised_speed_mps'] or 0)<=before

def test_radial_velocity_never_becomes_full_velocity_and_ttc_is_null():
    f=ReasoningFixture();warm(f)
    d=f.feed(points=[(2.,0.,-50.)])
    assert d['tracks'][0]['radial_velocity_mps']==-50.
    assert d['tracks'][0]['relative_velocity_mps'] is None
    assert d['tracks'][0]['absolute_target_velocity'] is None
    assert d['ttc'][0]['value_s'] is None and not d['ttc'][0]['valid']

def test_two_position_motion_is_conditional_and_doppler_independent():
    f=ReasoningFixture();warm(f)
    f.feed(points=[(2.,0.,80.)]);d=f.feed(points=[(1.9,0.,80.)])
    t=d['tracks'][0]
    assert t['relative_velocity_mps'][0]==pytest.approx(-1.)
    assert t['velocity_method']=='TWO_POSITION_FIXED_BODY_AXES_RESEARCH'
    assert d['ttc'][0]['valid'] and d['ttc'][0]['value_s']>0

def test_invalid_calibration_and_clock_remove_geometry_purposes():
    f=ReasoningFixture();warm(f)
    key=f.bundle.calibration_bundle['radar-a'][0];f.channel.calibrations.invalidate(key,'MOUNT_MOVED')
    d=f.feed(points=[(1.,0.,-1.)]);s=next(x for x in d['semantic_observations'] if x['source_id']=='radar-a')
    assert 'RANGE' not in s['purposes'] and not d['tracks']
    f.channel.clocks.records.clear();d=f.feed()
    assert not d['qualified_sources'] and d['state']=='UNKNOWN'

def test_duplicate_and_out_of_order_do_not_refresh_or_recover():
    f=ReasoningFixture();warm(f);old=f.channel.latest['radar-a'];counter=f.channel.counters['radar-a']['accepted']
    assert not f.channel.accept(old,f.now)
    bad=old.model_copy(update={'integrity':old.integrity.model_copy(update={'sequence_number':1})})
    assert not f.channel.accept(bad,f.now)
    d=f.engine.step(f.channel,f.now+2_000_000_000)
    assert d['state']=='UNKNOWN' and f.channel.counters['radar-a']['accepted']==counter

def test_recovery_requires_distinct_frames_not_polling():
    f=ReasoningFixture();d=f.feed();assert d['state']=='UNKNOWN'
    for _ in range(20):d=f.engine.step(f.channel,f.now)
    assert d['state']=='UNKNOWN'
    assert warm(f)['state']=='NORMAL'

def test_node_uncertainty_and_correction_loss_remove_peer():
    f=ReasoningFixture();warm(f,peer=True)
    d=f.feed(peer=True,peer_uncertainty=10.)
    assert d['cooperative_context']==[] and d['state']=='UNKNOWN'
    d=f.feed(peer=True,correction_age=10.)
    assert d['cooperative_context']==[]

def test_configuration_rejects_nonfinite_and_silent_geometry_defaults():
    with pytest.raises(ValueError):ReasoningConfig.model_validate({'vehicle':{'deceleration_mps2':0.}})
    with pytest.raises(ValueError):CoverageModel(source_id='radar-a',hazard_classes=['X'],half_angle_deg=30.,provenance='MEASURED',evidence_reference='none')
    with pytest.raises(ValueError):ReasoningConfig(corridor_half_width_m=float('nan'))

def test_no_gnss_as_local_range_and_unavailable_map_does_not_matter():
    f=ReasoningFixture();d=warm(f,peer=True)
    assert d['tracks']==[]
    assert all('RANGE' not in s['purposes'] for s in d['semantic_observations'] if s['source_id'].startswith('gnss'))

def test_checkpoint_determinism_and_json_roundtrip():
    f=ReasoningFixture();warm(f);checkpoint=f.engine.checkpoint()
    clone=R3Reasoner(f.config,'FIXTURE_SOFTWARE');clone.restore(checkpoint)
    d=f.feed(points=[(4.,0.,-.5)])
    replayed=clone.step(f.channel,f.now)
    assert d==replayed
    assert R3Decision.model_validate_json(R3Decision.model_validate(d).model_dump_json()).model_dump(mode='json')==d

def test_image_geometry_does_not_invent_range_and_disagreement_visible():
    f=ReasoningFixture();warm(f)
    d=f.feed(rgb_label='PERSON')
    assert not d['tracks']
    assert d['state']=='UNKNOWN' and d['limiting_reason']=='SEMANTIC_GEOMETRY_UNRESOLVED'
    f.feed(points=[(2.,0.,-1.)],rgb_label='PERSON')
    d=f.feed(points=[(1.9,0.,-1.)],rgb_label='PERSON')
    assert d['tracks'][0]['association']=='ASSOCIATED'
    assert d['tracks'][0]['classifications']==['PERSON']

def test_semantic_conflict_is_not_averaged_away():
    f=ReasoningFixture();warm(f)
    d=f.feed(points=[(2.,0.,-1.)],rgb_label='PERSON',thermal_label='VEHICLE')
    assert d['tracks'][0]['association']=='CONFLICTING'
    assert len(d['tracks'][0]['semantic_evidence_ids'])==2
    assert d['state']=='UNKNOWN' and d['limiting_reason']=='SOURCE_CONFLICT'

def test_over_capacity_cannot_hide_unprocessed_hazards():
    f=ReasoningFixture();warm(f)
    d=f.feed(points=[(40.,20.,0.)]*40)
    assert len(d['tracks'])<=f.config.max_tracks
    assert d['state']=='UNKNOWN' and d['limiting_reason']=='TRACK_CAPACITY_EXCEEDED'

def test_held_track_cannot_keep_current_velocity_without_new_measurement():
    f=ReasoningFixture();warm(f);f.feed(points=[(2.,0.,-1.)]);f.feed(points=[(1.9,0.,-1.)])
    d=f.engine.step(f.channel,f.now+20_000_000)
    assert d['tracks'][0]['lifecycle']=='COASTING' and d['ttc'][0]['value_s'] is None

@pytest.mark.parametrize('radius',[15.,10.,5.,2.,.5,0.])
def test_smaller_coverage_never_increases_capability(radius):
    config=demo_config();reference=warm(ReasoningFixture(config))
    changed=config.model_copy(update={'coverage':[m.model_copy(update={'range_m':min(m.range_m,radius)}) for m in config.coverage]})
    d=warm(ReasoningFixture(changed))
    assert (d['advised_speed_mps'] or 0.)<=reference['advised_speed_mps']
    assert ORDER[d['state']]>=ORDER[reference['state']]

def test_mixed_source_modes_cannot_justify_combined_envelope():
    f=ReasoningFixture();warm(f)
    old=f.channel.latest['rgb-a'];identity=old.identity.model_copy(update={'session_id':'real-session'})
    f.channel.begin_source(identity,'REAL',detected=True,identity_verified=True)
    o=old.model_copy(update={'identity':identity,'observation_id':'real-image',
        'provenance':old.provenance.model_copy(update={'mode':'REAL','evidence_origin':'REAL_CAPTURE'})})
    assert f.channel.accept(o,f.now)
    d=f.engine.step(f.channel,f.now)
    assert d['state']=='UNKNOWN' and d['limiting_reason']=='SOURCE_MODE_CONFLICT'

def test_publication_expiry_does_not_relax_stop():
    from app.r3.evidence import age_readiness
    f=ReasoningFixture();warm(f);d=f.feed(points=[(.4,0.,0.)]);assert d['state']=='STOP'
    view=f.channel.snapshot(f.now);view['advisory']=d
    aged=age_readiness(view,f.now+2_000_000_000)
    assert aged['advisory']['state']=='STOP' and aged['advisory']['advised_speed_mps']==0.
    assert aged['advisory']['publication_expired'] and not aged['advisory']['cooperative_context']
