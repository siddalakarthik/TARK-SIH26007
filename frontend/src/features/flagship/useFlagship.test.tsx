import {act,cleanup,renderHook} from '@testing-library/react';
import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import {isFlagship,useFlagship} from './useFlagship';

function fixture(sequence=1):any {
  const empty=()=>({type:'FeatureCollection',features:[]});
  return {schema_version:'tark.flagship.v1',mode:'SIMULATION',source_mode:'SIMULATION',
    timestamp_ns:sequence*1_000_000_000,sequence,traction:'DISABLED_PHASE_1',monitoring_only:true,
    hardware_verified:false,decision_source:'/api/v1/status',
    scene:{id:'demo-course-v1',label:'Synthetic test course',source:'SIMULATION',coordinate_system:'WGS84_DISPLAY_ANCHOR_ONLY',
      center:[78.4867,17.385],bounds:[78.48,17.38,78.49,17.39],review_status:'DEMO_FIXTURE_NOT_SURVEYED',
      roads:empty(),route:empty(),zones:empty(),waypoints:empty(),hazards:empty(),history:empty()},
    participants:[{id:'A',name:'Vehicle A',role:'INSTRUMENTED_VEHICLE',capabilities:['GNSS','RADAR']},
      {id:'B',name:'Node B',role:'LOCATION_ONLY',capabilities:['GNSS','PEER_TELEMETRY']}].map(p=>({...p,
        source_mode:'SIMULATION',state:'SIMULATED',position:{longitude_deg:78.4867,latitude_deg:17.385},
        speed_mps:.8,course_deg:90,heading_deg:null,accuracy_m:3,age_ms:0,
        timestamp_ns:sequence*1_000_000_000,quality:'SIMULATED_FIX'})),
    hardware:[{id:'radar',name:'TI IWR6843ISK',interface:'Processed output',status:'HARDWARE_PENDING',
      software_readiness:'MIGRATION_REQUIRED',reason:'Approved TI profile required'}],
    limitations:['Simulation only; not surveyed.']};
}
function unavailable(){
  const data=fixture();data.mode='REAL_RADAR';data.source_mode='UNAVAILABLE';
  data.scene.source='UNAVAILABLE';data.scene.review_status='UNAVAILABLE_NOT_SURVEYED';
  data.participants=data.participants.map((p:any)=>({...p,source_mode:'UNAVAILABLE',state:'UNAVAILABLE',quality:'NOT_CONNECTED',
    position:null,speed_mps:null,course_deg:null,heading_deg:null,accuracy_m:null,age_ms:null,timestamp_ns:null}));
  return data;
}
function response(body:any){return {ok:true,text:async()=>JSON.stringify(body)} as Response;}
async function flush(){await act(async()=>{await vi.advanceTimersByTimeAsync(0);});}
async function advance(ms:number){await act(async()=>{await vi.advanceTimersByTimeAsync(ms);});}
beforeEach(()=>vi.useFakeTimers({toFake:['setTimeout','clearTimeout','performance']}));
afterEach(()=>{cleanup();vi.useRealTimers();vi.unstubAllGlobals();vi.restoreAllMocks();});

test('accepts the current simulation and unavailable contracts without hardware claims',()=>{
  expect(isFlagship(fixture())).toBe(true);expect(isFlagship(unavailable())).toBe(true);
  const replay=unavailable();replay.mode='REPLAY';expect(isFlagship(replay)).toBe(true);
});

