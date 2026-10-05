"""Deterministic study generation. CSV tables are the plotting/report authority."""
import csv
import json
import math
from itertools import product
from dataclasses import replace
import numpy as np
from .model import Parameters, components, speed_cap, operating_point, encounter, requirements, normalized_cycle

MASTER = 'simulation_id scenario_id visibility_m trustworthy_perception_range_m speed_mps speed_kmph response_time_s effective_deceleration_mps2 uncertainty_m stopping_distance_m required_perception_range_m safety_margin_m minimum_clearance_m ttc_analysis_s operation_available restricted halted normalized_cycle_time normalized_productivity input_provenance result_class'.split()


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fields, extrasaction='ignore', lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def grid(spec):
    lo, hi, step = spec
    if step <= 0 or hi < lo:
        raise ValueError('invalid grid')
    return np.arange(lo, hi+step/2, step).tolist()


def validate_design(d, timeline):
    def finite(obj):
        if isinstance(obj,dict):
            for value in obj.values():finite(value)
        elif isinstance(obj,list):
            for value in obj:finite(value)
        elif isinstance(obj,(int,float)) and not math.isfinite(obj):raise ValueError('nonfinite design input')
    finite(d);finite(timeline)
    if d['schema_version'] != 1 or timeline['schema_version'] != 1:
        raise ValueError('unsupported schema')
    if set(d['sets']) != {'favourable','reference','adverse'}:
        raise ValueError('missing bound set')
    for p in d['sets'].values(): Parameters(**p)
    if d['visual_cases_m'] != [3,4,5]: raise ValueError('mandatory visual cases')
    for name in ['fog','integrated']:
        if not timeline[name]: raise ValueError('empty scenario')
        for row in timeline[name]:
            if type(row['available']) is not bool or type(row.get('link',True)) is not bool or any(row[k]<0 for k in ['age_s','range_m','visual_m','uncertainty_m']):
                raise ValueError('invalid scenario')
    if timeline['epoch_s']<=0 or timeline['desired_speed_mps']<=0:raise ValueError('invalid timeline controls')
    counts=d['uncertainty']['counts']
    if len(counts)<2 or any(type(n) is not int or n<2 for n in counts) or sorted(set(counts))!=counts:raise ValueError('invalid sample prefixes')
    c=d['cycle']
    if abs(c['fixed_fraction']+c['nonfog_fraction']+c['fog_fraction']-1)>1e-9:
        raise ValueError('cycle shares')
    for key in ['delay_s','deceleration_mps2','uncertainty_m','range_m','speed_mps']:
        a,b=d['uncertainty'][key]
        if not 0 <= a < b: raise ValueError('sampling bounds')
    if d['uncertainty']['deceleration_mps2'][0] <= 0: raise ValueError('zero deceleration')
    grid(d['range_grid_m']); grid(d['speed_grid_mps'])


def provenance_registry(root, d, timeline):
    rows=[]
    def walk(obj, prefix, source):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k != 'provenance': walk(v, f'{prefix}.{k}' if prefix else k, source)
        elif isinstance(obj,list):
            for i,v in enumerate(obj): walk(v, f'{prefix}[{i}]',source)
        elif isinstance(obj,(int,float)) and not isinstance(obj,bool):
            pc='ASSUMED_SENSITIVITY'; origin=source
            if prefix.startswith('visual_cases_m'):
                pc='DERIVED' if obj==4 else 'OFFICIAL_SIH'; origin='sources/SIH26007_official_modal.html: Background'
            if prefix.startswith('freshness'):
                pc='CURRENT_TARK_CONFIG'; origin='config/phase1.json; docs/ESP32_PROTOCOL_V2.md'
            if any(x in prefix for x in ['schema_version','seed','counts','quantiles','tolerance','iterations','epsilon']): pc='DERIVED'
            unit='dimensionless'
            if 'mps2' in prefix: unit='m/s2'
            elif 'mps' in prefix: unit='m/s'
            elif '_m' in prefix: unit='m'
            elif '_s' in prefix: unit='s'
            rows.append({'parameter':prefix,'symbol':prefix,'value/range':obj,'units':unit,
                         'provenance_class':pc,'source':origin,'source_date/version':'2026-09-29 / schema 1',
                         'reason':'Declared experiment control or sensitivity input; not mine measurement',
                         'used_by':('SIM-03' if prefix.startswith('encounter') else 'SIM-07' if prefix.startswith(('uncertainty','seed')) else 'SIM-08/09' if prefix.startswith('cycle') else 'SIM-04/10' if prefix.startswith('timeline') else 'SIM-05/06' if prefix.startswith('freshness') else 'shared model / numerical verification'),
                         'physical_validation_status':'NOT PHYSICALLY VALIDATED'})
    walk(d,'','inputs/design.json'); walk(timeline,'timeline','scenarios/timelines.json')
    rows += [dict(parameter='speed_unit_conversion',symbol='km/h per m/s',**{'value/range':3.6},units='(km/h)/(m/s)',provenance_class='DERIVED',source='3600 seconds/hour / 1000 metres/km',**{'source_date/version':'SI units'},reason='Exact unit conversion',used_by='all speed displays',physical_validation_status='NOT APPLICABLE')]
    write_csv(root/'inputs/parameter_registry.csv',rows)


