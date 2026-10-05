import {useEffect,useMemo,useState} from 'react';
import type {FlagshipSnapshot} from './types';

const STALE_MS=3000;
const record=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v);
const finite=(v:unknown):v is number=>typeof v==='number'&&Number.isFinite(v);
const integer=(v:unknown):v is number=>finite(v)&&Number.isInteger(v)&&v>=0;
const text=(v:unknown):v is string=>typeof v==='string'&&v.length>0&&v.length<=4000;
const nullableNonnegative=(v:unknown)=>v===null||(finite(v)&&v>=0);
const angle=(v:unknown)=>v===null||(finite(v)&&v>=0&&v<360);
const coordinate=(v:unknown):v is [number,number]=>Array.isArray(v)&&v.length===2&&v.every(finite)&&Math.abs(v[0])<=180&&Math.abs(v[1])<=90;

function geometry(value:unknown,type:string):boolean {
  if(!record(value)||value.type!==type)return false;
  const c=value.coordinates;
  if(type==='Point')return coordinate(c);
  if(type==='LineString')return Array.isArray(c)&&c.length>=2&&c.length<=4096&&c.every(coordinate);
  return type==='Polygon'&&Array.isArray(c)&&c.length>0&&c.length<=16&&c.every(ring=>Array.isArray(ring)&&ring.length>=4&&ring.length<=4096&&ring.every(coordinate)&&ring[0][0]===ring[ring.length-1][0]&&ring[0][1]===ring[ring.length-1][1]);
}

/** Validate the actual V1 demonstration contract, including source consistency. */
export function isFlagship(value:unknown):value is FlagshipSnapshot {
  if(!record(value)||value.schema_version!=='tark.flagship.v1'||value.traction!=='DISABLED_PHASE_1'||value.monitoring_only!==true||value.hardware_verified!==false)return false;
  if(!['SIMULATION','REAL_RADAR','REPLAY'].includes(value.mode as string)||!integer(value.timestamp_ns)||!integer(value.sequence)||!Number.isSafeInteger(value.sequence)||!record(value.scene))return false;
  const simulated=value.mode==='SIMULATION';
  const source=simulated?'SIMULATION':'UNAVAILABLE';
  const timestamp=value.timestamp_ns;
  if(value.source_mode!==source||value.decision_source!=='/api/v1/status')return false;
  const s=value.scene;
  if(!text(s.id)||!text(s.label)||s.source!==source||s.review_status!==(simulated?'DEMO_FIXTURE_NOT_SURVEYED':'UNAVAILABLE_NOT_SURVEYED')||s.coordinate_system!=='WGS84_DISPLAY_ANCHOR_ONLY')return false;
  if(!coordinate(s.center)||!Array.isArray(s.bounds)||s.bounds.length!==4||!coordinate(s.bounds.slice(0,2))||!coordinate(s.bounds.slice(2))||s.bounds[0]>=s.bounds[2]||s.bounds[1]>=s.bounds[3])return false;
  for(const [key,type] of Object.entries({roads:'LineString',route:'LineString',zones:'Polygon',waypoints:'Point',hazards:'Point',history:'LineString'})) {
    const collection=s[key];
    if(!record(collection)||collection.type!=='FeatureCollection'||!Array.isArray(collection.features)||collection.features.length>200||(!simulated&&collection.features.length!==0))return false;
    if(!collection.features.every(f=>record(f)&&f.type==='Feature'&&record(f.properties)&&f.properties.source_mode==='SIMULATION'&&f.properties.operational_authority===false&&geometry(f.geometry,type)))return false;
  }
  if(!Array.isArray(value.participants)||value.participants.length!==2)return false;
  if(!value.participants.every(p=>{
    if(!record(p)||!['A','B'].includes(p.id as string)||!text(p.name)||p.role!==(p.id==='A'?'INSTRUMENTED_VEHICLE':'LOCATION_ONLY')||p.source_mode!==source||!Array.isArray(p.capabilities)||p.capabilities.length>32||!p.capabilities.every(text))return false;
    if(p.id==='B'&&(p.heading_deg!==null||p.capabilities.some(c=>!['GNSS','PEER_TELEMETRY'].includes(c))))return false;
    if(![p.speed_mps,p.accuracy_m,p.age_ms].every(nullableNonnegative)||!angle(p.course_deg)||!angle(p.heading_deg))return false;
    if(!simulated)return p.state==='UNAVAILABLE'&&p.quality==='NOT_CONNECTED'&&[p.position,p.speed_mps,p.course_deg,p.heading_deg,p.accuracy_m,p.age_ms,p.timestamp_ns].every(v=>v===null);
    return ['SIMULATED','STALE'].includes(p.state as string)&&p.quality==='SIMULATED_FIX'&&integer(p.timestamp_ns)&&p.timestamp_ns<=timestamp&&finite(p.age_ms)&&record(p.position)&&coordinate([p.position.longitude_deg,p.position.latitude_deg]);
  }))return false;
  if(new Set(value.participants.map(p=>p.id)).size!==2)return false;
  return Array.isArray(value.hardware)&&value.hardware.length<=50&&value.hardware.every(h=>record(h)&&['id','name','interface','reason'].every(k=>text(h[k]))&&h.status==='HARDWARE_PENDING'&&['MIGRATION_REQUIRED','EXISTING_BOUNDARY_REVIEW_REQUIRED'].includes(h.software_readiness as string))&&Array.isArray(value.limitations)&&value.limitations.length<=50&&value.limitations.every(text);
}

