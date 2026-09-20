import type { Snapshot } from './types';

export type ConnectionState='CONNECTING'|'CONNECTED'|'DEGRADED'|'RECONNECTING'|'OFFLINE';
export class ApiError extends Error { constructor(public readonly status:number,message:string){super(message);} }

function isRecord(value:unknown):value is Record<string,unknown>{return typeof value==='object'&&value!==null;}
export function isSnapshot(value:unknown):value is Snapshot{
  if(!isRecord(value)||typeof value.mode!=='string'||typeof value.traction!=='string'||!isRecord(value.decision)||!isRecord(value.command))return false;
  if(value.traction!=='DISABLED_PHASE_1')return false;
  const decision=value.decision,command=value.command;
  return typeof decision.state==='string'&&typeof decision.permitted_speed_mps==='number'&&Number.isFinite(decision.permitted_speed_mps)&&typeof decision.reason_code==='string'&&typeof command.sequence==='number'&&Array.isArray(value.tracks)&&Array.isArray(value.sensors)&&Array.isArray(value.events);
}
export function websocketUrl(locationLike:Pick<Location,'protocol'|'host'>=window.location):string{
  return `${locationLike.protocol==='https:'?'wss':'ws'}://${locationLike.host}/api/v1/ws`;
}
async function request(path:string,init?:RequestInit):Promise<Response>{
  const response=await fetch(path,{credentials:'same-origin',...init});
  if(!response.ok)throw new ApiError(response.status,`API ${response.status}`);
  return response;
}
export type GeographicPoint={latitude:number;longitude:number};
export type AddressHierarchy={provider:string;country?:string|null;state?:string|null;district?:string|null;city?:string|null;locality?:string|null;road?:string|null;display_name?:string|null};
export type RouteResult={provider:string;distance_m:number;duration_s:number;coordinates:[number,number][];instructions:string[]};
export type VehicleLocationStatus={state:string;reason:string;breadcrumbs?:{latitude_deg:number;longitude_deg:number;timestamp_ns:number;source:string}[];location:null|{vehicle_id:string;timestamp_ns:number;source:'GNSS'|'SIMULATION'|'REPLAY'|'UNKNOWN';latitude_deg:number;longitude_deg:number;altitude_m?:number|null;speed_mps?:number|null;heading_deg?:number|null;horizontal_accuracy_m?:number|null;vertical_accuracy_m?:number|null;fix_type:string;satellites?:number|null;freshness_ms?:number|null;quality:string;status:string}};
export type CameraStatus={source_id:string;source_mode:string;state:string;timestamp_ns:number|null;age_ms:number|null;resolution:string|null;frame_rate_fps:number|null;reason:string;stream_url:string|null;stream_transport:string;hardware_claim:string;camera_id?:string|null;device_path?:string|null;pixel_format?:string|null;sequence?:number|null;dropped_frames?:number;backend?:string|null};
export type RecordingSession={session_id:string;started_ns:number;stopped_ns:number|null;source_mode:string;configuration_hash:string;status:'RECORDING'|'COMPLETE'|'FULL'|'INTERRUPTED';max_records:number;record_count:number};
export type ReplayTimelineItem={position:number;sequence:number;timestamp_ns:number;source_mode:'REPLAY';original_source_mode:string;decision:{state:string;reason_code:string;permitted_speed_mps:number};event:{event_type:string;severity:string;reason:string};command:{sequence:number};track_count:number};
export type ReplayTimeline={session_id:string;source_mode:'REPLAY';state:'READY'|'NO_REPLAYABLE_OBSERVATIONS';items:ReplayTimelineItem[];start_timestamp_ns:number|null;end_timestamp_ns:number|null;duration_ns:number;configuration_hash:string};
async function jsonRequest<T>(path:string,init?:RequestInit):Promise<T>{return await (await request(path,init)).json() as T;}
export async function reverseGeocode(point:GeographicPoint):Promise<AddressHierarchy>{return jsonRequest('/api/v1/location/reverse',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(point)});}
export async function calculateRoute(start:GeographicPoint,destination:GeographicPoint):Promise<RouteResult>{return jsonRequest('/api/v1/routes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({start,destination})});}
export async function getVehicleLocation():Promise<VehicleLocationStatus>{return jsonRequest('/api/v1/vehicle-location');}
export async function getVehicleCameraStatus():Promise<CameraStatus>{return jsonRequest('/api/v1/cameras/vehicle-rgb');}
export async function getReplaySessions():Promise<RecordingSession[]>{return jsonRequest('/api/v1/replay/sessions');}
export async function getReplaySession(sessionId:string):Promise<RecordingSession>{return jsonRequest(`/api/v1/replay/sessions/${encodeURIComponent(sessionId)}`);}
export async function getReplayTimeline(sessionId:string):Promise<ReplayTimeline>{return jsonRequest(`/api/v1/replay/sessions/${encodeURIComponent(sessionId)}/timeline`);}
export async function startRecording():Promise<RecordingSession>{return jsonRequest('/api/v1/recordings/start',{method:'POST'});}
export async function stopRecording():Promise<RecordingSession>{return jsonRequest('/api/v1/recordings/stop',{method:'POST'});}
export async function verifyReplay(sessionId:string):Promise<{session_id:string;result:'MATCH'|'MISMATCH';first_divergence:number|null}>{return jsonRequest(`/api/v1/replay/sessions/${encodeURIComponent(sessionId)}/verify`,{method:'POST'});}
export async function getSnapshot():Promise<Snapshot>{const value:unknown=await (await request('/api/v1/status')).json();if(!isSnapshot(value))throw new Error('Invalid status payload rejected');return value;}
export async function authenticate(accessToken:string):Promise<void>{await request('/api/v1/auth/session',{method:'POST',headers:{Authorization:`Bearer ${accessToken}`}});}
const locationSources=new Set(['GNSS','SIMULATION','REPLAY','UNKNOWN']);
function validCoordinate(latitude:unknown,longitude:unknown):boolean{return typeof latitude==='number'&&Number.isFinite(latitude)&&latitude>=-90&&latitude<=90&&typeof longitude==='number'&&Number.isFinite(longitude)&&longitude>=-180&&longitude<=180;}
export function isVehicleLocationStatus(value:unknown):value is VehicleLocationStatus{
  if(!isRecord(value)||typeof value.state!=='string'||typeof value.reason!=='string'||!('location' in value))return false;
  if(value.breadcrumbs!==undefined&&(!Array.isArray(value.breadcrumbs)||!value.breadcrumbs.every(item=>isRecord(item)&&validCoordinate(item.latitude_deg,item.longitude_deg)&&typeof item.timestamp_ns==='number'&&Number.isFinite(item.timestamp_ns)&&typeof item.source==='string'&&locationSources.has(item.source))))return false;
  if(value.location===null)return true;
  const location=value.location;
  return isRecord(location)&&typeof location.vehicle_id==='string'&&typeof location.timestamp_ns==='number'&&Number.isFinite(location.timestamp_ns)&&typeof location.source==='string'&&locationSources.has(location.source)&&validCoordinate(location.latitude_deg,location.longitude_deg)&&typeof location.fix_type==='string'&&typeof location.quality==='string'&&typeof location.status==='string'&&(location.heading_deg===undefined||location.heading_deg===null||(typeof location.heading_deg==='number'&&Number.isFinite(location.heading_deg)&&location.heading_deg>=0&&location.heading_deg<360))&&(location.horizontal_accuracy_m===undefined||location.horizontal_accuracy_m===null||(typeof location.horizontal_accuracy_m==='number'&&Number.isFinite(location.horizontal_accuracy_m)&&location.horizontal_accuracy_m>=0));
}
export function connect(onSnapshot:(s:Snapshot)=>void,onState:(state:ConnectionState,message?:string)=>void,onLocation?:(location:VehicleLocationStatus)=>void){
  let socket:WebSocket|undefined,stopped=false,retry:number|undefined,stale:number|undefined,attempt=0,lastStatus=0;
  const clearTimers=()=>{if(retry!==undefined)window.clearTimeout(retry);if(stale!==undefined)window.clearInterval(stale);};
  const scheduleStaleCheck=()=>{if(stale!==undefined)window.clearInterval(stale);stale=window.setInterval(()=>{if(Date.now()-lastStatus>3_000)onState('DEGRADED','Telemetry stale — retaining no new authority in browser.');},1_000);};
  const open=()=>{if(stopped)return;onState(attempt?'RECONNECTING':'CONNECTING');socket=new WebSocket(websocketUrl());socket.onopen=()=>{attempt=0;scheduleStaleCheck();};socket.onmessage=event=>{try{const message:unknown=JSON.parse(event.data);if(!isRecord(message)){onState('DEGRADED','Malformed WebSocket payload rejected');return;}if(message.type==='status'){if(!isSnapshot(message.payload)){onState('DEGRADED','Invalid WebSocket payload rejected');return;}lastStatus=Date.now();onSnapshot(message.payload);onState('CONNECTED');return;}if(message.type==='location_update'){if(isVehicleLocationStatus(message.payload))onLocation?.(message.payload);return;}onState('DEGRADED','Invalid WebSocket payload rejected');}catch{onState('DEGRADED','Malformed WebSocket payload rejected');}};socket.onerror=()=>onState('DEGRADED','WebSocket unavailable — dashboard is observation only');socket.onclose=event=>{if(stopped)return;clearTimers();if(event.code===1008){onState('OFFLINE','Authentication required for telemetry.');return;}attempt+=1;const delay=Math.min(15_000,1_000*2**Math.min(attempt-1,4));onState('RECONNECTING',`Reconnecting telemetry in ${Math.ceil(delay/1000)} s`);retry=window.setTimeout(open,delay);};};
  open();return()=>{stopped=true;clearTimers();socket?.close();};
}
