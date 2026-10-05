"""Independent exported-result checker: no study model functions imported."""
import csv
import hashlib
import json
import math
from pathlib import Path


def rows(path):
    with path.open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))


def close(a,b):
    if not math.isfinite(a) or not math.isfinite(b) or not math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8):
        raise ValueError(f'numerical mismatch: {a} != {b}')


def root_bisection(r,t,a,m,u):
    if r <= m+u: return 0.
    lo,hi=0.,1.
    while hi*t+hi*hi/(2*a)+m+u < r: hi*=2
    for _ in range(120):
        mid=(lo+hi)/2
        if mid*t+mid*mid/(2*a)+m+u <= r: lo=mid
        else: hi=mid
    return (lo+hi)/2


def percentile(x,q):
    y=sorted(x); f=(len(y)-1)*q; i=int(f)
    return y[i]+(y[min(i+1,len(y)-1)]-y[i])*(f-i)


def verify_numbers(root):
    n=0
    for r in rows(root/'tables/sim01_safe_speed_vs_range.csv'):
        v=root_bisection(*[float(r[k]) for k in ['trustworthy_perception_range_m','response_time_s','effective_deceleration_mps2','margin_m','uncertainty_m']])
        close(v,float(r['speed_mps'])); close(v*3.6,float(r['speed_kmph']));n+=1
    for name in ['sim01_required_range_vs_speed','sim02_operating_envelope','sim09_fullscale_requirements']:
        for r in rows(root/f'tables/{name}.csv'):
            v,t,a,m,u=[float(r[k]) for k in ['speed_mps','response_time_s','effective_deceleration_mps2','margin_m','uncertainty_m']]
            req=v*t+v*v/(2*a)+m+u; close(req,float(r['required_perception_range_m']));n+=1
            if name=='sim02_operating_envelope': close(float(r['trustworthy_perception_range_m'])-req,float(r['safety_margin_m']))
    samples=rows(root/'tables/sim07_samples.csv'); margins=[]
    for r in samples:
        v,t,a,m,u,R=[float(r[k]) for k in ['speed_mps','delay_s','deceleration_mps2','margin_m','uncertainty_m','range_m']]
        sm=R-(v*t+v*v/(2*a)+m+u);close(sm,float(r['safety_margin_m']));margins.append(sm);n+=1
    summaries=rows(root/'tables/sim07_uncertainty_samples_summary.csv')
    for r in summaries:
        s=margins[:int(r['samples'])]
        for key,q in [('p05_m',.05),('median_m',.5),('p95_m',.95)]: close(percentile(s,q),float(r[key]))
        close(min(s),float(r['minimum_m']));close(max(s),float(r['maximum_m']))
        close(sum(v<0 for v in s)/len(s),float(r['negative_margin_fraction']))
    d=json.loads((root/'inputs/design.json').read_text())['uncertainty']; a,b=summaries[-2:]
    stable=abs(float(a['negative_margin_fraction'])-float(b['negative_margin_fraction'])) <= d['fraction_stability_tolerance']
    stable &= all(abs(float(a[k])-float(b[k]))<=d['quantile_stability_tolerance_m'] for k in ['p05_m','median_m','p95_m'])
    if not stable: raise ValueError('predeclared uncertainty stability gate failed')
    for r in rows(root/'tables/sim08_operational_continuity.csv'):
        cap=float(r['speed_mps']); travel=cap if cap>0 else float(r['recovery_speed_mps'])
        cycle=float(r['fixed_fraction'])+float(r['nonfog_fraction'])+float(r['fog_fraction'])*float(r['desired_speed_mps'])/travel+(float(r['dwell_index']) if cap<=0 else 0)
        close(cycle,float(r['normalized_cycle_time']));close(1/cycle,float(r['normalized_productivity']));n+=1
    for r in rows(root/'tables/sim06_fault_story.csv'):
        if r['traction']!='DISABLED_PHASE_1': raise ValueError('traction changed')
        for k in ['live_permitted_speed_mps','live_left_command','live_right_command']: close(float(r[k]),0)
    for source in json.loads((root/'sources/source_inventory.json').read_text()):
        if hashlib.sha256((root/'sources'/source['file']).read_bytes()).hexdigest()!=source['sha256']: raise ValueError('source hash mismatch')
    for fig in json.loads((root/'results/figure_inventory.json').read_text()):
        if hashlib.sha256((root/fig['source_table']).read_bytes()).hexdigest()!=fig['source_sha256']: raise ValueError('figure source mismatch')
        for ext in ['png','svg']:
            if (root/'figures'/f"{fig['figure']}.{ext}").stat().st_size<1000: raise ValueError('missing/empty figure')
    return {'result':'PASS','independent_numeric_rows':n,'uncertainty_prefix_stability':'PASS','source_and_figure_checks':'PASS'}


def verify_hashes(root,repo):
    inventory=json.loads((root/'hashes.json').read_text())
    for name,expected in inventory.items():
        p=(repo/name).resolve()
        if not p.is_relative_to(repo.resolve()): raise ValueError('inventory path escapes repository')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected: raise ValueError(f'hash mismatch: {name}')
    return len(inventory)


def verify_summary(root):
    summary=json.loads((root/'results/final_simulation_summary.json').read_text())
    for h in summary['headline_results']:
        selected=[r for r in rows(root/h['source_table']) if r['scenario_id']==h['scenario_id']]
        if len(selected)!=1:raise ValueError('headline row identity mismatch')
        close(float(selected[0][h['field']]),h['value'])
    if any(summary[k] is not False for k in ['hardware_access','physical_validation','production_code_modified']):
        raise ValueError('invalid maturity flags')
    if len(summary['simulations_completed'])!=10:raise ValueError('incomplete simulation inventory')
    return len(summary['headline_results'])
