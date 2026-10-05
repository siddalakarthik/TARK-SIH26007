"""Read-only, bounded HTTP measurements for a running TARK instance.

Run on Pi 5 after commissioning to obtain Pi-local observations. Running this on
a PC measures that PC's HTTP path, not Pi real-time capability. Never opens a
sensor or starts a recording. Output is JSON on stdout; redirect deliberately.
"""
import argparse
import json
import math
import platform
import time
import urllib.request
from urllib.parse import urlsplit

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True);p.add_argument('--samples',type=int,default=20)
    p.add_argument('--interval',type=float,default=.25);args=p.parse_args()
    u=urlsplit(args.url)
    if u.scheme not in {'http','https'} or not u.netloc or u.username or u.password or u.query or u.fragment:p.error('explicit HTTP(S) base URL without credentials required')
    if not 1<=args.samples<=200 or not .1<=args.interval<=5:p.error('samples 1..200 and interval .1..5 required')
    timings=[];failures=0;last=None;total_bytes=0
    for _ in range(args.samples):
        start=time.monotonic_ns()
        try:
            with urllib.request.urlopen(args.url.rstrip('/')+'/api/v2/r3/readiness',timeout=2) as response:
                raw=response.read(1_000_001)
            if len(raw)>1_000_000:raise ValueError('response limit')
            value=json.loads(raw)
            if value.get('schema_version')!='TARK_READINESS_1':raise ValueError('wrong schema')
            last=value;total_bytes+=len(raw);timings.append(time.monotonic_ns()-start)
        except (OSError,ValueError):failures+=1
        time.sleep(args.interval)
    timings.sort()
    percentile=lambda n:timings[max(0,math.ceil(len(timings)*n)-1)]/1e6 if timings else None
    print(json.dumps({'observer_machine':platform.machine(),'observer_os':platform.system(),
        'scope':'HTTP latency and reported source health only; not hard-real-time or hardware validation',
        'samples':args.samples,'successes':len(timings),'failures':failures,'received_bytes':total_bytes,
        'http_p50_ms':percentile(.5),'http_p95_ms':percentile(.95),
        'last_sources':last['sources'] if last else None,'inference':last.get('inference') if last else None,
        'cpu_load':None,'temperature':None,'throttling':None,'hardware_verified':False},indent=2,allow_nan=False))
    return 0 if failures==0 else 1

if __name__=='__main__':raise SystemExit(main())
