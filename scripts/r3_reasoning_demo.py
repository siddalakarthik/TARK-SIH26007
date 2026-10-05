"""Run the production R3 reasoner on explicit synthetic research evidence.

No serial/USB/I2C/network access. Produces reproducible records, comparisons,
25-scenario matrix and measured PC timings. Does not publish to the live bus.
"""
import argparse
import json
import math
import platform
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.r3.reasoning_fixtures import ReasoningFixture,novelty_demo
from app.r3.reasoning_scenarios import SCENARIOS,run_scenario
from app.r3.reasoning_models import Environment
from app.r3.replay import recompute_advisory,recompute_evidence
from app.r3.runtime import r3_software_fingerprint

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--ticks',type=int,default=300)
    args=parser.parse_args()
    if not 30<=args.ticks<=1000:parser.error('ticks must be 30..1000')
    if args.output.exists():parser.error('output directory exists; choose a new evidence directory')
    fingerprint=r3_software_fingerprint();f=ReasoningFixture(software=fingerprint)
    metadata=f.metadata();records=[];latencies=[];perception=[];reasoning=[]
    for i in range(args.ticks):
        environment=Environment(visibility='SEVERE',provenance='CONFIGURED_RESEARCH',evidence_reference='SYNTHETIC_FOG') if args.ticks//4<=i<args.ticks//2 else f.config.environment
        start=time.perf_counter_ns()
        d=f.feed(peer=args.ticks//2<=i<3*args.ticks//4,environment=environment,
                 omit=('gnss-b',) if i>=3*args.ticks//4 else ())
        latencies.append(time.perf_counter_ns()-start)
        perception.append(f.engine.metrics['perception_latency_ns']);reasoning.append(f.engine.metrics['reasoning_latency_ns'])
        records.append(f.record(d,environment))
    replay=recompute_advisory(iter(records),metadata,fingerprint)
    evidence=recompute_evidence(iter(records),metadata,fingerprint)
    matrix=[]
    for name,expected in SCENARIOS:
        d=run_scenario(name);matrix.append({'scenario':name,'expected_state':expected,'actual_state':d['state'],'pass':d['state']==expected,
            'reason':d['limiting_reason'],'advised_speed_mps':d['advised_speed_mps'],'observability_m':d['observability']['forward_range_m']})
    def stats(values):
        values=sorted(values)
        return {'p50_ms':values[math.ceil(len(values)*.5)-1]/1e6,'p95_ms':values[math.ceil(len(values)*.95)-1]/1e6,'max_ms':max(values)/1e6}
    output={'notice':'SYNTHETIC RESEARCH EVIDENCE ONLY; NO HARDWARE VALIDATION','software':fingerprint,'hardware_verified':False,
        'traction':'DISABLED_PHASE_1','machine':platform.machine(),'os':platform.system(),'ticks':args.ticks,'matrix':matrix,
        'r3_qualification':evidence,'r3_advisory':replay,'demonstrations':novelty_demo(),
        'performance':{'scope':'DEVELOPMENT_PC_NOT_PI5','fixture_admission_and_cycle':stats(latencies),'perception':stats(perception),
                       'reasoning':stats(reasoning),'queue_depth':0,'max_track_count':max(len(r['payload']['r3_readiness']['advisory']['tracks']) for r in records)}}
    args.output.mkdir(parents=True)
    for name,value in [('report.json',output),('metadata.json',metadata),('records.json',records)]:
        (args.output/name).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k not in {'demonstrations','matrix'}},indent=2))
    print(f'Scenarios passed: {sum(row["pass"] for row in matrix)}/{len(matrix)}')
    return 0 if all(row['pass'] for row in matrix) and replay['result']==evidence['result']=='MATCH' else 1

if __name__=='__main__':raise SystemExit(main())
