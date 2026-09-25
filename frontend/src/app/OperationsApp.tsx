import {lazy,Suspense,useEffect,useRef,useState,type FormEvent} from 'react';
import {ApiError,authenticate,connect,getSnapshot,getVehicleLocation,type ConnectionState,type VehicleLocationStatus} from '../api';
import type {Snapshot} from '../types';
import {ErrorBoundary} from '../components/ErrorBoundary';
import {DriverView} from '../features/dashboard/DriverView';
import {SupervisorView} from '../features/supervisor/SupervisorView';
import {OwnerView} from '../features/owner/OwnerView';
import {SensorMatrix} from '../features/sensors/SensorMatrix';
import {CameraPanels} from '../features/sensors/CameraPanels';
import {EventTimeline} from '../features/events/EventTimeline';
import {ReplayPanel} from '../features/replay/ReplayPanel';
import {Diagnostics} from '../features/diagnostics/Diagnostics';
import {SettingsView,type DiagnosticsData} from '../features/settings/SettingsView';

const MapView=lazy(()=>import('../MapView'));
const pages=['Dashboard','Map','Sensors','Safety','Logs','Replay','Diagnostics','Settings'] as const;
type Page=typeof pages[number];
type Role='DRIVER'|'SUPERVISOR'|'OWNER / FLEET';

function ConnectionBadge({state}:{state:ConnectionState}){return <span className={`connection ${state.toLowerCase()}`} aria-live="polite" aria-label={`Telemetry ${state}`}>Telemetry: {state}</span>}
function AccessPrompt({onSubmit}:{onSubmit:(token:string)=>Promise<void>}){const [token,setToken]=useState(''),[error,setError]=useState('');async function submit(event:FormEvent){event.preventDefault();try{await onSubmit(token);}catch{setError('Access was not accepted. Confirm the deployment access token.');}}return <main className="loading"><h1>Protected TARK HMI</h1><p>Authentication is required by this deployment. This access boundary does not grant motion authority.</p><form onSubmit={submit}><label>Access token <input aria-label="Access token" type="password" value={token} onChange={event=>setToken(event.target.value)} autoComplete="current-password"/></label><button type="submit">Open monitoring HMI</button></form>{error&&<p className="issue">{error}</p>}</main>}

export function OperationsApp(){
  const [page,setPage]=useState<Page>('Dashboard');
  const [role,setRole]=useState<Role>('DRIVER');
  const [snapshot,setSnapshot]=useState<Snapshot|null>(null);
  const [connection,setConnection]=useState<ConnectionState>('CONNECTING');
  const [issue,setIssue]=useState('Connecting to TARK service…');
  const [accessRequired,setAccessRequired]=useState(false);
  const [sessionVersion,setSessionVersion]=useState(0);
  const [lastTelemetry,setLastTelemetry]=useState<number|null>(null);
  const [diagnostics,setDiagnostics]=useState<DiagnosticsData|null>(null);
  const [vehicleLocation,setVehicleLocation]=useState<VehicleLocationStatus|null>(null);
  const telemetryGeneration=useRef(0);

  const load=async()=>{const generation=telemetryGeneration.current;try{const next=await getSnapshot();if(generation!==telemetryGeneration.current)return;setSnapshot(next);setLastTelemetry(Date.now());setIssue('');setAccessRequired(false);const location=await getVehicleLocation();if(generation===telemetryGeneration.current)setVehicleLocation(location);}catch(error){if(generation!==telemetryGeneration.current)return;setSnapshot(null);setVehicleLocation(null);if(error instanceof ApiError&&error.status===401)setAccessRequired(true);else setIssue('SERVER STARTING or telemetry unavailable — dashboard has no authority.');}};
  useEffect(()=>{void load();fetch('/api/v1/diagnostics',{credentials:'same-origin'}).then(response=>response.ok?response.json():null).then(setDiagnostics).catch(()=>undefined);const stop=connect(next=>{telemetryGeneration.current+=1;setSnapshot(next);setLastTelemetry(Date.now());setIssue('');},(state,message)=>{setConnection(state);if(state==='DEGRADED'||state==='OFFLINE'||state==='RECONNECTING'){telemetryGeneration.current+=1;setSnapshot(null);setVehicleLocation(null);setIssue(message||'TELEMETRY UNAVAILABLE — previous values are not current.');}else if(message)setIssue(message);},setVehicleLocation);return()=>{telemetryGeneration.current+=1;stop();};},[sessionVersion]);

  if(accessRequired)return <AccessPrompt onSubmit={async token=>{await authenticate(token);setSessionVersion(value=>value+1);await load();}}/>;
  if(!snapshot)return <main className="loading"><ConnectionBadge state={connection}/><p>{issue}</p><p>Simulation/hardware status has not been received; no values are invented.</p></main>;

  let body:JSX.Element;
  switch(page){
    case 'Dashboard': body=role==='DRIVER'?<DriverView snapshot={snapshot}/>:role==='SUPERVISOR'?<SupervisorView snapshot={snapshot}/>:<OwnerView snapshot={snapshot}/>; break;
    case 'Map': body=<ErrorBoundary label="Map service unavailable"><Suspense fallback={<section className="panel">Loading map resources…</section>}><MapView snapshot={snapshot} vehicleLocation={vehicleLocation} mapConfig={diagnostics?.map}/></Suspense></ErrorBoundary>; break;
    case 'Sensors': body=<><ErrorBoundary label="Sensor panel unavailable"><SensorMatrix snapshot={snapshot}/></ErrorBoundary><CameraPanels browserPreviewEnabled={diagnostics?.capabilities?.browser_camera_preview===true}/></>; break;
    case 'Safety': body=<SupervisorView snapshot={snapshot}/>; break;
    case 'Logs': body=<ErrorBoundary label="Event log unavailable"><EventTimeline snapshot={snapshot}/></ErrorBoundary>; break;
    case 'Replay': body=<ErrorBoundary label="Replay unavailable"><ReplayPanel recordingControlsAvailable={diagnostics!==null&&diagnostics.deployment_environment!=='public_demo'}/></ErrorBoundary>; break;
    case 'Diagnostics': body=<ErrorBoundary label="Diagnostics unavailable"><Diagnostics diagnostics={diagnostics}/></ErrorBoundary>; break;
    case 'Settings': body=<ErrorBoundary label="Settings unavailable"><SettingsView diagnostics={diagnostics} connection={connection} lastTelemetry={lastTelemetry}/></ErrorBoundary>; break;
  }

  return <div className="app"><header><div><b>TARK</b><small>Terrain Aware Responsive Kernel · SIH26007 · Research Prototype · NOT PHYSICALLY VALIDATED</small></div><div className="header-status"><strong>{snapshot.mode}</strong><span>HARDWARE NOT CONNECTED</span><span>TRACTION DISABLED — PHASE 1</span><ConnectionBadge state={connection}/><select aria-label="Role" value={role} onChange={event=>setRole(event.target.value as Role)}>{(['DRIVER','SUPERVISOR','OWNER / FLEET'] as Role[]).map(value=><option key={value}>{value}</option>)}</select></div></header><aside aria-label="Primary navigation">{pages.map(value=><button key={value} aria-current={page===value?'page':undefined} className={page===value?'active':''} onClick={()=>setPage(value)}>{value}</button>)}<p>Monitoring only.<br/>No browser motion authority.</p></aside><section className="workspace">{issue&&connection!=='CONNECTED'&&<div className="issue" role="status">{issue}</div>}{body}</section></div>;
}
