"""25 explicit deterministic research scenarios; expected states are specifications."""
from app.r3.reasoning_fixtures import ReasoningFixture, demo_config, novelty_demo
from app.r3.reasoning_models import Environment

SCENARIOS=[
 ('clear_healthy','NORMAL'),('stationary_critical_obstacle','STOP'),('lead_moving','RESTRICT'),
 ('oncoming','STOP'),('crossing','UNKNOWN'),('rgb_fog_radar_valid','RESTRICT'),
 ('radar_stale','WARN'),('rgb_unavailable','RESTRICT'),('thermal_unavailable','WARN'),
 ('multiple_degraded','UNKNOWN'),('all_geometry_unavailable','UNKNOWN'),('calibration_invalid','WARN'),
 ('clock_expired','UNKNOWN'),('target_uncertainty_increases','UNKNOWN'),('duplicate_frame_expired','UNKNOWN'),
 ('out_of_order_expired','UNKNOWN'),('radar_rgb_geometry_disagreement','UNKNOWN'),
 ('node_b_approach','RESTRICT'),('node_b_stale','UNKNOWN'),('node_b_uncertain','UNKNOWN'),
 ('cooperative_correction_lost','UNKNOWN'),('map_unavailable','NORMAL'),('speed_increases','RESTRICT'),
 ('stopping_parameters_change','RESTRICT'),('sustained_recovery','NORMAL')]

def run_scenario(name):
    config=demo_config()
    if name=='stopping_parameters_change':config=config.model_copy(update={'vehicle':config.vehicle.model_copy(update={'deceleration_mps2':.03})})
    f=ReasoningFixture(config)
    for _ in range(10):d=f.feed(peer=name.startswith('node_b_') or name=='cooperative_correction_lost')
    if name in {'clear_healthy','map_unavailable','stopping_parameters_change'}:return d
    if name=='stationary_critical_obstacle':return f.feed(points=[(.4,0.,0.)])
    if name=='lead_moving':
        for i in range(12):d=f.feed(points=[(4.-i*.02,0.,-.2)])
    elif name=='oncoming':
        for i in range(12):d=f.feed(points=[(2.-i*.1,0.,-1.)])
    elif name=='crossing':
        for i in range(5):d=f.feed(points=[(4.,2.-i*.1,0.)])
    elif name=='rgb_fog_radar_valid':d=f.feed(environment=Environment(visibility='SEVERE',provenance='CONFIGURED_RESEARCH',evidence_reference='SYNTHETIC_FOG'))
    elif name in {'radar_stale','rgb_unavailable','thermal_unavailable','multiple_degraded','all_geometry_unavailable'}:
        missing={'radar_stale':('radar-a',),'rgb_unavailable':('rgb-a',),'thermal_unavailable':('thermal-a',),
                 'multiple_degraded':('radar-a','rgb-a','thermal-a','imu-a'),'all_geometry_unavailable':('radar-a','rgb-a','thermal-a')}[name]
        for _ in range(15):d=f.feed(omit=missing)
    elif name=='calibration_invalid':
        for key in f.bundle.calibration_bundle['radar-a']:f.channel.calibrations.invalidate(key,'MOUNT_MOVED')
        d=f.feed()
    elif name=='clock_expired':
        for key,mapping in list(f.channel.clocks.records.items()):f.channel.clocks.records[key]=mapping.model_copy(update={'valid_until_ns':f.now})
        d=f.feed()
    elif name=='target_uncertainty_increases':
        for i in range(12):d=f.feed(points=[(4.-i*.02,0.,-.2)])
        d=f.feed(points=[(3.75,0.,-.2)],uncertainty=3.)
    elif name in {'duplicate_frame_expired','out_of_order_expired'}:
        o=f.channel.latest['radar-a']
        if name=='out_of_order_expired':o=o.model_copy(update={'integrity':o.integrity.model_copy(update={'sequence_number':1})})
        assert not f.channel.accept(o,f.now)
        d=f.engine.step(f.channel,f.now+2_000_000_000)
    elif name=='radar_rgb_geometry_disagreement':
        for i in range(12):d=f.feed(points=[(4.-i*.02,0.,-.2)],rgb_label='PERSON',rgb_box=[0.,0.,10.,10.])
        assert d['tracks'][0]['association']=='UNRESOLVED' and not d['tracks'][0]['classifications']
    elif name=='node_b_approach':d=f.feed(peer=True)
    elif name=='node_b_stale':
        for _ in range(15):d=f.feed(omit=('gnss-b',))
        assert d['cooperative_context']==[]
    elif name=='node_b_uncertain':d=f.feed(peer=True,peer_uncertainty=10.)
    elif name=='cooperative_correction_lost':d=f.feed(peer=True,correction_age=10.)
    elif name=='speed_increases':d=f.feed(speed=3.)
    elif name=='sustained_recovery':
        for _ in range(10):f.feed(omit=('radar-a','rgb-a'))
        for _ in range(15):d=f.feed()
    else:raise ValueError('unknown scenario')
    return d
