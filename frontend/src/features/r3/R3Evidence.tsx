import {useState,type FormEvent} from 'react';
import {readR3,type R3Readiness} from './contract';
import './r3.css';

export function EvidenceWhy({value}:{value:unknown}){
  const data=readR3(value);
  return <details className="r2-details"><summary>Why? Evidence scope</summary>{data?<><p><b>{data.explanation.decision_state}</b> · {data.explanation.primary_reason}</p><p>{data.explanation.reason}</p><p>Scope: {data.explanation.decision_scope}. Configuration: {data.configuration_bundle_id}.</p><p>{data.sources.filter(s=>!s.qualified).length} R3 sources are not qualified. This does not alter the legacy advisory.</p></>:<p>R3 evidence explanation unavailable. No readiness is inferred.</p>}</details>;
}
function ExperimentControls({data,enabled}:{data:R3Readiness;enabled:boolean}){
  const [status,setStatus]=useState(''),[busy,setBusy]=useState(false);
  const [catalog,setCatalog]=useState<{id:string;status:string;recording:string|null;result:string;ticks:number|null}[]|null>(null);
  async function loadCatalog(){setBusy(true);try{
    const response=await fetch('/api/v2/r3/experiments',{credentials:'same-origin'});
    if(!response.ok)throw new Error('unavailable');
    const rows:unknown=await response.json();
    if(!Array.isArray(rows)||rows.length>1000)throw new Error('invalid catalog');
    const latest=rows.slice(0,10).map(row=>{
      if(!row||typeof row!=='object'||typeof row.experiment_id!=='string'||row.experiment_id.length>128||!['ACTIVE','COMPLETE','INTERRUPTED'].includes(row.status)||!(row.recording_id===null||typeof row.recording_id==='string'))throw new Error('invalid experiment');
      const result=row.summary?.replay_result?.result,ticks=row.summary?.recorded_ticks;
      return {id:row.experiment_id,status:row.status,recording:row.recording_id,result:['MATCH','MISMATCH','NOT RECOMPUTABLE'].includes(result)?result:'NOT VERIFIED',ticks:typeof ticks==='number'&&Number.isSafeInteger(ticks)&&ticks>=0?ticks:null};
    });
    setCatalog(latest);setStatus('Catalog loaded. Counts are recorded software evidence, not physical results.');
  }catch{setCatalog(null);setStatus('Experiment catalog unavailable or invalid. No result inferred.');}finally{setBusy(false);}}
  async function create(event:FormEvent<HTMLFormElement>){
    event.preventDefault();const form=new FormData(event.currentTarget);setBusy(true);
    try{
      const result=await fetch('/api/v2/r3/experiments',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({
        experiment_id:form.get('experiment_id'),title:form.get('title'),scenario:form.get('scenario'),operator:form.get('operator'),date:new Date().toISOString(),
        hardware_profile:data.profile_id,configuration_bundle:data.configuration_bundle_id,calibration_bundle:data.calibration_bundle,
        software_version:data.software_version,expected_sources:data.sources.map(s=>s.source_id),visibility_condition:form.get('condition'),notes:form.get('notes')})});
      setStatus(result.ok?'Experiment created. Start its recording on Replay.':'Experiment rejected; check current bundle and active recording.');
    }catch{setStatus('Experiment service unavailable. No configuration changed.');}finally{setBusy(false);}
  }
  async function finish(){setBusy(true);try{const response=await fetch('/api/v2/r3/experiments/finish',{method:'POST',credentials:'same-origin'});setStatus(response.ok?'Experiment closed; retained in the experiment catalog.':'Stop the recording before closing its experiment.');}catch{setStatus('Experiment service unavailable.');}finally{setBusy(false);}}
  return <section className="r2-card r3-experiment"><h3>Engineering experiment</h3><p>Active: {data.experiment?.experiment_id??'NONE'} · {data.experiment?.status??'No experiment started'}</p>{!enabled?<p>Monitoring-only deployment: experiment writes unavailable.</p>:data.experiment?<button disabled={busy} onClick={()=>void finish()}>Finish experiment</button>:<details><summary>Create a local experiment</summary><form onSubmit={event=>void create(event)} className="r3-experiment-form">{[['experiment_id','Experiment ID'],['title','Experiment title'],['scenario','Scenario'],['operator','Operator'],['condition','Test / visibility condition']].map(([name,label])=><label key={name}>{label}<input required name={name} maxLength={name==='title'?200:128}/></label>)}<label>Notes<textarea name="notes" maxLength={2000}/></label><p>Uses the current versioned bundle. Does not configure or open hardware.</p><button disabled={busy} type="submit">Create experiment</button></form></details>}<button disabled={busy} onClick={()=>void loadCatalog()}>Load experiment catalog</button>{catalog&&<div aria-label="Recent experiments"><p>Most recent {catalog.length} experiments. Replay results apply to normalized evidence qualification only.</p>{catalog.length===0&&<p>No experiments recorded.</p>}{catalog.map(row=><p key={row.id}><b>{row.id}</b> · {row.status}<br/>Recording: {row.recording??'NONE'}<br/>Recorded ticks: {row.ticks??'UNKNOWN'} · R3 replay: {row.result}</p>)}</div>}<p role="status">{status}</p></section>;
}
export function R3Evidence({value,engineeringWrites=false}:{value:unknown;engineeringWrites?:boolean}){
  const data=readR3(value);
  if(!data)return <section className="r2-card"><h2>R3 evidence readiness</h2><p role="status">Unavailable or invalid R3 evidence contract. Hardware readiness is not inferred.</p></section>;
  return <section className="r3-evidence" aria-label="R3 evidence readiness"><div className="r2-callout"><p><b>R3 {data.source_mode} · HARDWARE UNVERIFIED</b><br/>Active profile: {data.active_profile}. Expected is not detected. Connected is not qualified.</p></div><div className="r3-source-grid">{data.sources.map(s=><article className="r2-card" key={s.source_id}><h3>{s.source_id} <small>{s.part_number}</small></h3><p><b>{s.mode}</b> · {s.evidence_origin??'NO EVIDENCE'}</p><dl className="r3-stages">{(['expected','detected','identity_verified','driver_ready','producing','fresh','plausible','time_valid','calibration_valid','qualified'] as const).map(key=><div key={key}><dt>{key.replaceAll('_',' ')}</dt><dd>{s[key]?'YES':'NO'}</dd></div>)}</dl><p>{s.qualified?`Purpose: ${s.qualified_for.join(', ')}`:`Not qualified: ${s.fault_reason??'EVIDENCE INSUFFICIENT'}`}</p><p>Clock: {s.clock_state}<br/>Calibration: {s.calibration_state}<br/>Capture-age bound: {s.age_bound_ns===null?'UNKNOWN':`${(s.age_bound_ns/1e6).toFixed(1)} ms`}<br/>Observed arrival rate: {s.rate_hz===null?'UNKNOWN':`${s.rate_hz.toFixed(1)} Hz`}<br/>Queue: {s.queue_depth} · Drops: {s.counters.drops??0} · Rejected: {s.counters.invalid??0}</p>{s.source_id==='gnss-b'&&<p>Cooperative evidence only. Ordinary local Wi-Fi; not local detection of an unequipped target. A normalized fixture is not proof of a radio link.</p>}</article>)}</div><EvidenceWhy value={value}/><ExperimentControls data={data} enabled={engineeringWrites}/><details className="r2-details"><summary>Source evidence timeline ({data.timeline.length} retained)</summary><ol>{data.timeline.slice(-20).map((event,i)=><li key={`${event.source_id}-${event.arrival_ns}-${i}`}>{event.source_id} · {event.mode} · {event.event} · host arrival {event.arrival_ns} ns</li>)}</ol>{!data.timeline.length&&<p>No R3 observation has arrived.</p>}</details></section>;
}