test.each([
  ['unknown mode',(d:any)=>{d.mode='LIVE';}],
  ['mixed sources',(d:any)=>{d.mode='REAL_RADAR';}],
  ['unknown source',(d:any)=>{d.source_mode='REAL';}],
  ['negative timestamp',(d:any)=>{d.timestamp_ns=-1;}],
  ['fractional timestamp',(d:any)=>{d.timestamp_ns=.5;}],
  ['NaN timestamp',(d:any)=>{d.timestamp_ns=NaN;}],
  ['negative sequence',(d:any)=>{d.sequence=-1;}],
  ['fractional sequence',(d:any)=>{d.sequence=1.5;}],
  ['unsafe sequence',(d:any)=>{d.sequence=Number.MAX_SAFE_INTEGER+1;}],
  ['fake verification',(d:any)=>{d.hardware_verified=true;}],
  ['motion authority',(d:any)=>{d.monitoring_only=false;}],
  ['traction enabled',(d:any)=>{d.traction='ENABLED';}],
  ['missing decision source',(d:any)=>{delete d.decision_source;}],
  ['negative age',(d:any)=>{d.participants[0].age_ms=-1;}],
  ['null simulation age',(d:any)=>{d.participants[0].age_ms=null;}],
  ['infinite age',(d:any)=>{d.participants[0].age_ms=Infinity;}],
  ['future participant timestamp',(d:any)=>{d.participants[0].timestamp_ns=d.timestamp_ns+1;}],
  ['unknown participant state',(d:any)=>{d.participants[0].state='SAFE';}],
  ['real participant in fixture',(d:any)=>{d.participants[0].source_mode='GNSS';}],
  ['duplicate identity',(d:any)=>{d.participants[1].id='A';}],
  ['fabricated B radar',(d:any)=>{d.participants[1].capabilities.push('RADAR');}],
  ['fabricated B heading',(d:any)=>{d.participants[1].heading_deg=90;}],
  ['invalid course',(d:any)=>{d.participants[0].course_deg=360;}],
  ['negative speed',(d:any)=>{d.participants[0].speed_mps=-1;}],
  ['invalid coordinates',(d:any)=>{d.participants[0].position.latitude_deg=91;}],
  ['reversed bounds',(d:any)=>{d.scene.bounds=[79,18,78,17];}],
  ['unverified map source',(d:any)=>{d.scene.source='LIVE';}],
  ['surveyed map claim',(d:any)=>{d.scene.review_status='SURVEYED';}],
  ['fake hardware online',(d:any)=>{d.hardware[0].status='ONLINE';}],
  ['fake software ready',(d:any)=>{d.hardware[0].software_readiness='VERIFIED';}],
] as const)('rejects %s',(_name,mutate)=>{const data=fixture();mutate(data);expect(isFlagship(data)).toBe(false);});

test('unavailable modes reject even a single simulated position or route',()=>{
  const position=unavailable();position.participants[0].position={longitude_deg:78,latitude_deg:17};
  expect(isFlagship(position)).toBe(false);
  const route=unavailable();route.scene.route.features=[{type:'Feature',properties:{source_mode:'SIMULATION',operational_authority:false},geometry:{type:'LineString',coordinates:[[78,17],[79,18]]}}];
  expect(isFlagship(route)).toBe(false);
});

test('geometry validation rejects malformed, oversized and authoritative display objects',()=>{
  const base={type:'Feature',properties:{source_mode:'SIMULATION',operational_authority:false},geometry:{type:'LineString',coordinates:[[78,17],[79,18]]}};
  const data=fixture();data.scene.route.features=[base];expect(isFlagship(data)).toBe(true);
  for(const coordinates of [[[78,17]],[[Infinity,17],[79,18]],[[78,91],[79,18]],Array(4097).fill([78,17])]){
    data.scene.route.features=[{...base,geometry:{type:'LineString',coordinates}}];expect(isFlagship(data)).toBe(false);
  }
  data.scene.route.features=[{...base,properties:{...base.properties,operational_authority:true}}];expect(isFlagship(data)).toBe(false);
  data.scene.route.features=Array(201).fill(base);expect(isFlagship(data)).toBe(false);
  data.scene.route.features=[];
  data.scene.zones.features=[{...base,geometry:{type:'Polygon',coordinates:[[[78,17],[79,17],[79,18],[78,18]]]}}];
  expect(isFlagship(data)).toBe(false);
});

test('polls sequentially using same-origin, no-store and a cancellable signal',async()=>{
  const fetcher=vi.fn().mockResolvedValue(response(fixture()));vi.stubGlobal('fetch',fetcher);
  const hook=renderHook(()=>useFlagship(true,0));await flush();
  expect(hook.result.current.data?.participants).toHaveLength(2);
  expect(fetcher).toHaveBeenCalledTimes(1);
  expect(fetcher.mock.calls[0][0]).toBe('/api/v1/flagship');
  expect(fetcher.mock.calls[0][1]).toMatchObject({credentials:'same-origin',cache:'no-store'});
  expect(fetcher.mock.calls[0][1].signal).toBeInstanceOf(AbortSignal);
  hook.unmount();expect(vi.getTimerCount()).toBe(0);
});

test('age expires independently of a hung poll and removes direction/speed authority',async()=>{
  const data=fixture();data.participants.forEach((p:any)=>{p.age_ms=250;});
  const fetcher=vi.fn().mockResolvedValueOnce(response(data)).mockImplementation(()=>new Promise(()=>{}));
  vi.stubGlobal('fetch',fetcher);
  const hook=renderHook(()=>useFlagship(true,0));await flush();
  await advance(1000);expect(hook.result.current.data?.participants[0].age_ms).toBe(1250);
  await advance(1749);expect(hook.result.current.data?.participants[0].state).toBe('SIMULATED');
  await advance(1);
  const participant=hook.result.current.data?.participants[0];
  expect(participant?.state).toBe('STALE');expect(participant?.age_ms).toBe(3000);
  expect(participant?.position).not.toBeNull(); // Last-known geometry remains explicit.
  expect(participant?.course_deg).toBeNull();expect(participant?.speed_mps).toBeNull();expect(participant?.accuracy_m).toBeNull();
  expect(fetcher).toHaveBeenCalledTimes(2); // No parallel requests while hung.
  hook.unmount();expect(fetcher.mock.calls[1][1].signal.aborted).toBe(true);
});

