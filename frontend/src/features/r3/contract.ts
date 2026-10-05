// Additive schema. A malformed R3 extension cannot acquire a green readiness state.
export type R3Source={source_id:string;part_number:string;mode:string;evidence_origin:string|null;
  expected:boolean;detected:boolean;identity_verified:boolean;driver_ready:boolean;producing:boolean;fresh:boolean;
  plausible:boolean;time_valid:boolean;calibration_valid:boolean;qualified:boolean;qualified_for:string[];
  clock_state:string;calibration_state:string;fault_reason:string|null;age_bound_ns:number|null;rate_hz:number|null;
  counters:Record<string,number>;queue_depth:number;connection_state:string;health_state:string};
export type R3Readiness={schema_version:'TARK_READINESS_1';source_mode:string;active_profile:string;profile_id:string;
  hardware_claim:'HARDWARE_UNVERIFIED';traction:'DISABLED_PHASE_1';sources:R3Source[];configuration_bundle_id:string;
  software_version:string;calibration_bundle:string[];experiment:null|{experiment_id:string;status:string};
  timeline:{source_id:string;event:string;mode:string;arrival_ns:number}[];
  explanation:{decision_scope:string;decision_state:string;primary_reason:string;reason:string;motion_authority:false}};
const object=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v);
const text=(v:unknown):v is string=>typeof v==='string'&&v.length>0&&v.length<=512;
const number=(v:unknown):v is number=>typeof v==='number'&&Number.isFinite(v)&&v>=0;
const strings=(v:unknown):v is string[]=>Array.isArray(v)&&v.length<=32&&v.every(text);
const modes=['REAL','SIMULATION','REPLAY','UNAVAILABLE'];
function source(v:unknown):v is R3Source{
  if(!object(v)||!text(v.source_id)||!text(v.part_number)||!text(v.mode)||!modes.includes(v.mode))return false;
  const flags=['expected','detected','identity_verified','driver_ready','producing','fresh','plausible','time_valid','calibration_valid','qualified'];
  if(!flags.every(k=>typeof v[k]==='boolean')||!strings(v.qualified_for))return false;
  if(v.qualified&&(!['producing','fresh','plausible','time_valid','calibration_valid'].every(k=>v[k]===true)||v.qualified_for.length===0))return false;
  if(v.mode!=='REAL'&&v.identity_verified)return false;
  if(v.qualified&&(v.health_state!=='ONLINE'||v.connection_state!=='CONNECTED'||v.fault_reason!==null||(v.mode==='REAL'&&!v.identity_verified)))return false;
  if(v.mode==='REAL'&&v.evidence_origin!==null&&v.evidence_origin!=='REAL_CAPTURE')return false;
  if(v.mode==='SIMULATION'&&v.evidence_origin!==null&&!['SYNTHETIC_FIXTURE','SIMULATOR'].includes(String(v.evidence_origin)))return false;
  return ['clock_state','calibration_state','connection_state','health_state'].every(k=>text(v[k]))
    &&(v.fault_reason===null||text(v.fault_reason))&&(v.evidence_origin===null||text(v.evidence_origin))
    &&(v.age_bound_ns===null||number(v.age_bound_ns))&&(v.rate_hz===null||number(v.rate_hz))
    &&number(v.queue_depth)&&object(v.counters)&&Object.keys(v.counters).length<=16&&Object.values(v.counters).every(number);
}
export function readR3(value:unknown):R3Readiness|null{
  if(!object(value)||value.schema_version!=='TARK_READINESS_1'||value.traction!=='DISABLED_PHASE_1'||value.hardware_claim!=='HARDWARE_UNVERIFIED')return null;
  if(!['source_mode','active_profile','profile_id','configuration_bundle_id','software_version'].every(k=>text(value[k]))||!modes.concat('MIXED').includes(String(value.source_mode)))return null;
  if(!Array.isArray(value.sources)||value.sources.length>32||!value.sources.every(source)||new Set(value.sources.map(s=>s.source_id)).size!==value.sources.length)return null;
  if(!strings(value.calibration_bundle)||!Array.isArray(value.timeline)||value.timeline.length>100||!value.timeline.every(x=>object(x)&&text(x.source_id)&&text(x.event)&&text(x.mode)&&number(x.arrival_ns)))return null;
  if(value.experiment!==null&&(!object(value.experiment)||!text(value.experiment.experiment_id)||!text(value.experiment.status)))return null;
  const why=value.explanation;
  if(!object(why)||why.motion_authority!==false||!['decision_scope','decision_state','primary_reason','reason'].every(k=>text(why[k])))return null;
  return value as R3Readiness;
}