def run(root, repo):
    d=json.loads((root/'inputs/design.json').read_text()); timeline=json.loads((root/'scenarios/timelines.json').read_text())
    validate_design(d,timeline); provenance_registry(root,d,timeline)
    sets={k:Parameters(**v) for k,v in d['sets'].items()}; ref=sets['reference']
    tables={}; master=[]
    def save(name, rows, sim):
        for i,r in enumerate(rows):
            r['simulation_id']=sim; r['scenario_id']=f'{name}-{i+1:06d}'
            r.setdefault('input_provenance','ASSUMED_SENSITIVITY')
            r.setdefault('result_class','SENSITIVITY_RESULT')
        write_csv(root/'tables'/f'{name}.csv',rows); tables[name]=rows
        master.extend(dict(r) for r in rows)
    def base(p,r,v,ps):
        return dict(parameter_set=ps,trustworthy_perception_range_m=r,speed_mps=v,speed_kmph=v*3.6,
                    response_time_s=p.delay_s,effective_deceleration_mps2=p.deceleration_mps2,
                    margin_m=p.margin_m,uncertainty_m=p.uncertainty_m)
    rows=[]
    for ps,p in sets.items():
        for r in grid(d['range_grid_m']):
            v=speed_cap(r,p); c=components(v,p)
            rows.append(dict(**base(p,r,v,ps),**c,safety_margin_m=r-c['required_perception_range_m'],
                             positive_speed_available=v>0,visibility_m=r if r in d['visual_cases_m'] else None))
    save('sim01_safe_speed_vs_range',rows,'SIM-01')
    save('sim01_required_range_vs_speed',[dict(**base(p,None,v,ps),**components(v,p)) for ps,p in sets.items() for v in grid(d['speed_grid_mps'])],'SIM-01')
    rows=[]
    for ps,p in sets.items():
        for r,v in product(grid(d['range_grid_m']),grid(d['speed_grid_mps'])):
            c=components(v,p); sm=r-c['required_perception_range_m']
            rows.append(dict(**base(p,r,v,ps),**c,safety_margin_m=sm,speed_cap_mps=speed_cap(r,p),
                             model_region='MODEL_COMPATIBLE' if sm>=0 else 'RESTRICT_TO_CAP' if speed_cap(r,p)>0 else 'HALT_UNAVAILABLE'))
    save('sim02_operating_envelope',rows,'SIM-02')
    e=d['encounter']; rows=[]
    for ps,p in sets.items():
        for sep,v,r,kind in product(e['separations_m'],e['speeds_mps'],e['ranges_m'],['stationary','slower_lead','oncoming']):
            vt=0 if kind=='stationary' else v*(e['lead_speed_ratio'] if kind=='slower_lead' else e['oncoming_speed_ratio'])
            rows.append(dict(**base(p,r,v,ps),encounter_type=kind,initial_separation_m=sep,target_speed_mps=vt,
                             **encounter(sep,v,vt,r,p,e['post_stop_horizon_s'])))
    save('sim03_encounters',rows,'SIM-03')
    for name,sim in [('fog','SIM-04'),('integrated','SIM-10')]:
        rows=[]
        for i,event in enumerate(timeline[name]):
            p=replace(ref,uncertainty_m=event['uncertainty_m'])
            r=min(event['range_m'],event.get('separation_m',event['range_m']))
            point=operating_point(r,timeline['desired_speed_mps'],p,age_s=event['age_s'],stale_s=d['freshness']['stale_s'],available=event['available'] and event.get('link',True))
            rows.append(dict(**{k:v for k,v in base(p,r,point['speed_mps'],'reference').items() if k not in point},
                             **point,epoch_start_s=i*timeline['epoch_s'],epoch_duration_s=timeline['epoch_s'],
                             visibility_m=event['visual_m'],event=event['name'],age_s=event['age_s'],
                             evidence_available=event['available'],link_available=event.get('link',True),
                             separation_m=event.get('separation_m'),visual_reference_cap_mps=speed_cap(event['visual_m'],p),
                             result_class='SYNTHETIC_SCENARIO_RESULT'))
        save('sim04_fog_transition' if name=='fog' else 'sim10_integrated',rows,sim)
    rows=[]
    for r,u,age,kind in product(d['cycle']['range_cases_m'],[ref.uncertainty_m,sets['adverse'].uncertainty_m],
                              [0,d['freshness']['fresh_s'],d['freshness']['stale_s'],timeline['fog'][3]['age_s']],
                              ['valid_target','valid_empty','missing','out_of_order']):
        p=replace(ref,uncertainty_m=u)
        point=operating_point(r,d['cycle']['desired_speed_mps'],p,age_s=age,stale_s=d['freshness']['stale_s'],available=kind=='valid_target')
        rows.append(dict(**{k:v for k,v in base(p,r,point['speed_mps'],'reference').items() if k not in point},
                         **point,age_s=age,report_kind=kind,
                         reason='research gate; empty does not prove clear space; out-of-order report grants no new authority'))
    save('sim05_perception_degradation',rows,'SIM-05')
    # Project existing verified traces; do not duplicate a wire protocol or claim fresh hardware timing.
    rows=[]
    for sid in ['EV-03','EV-05','EV-07','EV-10','EV-11','EV-13','EV-14','EV-15','EV-20']:
        trace=[json.loads(x) for x in (repo/'evidence/prompt3/traces'/f'{sid}.jsonl').read_text().splitlines()]
        for t in trace:
            cmd=t.get('command') or {}; facts=t['facts']
            assert t['traction']=='DISABLED_PHASE_1'
            assert all(cmd.get(k,0)==0 for k in ['permitted_speed_mps','left_command','right_command'])
            r=t['decision']['D_env_m'] if t.get('decision') else 0
            available=facts['freshness']=='FRESH' and facts['communication']=='ONLINE' and facts['receiver_active']
            point=operating_point(r,d['cycle']['desired_speed_mps'],ref,available=available)
            rows.append(dict(source_scenario=sid,step=t['step_number'],controlled_time_s=(t['logical_runtime_time']-trace[0]['logical_runtime_time'])/1e9,
                             action=t['action'],receiver_reason=facts['receiver_reason'],freshness=facts['freshness'],
                             r1_state=facts['state'],communication=facts['communication'],session_active=facts['session_active'],
                             receiver_active=facts['receiver_active'],live_permitted_speed_mps=cmd.get('permitted_speed_mps',0),
                             live_left_command=cmd.get('left_command',0),live_right_command=cmd.get('right_command',0),
                             traction=t['traction'],analytical_cap_mps=point['speed_mps'],
                             result_class='SOFTWARE_VERIFIED_R1',input_provenance='CURRENT_TARK_CONFIG; evidence/prompt3 verified trace',
                             note='R1 fields copied; analytical_cap is a separate conservative research overlay'))
    save('sim06_fault_story',rows,'SIM-06')
    u=d['uncertainty']; n=max(u['counts']); rng=np.random.default_rng(d['seed'])
    # Row-major draws preserve prefixes when increasing sample count.
    names=['delay_s','deceleration_mps2','uncertainty_m','range_m','speed_mps']; draws=rng.random((n,len(names)))
    vals={k:u[k][0]+draws[:,i]*(u[k][1]-u[k][0]) for i,k in enumerate(names)}
    req=vals['speed_mps']*vals['delay_s']+vals['speed_mps']**2/(2*vals['deceleration_mps2'])+u['margin_m']+vals['uncertainty_m']
    sm=vals['range_m']-req
    rows=[dict(sample=i+1,**{k:float(v[i]) for k,v in vals.items()},
               trustworthy_perception_range_m=float(vals['range_m'][i]),speed_kmph=float(vals['speed_mps'][i])*3.6,
               response_time_s=float(vals['delay_s'][i]),effective_deceleration_mps2=float(vals['deceleration_mps2'][i]),
               margin_m=u['margin_m'],stopping_distance_m=float(req[i]-vals['uncertainty_m'][i]),
               required_perception_range_m=float(req[i]),safety_margin_m=float(sm[i])) for i in range(n)]
    save('sim07_samples',rows,'SIM-07')
    summary=[]
    for count in u['counts']:
        x=sm[:count]; q=np.quantile(x,u['quantiles'])
        summary.append(dict(samples=count,seed=d['seed'],minimum_m=float(x.min()),p05_m=float(q[0]),median_m=float(q[1]),p95_m=float(q[2]),maximum_m=float(x.max()),negative_margin_fraction=float(np.mean(x<0))))
    save('sim07_uncertainty_samples_summary',summary,'SIM-07')
    sensitivity=[]
    for k in names:
        sensitivity.append(dict(parameter=k,pearson_correlation=float(np.corrcoef(vals[k],sm)[0,1]),method='marginal Pearson correlation over declared independent uniform bounds'))
    save('sim07_sensitivity',sensitivity,'SIM-07')
    c=d['cycle']; rows=[]
    for ps,p in sets.items():
        for r,dwell,policy in product(c['range_cases_m'],c['halt_dwell_indices'],['visual_reference','halt_reference','perception_concept']):
            rr=c['visual_m'] if policy=='visual_reference' else r
            point=operating_point(rr,c['desired_speed_mps'],p)
            cap=0 if policy=='halt_reference' else point['speed_mps']
            recovery=operating_point(c['recovery_range_m'],c['desired_speed_mps'],p)['speed_mps']
            out=normalized_cycle(c['fixed_fraction'],c['nonfog_fraction'],c['fog_fraction'],c['desired_speed_mps'],cap,recovery,dwell)
            rows.append(dict(**base(p,rr,cap,ps),policy=policy,range_case_m=r,visibility_m=c['visual_m'],
                             fixed_fraction=c['fixed_fraction'],nonfog_fraction=c['nonfog_fraction'],fog_fraction=c['fog_fraction'],
                             desired_speed_mps=c['desired_speed_mps'],recovery_speed_mps=recovery,dwell_index=dwell,
                             operation_available=cap>0,restricted=0<cap<c['desired_speed_mps'],halted=cap==0,
                             safety_margin_m=rr-components(cap,p)['required_perception_range_m'],**out))
    save('sim08_operational_continuity',rows,'SIM-08')
    save('sim09_fullscale_requirements',[dict(**base(p,r,v,ps),**requirements(v,r,p)) for ps,p in sets.items() for v,r in product(d['candidate_speeds_mps'],c['range_cases_m']+[100,150])],'SIM-09')
    # Pareto comparison only within fixed range and parameter set. More sensing is not free.
    rows=[]
    for r in c['range_cases_m']:
        feasible=[q for q in tables['sim02_operating_envelope'] if q['parameter_set']=='reference' and q['trustworthy_perception_range_m']==r and q['safety_margin_m']>=0]
        for q in feasible:
            dominated=any(z['speed_mps']>=q['speed_mps'] and z['safety_margin_m']>=q['safety_margin_m'] and (z['speed_mps']>q['speed_mps'] or z['safety_margin_m']>q['safety_margin_m']) for z in feasible)
            rows.append(dict(q,dominated=dominated))
    save('safety_efficiency_trade_space',rows,'SIM-02')
    write_csv(root/'results/SIH_SIMULATION_MASTER_RESULTS.csv',master,MASTER)
    return d,timeline,tables
