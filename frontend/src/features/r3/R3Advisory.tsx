import './r3.css';
type Row=Record<string,unknown>;
const object=(v:unknown):v is Row=>!!v&&typeof v==='object'&&!Array.isArray(v);
const token=(v:unknown):v is string=>typeof v==='string'&&v.length>0&&v.length<=128;
const number=(v:unknown):v is number=>typeof v==='number'&&Number.isFinite(v)&&v>=0;
const nullable=(v:unknown)=>v===null||number(v);
const tokens=(v:unknown):v is string[]=>Array.isArray(v)&&v.length<=256&&v.every(token);
type Advisory={state:string;advisory:string;limiting_reason:string;source_mode:string;advised_speed_mps:number|null;stopping_requirement_m:number|null;
 configuration_id:string;configuration_hash:string;software_fingerprint:string;vehicle_profile:{profile:string;provenance:string};
 observability:{forward_range_m:number|null;provenance:string;road_clear_claim:false};qualified_sources:string[];excluded_sources:Record<string,string>;
 semantic_observations:{source_id:string;purposes:string[];exclusion_reason:string|null}[];
 tracks:{track_id:string;relevance:string;association:string;lifecycle:string}[];ttc:{track_id:string;value_s:number|null;valid:boolean;reason:string}[];cooperative_context:unknown[]};

export function readAdvisory(value:unknown):Advisory|null{
 if(!object(value)||!object(value.advisory))return null;
 const a=value.advisory;
 if(a.decision_version!=='TARK_R3_ADVISORY_1'||!['NORMAL','WARN','RESTRICT','UNKNOWN','STOP'].includes(String(a.state))||a.motion_authority!==false||a.hardware_verified!==false||a.traction!=='DISABLED_PHASE_1')return null;
 if(!['advisory','limiting_reason','source_mode','configuration_id','configuration_hash','software_fingerprint'].every(k=>token(a[k]))||!nullable(a.advised_speed_mps)||!nullable(a.stopping_requirement_m))return null;
 if(a.state==='UNKNOWN'&&a.advised_speed_mps!==null)return null;
 if(!object(a.observability)||!nullable(a.observability.forward_range_m)||!token(a.observability.provenance)||a.observability.road_clear_claim!==false)return null;
 if(!object(a.vehicle_profile)||!token(a.vehicle_profile.profile)||!token(a.vehicle_profile.provenance)||!tokens(a.qualified_sources))return null;
 if(!object(a.excluded_sources)||Object.keys(a.excluded_sources).length>32||!Object.entries(a.excluded_sources).every(([k,v])=>token(k)&&token(v)))return null;
 if(!Array.isArray(a.semantic_observations)||a.semantic_observations.length>32||!a.semantic_observations.every(s=>object(s)&&token(s.source_id)&&tokens(s.purposes)&&(s.exclusion_reason===null||token(s.exclusion_reason))))return null;
 if(!Array.isArray(a.tracks)||a.tracks.length>64||!a.tracks.every(t=>object(t)&&['track_id','relevance','association','lifecycle'].every(k=>token(t[k]))))return null;
 if(!Array.isArray(a.ttc)||a.ttc.length>64||!a.ttc.every(t=>object(t)&&token(t.track_id)&&nullable(t.value_s)&&typeof t.valid==='boolean'&&token(t.reason)&&(t.valid?t.value_s!==null:t.value_s===null)))return null;
 if(!Array.isArray(a.cooperative_context)||a.cooperative_context.length>8)return null;
 return a as unknown as Advisory;
}
const display=(n:number|null,unit:string)=>n===null?'Unavailable':`${n.toFixed(2)} ${unit}`;
const words=(s:string)=>s.replaceAll('_',' ').toLowerCase();

export function R3Advisory({value,compact=false}:{value:unknown;compact?:boolean}){
 const d=readAdvisory(value);
 if(!d)return <section className="r2-card r3-advisory" aria-label="R3 advisory"><h2>R3_ADVISORY</h2><p role="status">Unavailable or invalid advisory. No operating capability inferred.</p></section>;
 return <section className="r2-card r3-advisory" aria-label="R3 advisory"><div className="card-heading"><h2>R3_ADVISORY</h2><span className="small-badge">{d.source_mode} · RESEARCH</span></div>
 <p className="r3-action"><b>{d.state}</b> — {words(d.advisory)}</p><p>Reason: {words(d.limiting_reason)}.</p>
 <p className="r3-boundary">Advisory only · no motor authority · hardware unverified.</p>
 {!compact&&<><div className="r3-advisory-metrics"><div><span>Research speed ceiling</span><b>{display(d.advised_speed_mps,'m/s')}</b></div><div><span>Forward observability</span><b>{display(d.observability.forward_range_m,'m')}</b></div><div><span>Stopping requirement</span><b>{display(d.stopping_requirement_m,'m')}</b></div></div>
 <p>{d.vehicle_profile.profile} · {d.vehicle_profile.provenance}. Coverage: {d.observability.provenance}. Not a road-clear claim. Wheel response is not ground-truth speed.</p>
 <details><summary>Why? Sources, hazards and provenance</summary><p>Contributing: {d.qualified_sources.join(', ')||'NONE'}</p>{d.semantic_observations.map(s=><p key={s.source_id}><b>{s.source_id}</b> — {s.purposes.join(', ')||'EXCLUDED'}{s.exclusion_reason?` · ${s.exclusion_reason}`:''}</p>)}{Object.entries(d.excluded_sources).map(([s,r])=><p key={s}>{s}: {r}</p>)}
 <h3>Local tracks</h3>{!d.tracks.length&&<p>No retained local tracks. This does not prove the road is clear.</p>}{d.tracks.map(t=><p key={t.track_id}>{t.track_id} · {t.lifecycle} · {t.relevance} · {t.association}</p>)}
 {d.ttc.map(t=><p key={t.track_id}>TTC {t.track_id}: {t.valid?display(t.value_s,'s'):'Unavailable'} · {t.reason}</p>)}<p>Qualified cooperative peers: {d.cooperative_context.length}. Separate from local radar tracks; no detection claim for unequipped vehicles.</p>
 <p>Configuration: {d.configuration_id}<br/>Hash: {d.configuration_hash}<br/>Software: {d.software_fingerprint}</p></details></>}
 </section>;
}