test('duplicate snapshots cannot refresh age even when the server repeats age zero',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue(response(fixture())));
  const hook=renderHook(()=>useFlagship(true,0));await flush();await advance(3000);
  expect(hook.result.current.data?.participants[0].state).toBe('STALE');
  expect(hook.result.current.data?.participants[0].age_ms).toBe(3000);
});

test('slow response time is conservatively added to the source age',async()=>{
  let resolve!:(response:Response)=>void;
  vi.stubGlobal('fetch',vi.fn(()=>new Promise<Response>(done=>{resolve=done;})));
  const hook=renderHook(()=>useFlagship(true,0));await advance(2500);
  const data=fixture();data.participants.forEach((p:any)=>{p.age_ms=700;});
  await act(async()=>resolve(response(data)));await flush();
  expect(hook.result.current.data?.participants[0].age_ms).toBe(3200);
  expect(hook.result.current.data?.participants[0].state).toBe('STALE');
});

test('out-of-order responses stay rejected until a new stream session is selected',async()=>{
  const fetcher=vi.fn().mockResolvedValueOnce(response(fixture(5))).mockResolvedValue(response(fixture(4)));
  vi.stubGlobal('fetch',fetcher);
  const hook=renderHook(({session})=>useFlagship(true,session),{initialProps:{session:0}});await flush();
  await advance(1000);expect(hook.result.current.data).toBeNull();expect(hook.result.current.error).toMatch(/Out-of-order/);
  await advance(1000);expect(hook.result.current.data).toBeNull();
  hook.rerender({session:1});expect(hook.result.current.data).toBeNull();await flush();
  expect(hook.result.current.data?.sequence).toBe(4);
});

test('changing timestamp without changing sequence is rejected',async()=>{
  const malformed=fixture();malformed.timestamp_ns+=10;
  vi.stubGlobal('fetch',vi.fn().mockResolvedValueOnce(response(fixture())).mockResolvedValue(response(malformed)));
  const hook=renderHook(()=>useFlagship(true,0));await flush();await advance(1000);
  expect(hook.result.current.data).toBeNull();expect(hook.result.current.error).toMatch(/Inconsistent/);
});

test('disabling core telemetry clears immediately and a late response cannot restore it',async()=>{
  let resolve!:(response:Response)=>void;
  const fetcher=vi.fn().mockResolvedValueOnce(response(fixture())).mockImplementation(()=>new Promise<Response>(done=>{resolve=done;}));
  vi.stubGlobal('fetch',fetcher);
  const hook=renderHook(({enabled})=>useFlagship(enabled,0),{initialProps:{enabled:true}});await flush();await advance(1000);
  hook.rerender({enabled:false});expect(hook.result.current.data).toBeNull();
  expect(fetcher.mock.calls[1][1].signal.aborted).toBe(true);
  await act(async()=>resolve(response(fixture(2))));await flush();
  expect(hook.result.current.data).toBeNull();expect(hook.result.current.error).toBe('Fleet telemetry unavailable');
});

test.each(['bad-json','oversized','unauthorized','invalid-contract'])('failed payload %s clears the old display',async failure=>{
  const rejected=failure==='bad-json'?{ok:true,text:async()=>'{'}:failure==='oversized'?{ok:true,text:async()=>'x'.repeat(1_000_001)}:failure==='unauthorized'?{ok:false}:response({...fixture(),hardware_verified:true});
  vi.stubGlobal('fetch',vi.fn().mockResolvedValueOnce(response(fixture())).mockResolvedValue(rejected));
  const hook=renderHook(()=>useFlagship(true,0));await flush();await advance(1000);
  expect(hook.result.current.data).toBeNull();expect(hook.result.current.error).not.toBe('');
});

test('unavailable observations never gain a synthetic location or freshness as time passes',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue(response(unavailable())));
  const hook=renderHook(()=>useFlagship(true,0));await flush();await advance(3500);
  expect(hook.result.current.data?.participants.every(p=>p.position===null&&p.age_ms===null&&p.state==='UNAVAILABLE')).toBe(true);
});