type Received={snapshot:FlagshipSnapshot;receivedAt:number;requestElapsedMs:number;session:number};

/** Browser elapsed time is added to server age, never compared to server monotonic ns. */
function aged(received:Received,now:number):FlagshipSnapshot {
  const elapsed=Math.max(0,now-received.receivedAt)+received.requestElapsedMs;
  return {...received.snapshot,participants:received.snapshot.participants.map(p=>{
    if(p.age_ms===null)return p;
    const age_ms=Math.round(p.age_ms+elapsed);
    const stale=p.state==='STALE'||age_ms>=STALE_MS;
    return {...p,age_ms,state:stale?'STALE':p.state,
      ...(stale?{course_deg:null,heading_deg:null,speed_mps:null,accuracy_m:null}:{} )};
  })};
}

/** One sequential, cancellable feed. It never opens hardware or changes the core. */
export function useFlagship(enabled:boolean,session:number) {
  const [received,setReceived]=useState<Received|null>(null);
  const [now,setNow]=useState(()=>performance.now());
  const [error,setError]=useState('Loading the demonstration course…');
  useEffect(()=>{
    setReceived(null);
    if(!enabled){setError('Fleet telemetry unavailable');return;}
    setError('Loading the demonstration course…');
    let stopped=false,timer:number|undefined,controller:AbortController|undefined;
    let last:Received|null=null;
    async function poll(){
      const requestController=new AbortController();controller=requestController;
      const started=performance.now();
      const timeout=window.setTimeout(()=>requestController.abort(),4000);
      try{
        const response=await fetch('/api/v1/flagship',{credentials:'same-origin',cache:'no-store',signal:requestController.signal});
        if(!response.ok)throw new Error('Fleet service unavailable');
        const body=await response.text();if(body.length>1_000_000)throw new Error('Oversized fleet payload rejected');
        const next:unknown=JSON.parse(body);if(!isFlagship(next))throw new Error('Invalid fleet payload rejected');
        if(last&&(next.sequence<last.snapshot.sequence||next.timestamp_ns<last.snapshot.timestamp_ns||next.mode!==last.snapshot.mode))throw new Error('Out-of-order fleet stream — reconnect to refresh');
        if(last&&((next.sequence===last.snapshot.sequence)!==(next.timestamp_ns===last.snapshot.timestamp_ns)))throw new Error('Inconsistent fleet observation rejected');
        if(!stopped){
          const arrived=performance.now();
          // Identical snapshots may be reread, but cannot reset observation age.
          if(!last||next.sequence>last.snapshot.sequence)last={snapshot:next,receivedAt:arrived,requestElapsedMs:Math.max(0,arrived-started),session};
          setReceived(last);setNow(arrived);setError('');
        }
      }catch(e){if(!stopped){setReceived(null);setError(e instanceof Error?e.message:'Fleet telemetry unavailable');}}
      finally{window.clearTimeout(timeout);if(!stopped)timer=window.setTimeout(()=>void poll(),document.hidden?5000:1000);}
    }
    void poll();return()=>{stopped=true;if(timer!==undefined)window.clearTimeout(timer);controller?.abort();};
  },[enabled,session]);

  useEffect(()=>{
    if(!enabled||!received||received.session!==session)return;
    let timer:number|undefined,stopped=false;
    const update=()=>{
      if(stopped)return;
      const tick=performance.now();setNow(tick);
      const remaining=received.snapshot.participants.filter(p=>p.age_ms!==null).map(p=>STALE_MS-(p.age_ms!+received.requestElapsedMs+Math.max(0,tick-received.receivedAt))).filter(age=>age>0);
      // One Hz labels, plus an exact expiry callback: never wait for a slow poll.
      timer=window.setTimeout(update,Math.max(1,Math.min(1000,...remaining)));
    };
    update();return()=>{stopped=true;if(timer!==undefined)window.clearTimeout(timer);};
  },[enabled,received,session]);
  const data=useMemo(()=>enabled&&received?.session===session?aged(received,now):null,[enabled,received,session,now]);
  return {data,error:!enabled?'Fleet telemetry unavailable':error};
}
