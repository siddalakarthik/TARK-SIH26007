import {useEffect,useRef,useState} from 'react';
import {getVehicleCameraStatus,type CameraStatus} from '../../api';

const unavailable:CameraStatus={source_id:'vehicle_rgb_camera',source_mode:'NOT_CONNECTED_PHASE_2',state:'NOT_CONNECTED',timestamp_ns:null,age_ms:null,resolution:null,frame_rate_fps:null,reason:'CAMERA NOT CONNECTED',stream_url:null,stream_transport:'PENDING_PI_UVC_INTEGRATION',hardware_claim:'NOT_CONNECTED'};

const positive=(value:unknown)=>typeof value==='number'&&Number.isFinite(value)&&value>=0;
function validCamera(camera:CameraStatus):boolean {
  if(!camera||typeof camera!=='object'||!['source_id','source_mode','state','reason','stream_transport','hardware_claim'].every(key=>typeof camera[key as keyof CameraStatus]==='string'))return false;
  if(![camera.age_ms,camera.timestamp_ns,camera.frame_rate_fps].every(value=>value===null||positive(value)))return false;
  if(camera.resolution!==null&&typeof camera.resolution!=='string')return false;
  if(camera.stream_url!==null&&camera.stream_url!=='/api/v1/cameras/vehicle-rgb/stream')return false;
  if(camera.state==='ONLINE')return positive(camera.age_ms)&&positive(camera.timestamp_ns)&&['PI_UVC','SIMULATION','REPLAY'].includes(camera.source_mode)&&(camera.source_mode!=='PI_UVC'||camera.hardware_claim==='REAL_PI_UVC');
  return true;
}

function CameraMetadata({camera,onStreamError}:{camera:CameraStatus;onStreamError:()=>void}){
  const hasStream=camera.state==='ONLINE'&&!!camera.stream_url;
  const live=camera.source_mode==='PI_UVC'&&hasStream&&camera.hardware_claim==='REAL_PI_UVC';
  const label=camera.source_mode==='PI_UVC'?'PI UVC CAMERA':camera.source_mode==='SIMULATION'?'SIMULATION CAMERA':camera.source_mode==='REPLAY'?'REPLAY CAMERA':camera.source_mode;
  const availability=camera.reason==='CAMERA NOT CONNECTED'?'No vehicle camera frame is available.':camera.reason;
  return <article className="vehicle-camera"><b>VEHICLE RGB CAMERA</b><span className={`camera-state ${camera.state.toLowerCase()}`}>{live?'● LIVE VEHICLE CAMERA':camera.state==='NOT_CONNECTED'?'CAMERA NOT CONNECTED':camera.state}</span>
    <small>Selected flagship: Arducam B0200 IMX291 · UVC</small>
    {hasStream?<img className="vehicle-camera-video" src={camera.stream_url!} alt={live?'Live vehicle RGB camera stream':'Simulated or replay camera stream'} onError={onStreamError}/>:<div className="camera-empty" role="status">{availability}</div>}
    <small>Source: {label} · selected-device identity is not established by a video frame.</small>
    <small>Resolution: {camera.resolution??'UNAVAILABLE'} · FPS: {camera.frame_rate_fps??'UNAVAILABLE'}</small>
    <small>Frame age at latest status: {camera.age_ms===null?'UNAVAILABLE':`${Math.round(camera.age_ms)} ms`} · Pixel format: {camera.pixel_format??'UNAVAILABLE'}</small>
    <small>Host frame timestamp: {camera.timestamp_ns??'UNAVAILABLE'}{camera.timestamp_ns!==null?' ns · monotonic':''}</small>
    <small>Sequence: {camera.sequence??'UNAVAILABLE'} · Dropped: {camera.dropped_frames??'UNAVAILABLE'} · Hardware: {camera.hardware_claim}</small></article>;
}

export function CameraPanels({browserPreviewEnabled}:{browserPreviewEnabled:boolean}){
  const video=useRef<HTMLVideoElement>(null),stream=useRef<MediaStream|null>(null);
  const alive=useRef(false),allowed=useRef(browserPreviewEnabled),requestId=useRef(0),pending=useRef(false);
  allowed.current=browserPreviewEnabled;
  const [state,setState]=useState('DEVELOPMENT BROWSER CAMERA NOT STARTED'),[active,setActive]=useState(false),[starting,setStarting]=useState(false),[camera,setCamera]=useState<CameraStatus>(unavailable);
  const stopTracks=()=>{stream.current?.getTracks().forEach(track=>track.stop());stream.current=null;if(video.current)video.current.srcObject=null;};

  useEffect(()=>{alive.current=true;return()=>{alive.current=false;requestId.current++;stopTracks();};},[]);
  useEffect(()=>{
    let cancelled=false,timer:number|undefined,expiry:number|undefined,requestTimeout:number|undefined,controller:AbortController|undefined;
    let previous:{timestamp:number;source:string;receivedAt:number;age:number}|null=null;
    const clearExpiry=()=>{if(expiry!==undefined)window.clearTimeout(expiry);};
    const offline=(reason:string)=>{clearExpiry();if(!cancelled)setCamera({...unavailable,state:'UNAVAILABLE',reason});};
    async function refresh(){
      const current=new AbortController();controller=current;const started=performance.now();
      const timeout=window.setTimeout(()=>{current.abort();offline('CAMERA STATUS TIMED OUT — NO CURRENT FRAME');},4000);requestTimeout=timeout;
      try{
        const value=await getVehicleCameraStatus(current.signal);
        if(cancelled||current.signal.aborted)return;
        if(!validCamera(value))throw new Error('Invalid camera metadata');
        const receivedAt=performance.now();let age=value.age_ms;
        if(value.timestamp_ns!==null&&age!==null){
          age+=Math.max(0,receivedAt-started);
          if(previous?.source===value.source_mode){
            if(value.timestamp_ns<previous.timestamp)throw new Error('Out-of-order camera metadata');
            if(value.timestamp_ns===previous.timestamp)age=Math.max(age,previous.age+Math.max(0,receivedAt-previous.receivedAt));
          }
          previous={timestamp:value.timestamp_ns,source:value.source_mode,receivedAt,age};
        }
        clearExpiry();
        const stale=value.state==='ONLINE'&&age!==null&&age>=3000;
        setCamera({...value,age_ms:age,...(stale?{state:'STALE',stream_url:null,reason:'CAMERA STATUS EXPIRED — NO CURRENT FRAME'}:{})});
        if(value.state==='ONLINE'&&!stale&&age!==null)expiry=window.setTimeout(()=>{if(!cancelled)setCamera(currentCamera=>({...currentCamera,state:'STALE',stream_url:null,age_ms:3000,reason:'CAMERA STATUS EXPIRED — NO CURRENT FRAME'}));},Math.max(1,3000-age));
      }catch{if(!current.signal.aborted)offline('CAMERA STATUS UNAVAILABLE — NO CURRENT FRAME');}
      finally{window.clearTimeout(timeout);if(!cancelled)timer=window.setTimeout(()=>void refresh(),document.hidden?5000:1000);}
    }
    void refresh();return()=>{cancelled=true;clearExpiry();if(timer!==undefined)window.clearTimeout(timer);if(requestTimeout!==undefined)window.clearTimeout(requestTimeout);controller?.abort();};
  },[]);
  useEffect(()=>{if(active&&video.current)video.current.srcObject=stream.current;},[active]);
  useEffect(()=>{if(!browserPreviewEnabled){requestId.current++;pending.current=false;setStarting(false);stopTracks();setActive(false);}},[browserPreviewEnabled]);
  const stop=()=>{requestId.current++;pending.current=false;setStarting(false);stopTracks();setActive(false);setState('DEVELOPMENT BROWSER CAMERA STOPPED');};
  const start=async()=>{
    if(!allowed.current){setState('DEVELOPMENT BROWSER CAMERA DISABLED BY SERVER CONFIGURATION');return;}
    if(pending.current||stream.current)return;
    if(!navigator.mediaDevices?.getUserMedia){setState('DEVELOPMENT BROWSER CAMERA UNAVAILABLE');return;}
    const identifier=++requestId.current;pending.current=true;setStarting(true);
    try{
      const next=await navigator.mediaDevices.getUserMedia({video:true,audio:false});
      if(!alive.current||identifier!==requestId.current||!allowed.current){next.getTracks().forEach(track=>track.stop());return;}
      stream.current=next;setActive(true);setState('DEVELOPMENT BROWSER CAMERA ACTIVE — NOT VEHICLE CAMERA');
    }catch{if(alive.current&&identifier===requestId.current)setState('BROWSER CAMERA PERMISSION DENIED OR UNAVAILABLE');}
    finally{if(alive.current&&identifier===requestId.current){pending.current=false;setStarting(false);}}
  };
  const streamError=()=>setCamera(current=>({...current,state:'UNAVAILABLE',stream_url:null,reason:'CAMERA STREAM UNAVAILABLE — NO CURRENT FRAME'}));
  return <section className="camera-panels panel"><h2>Camera and thermal observation <em>MONITORING ONLY</em></h2><div><CameraMetadata camera={camera} onStreamError={streamError}/>
    <article><b>THERMAL CAMERA</b><small>Selected flagship: Lepton 3.5 + PureThermal 3</small><span className="camera-state not_connected">SOFTWARE MIGRATION REQUIRED · HARDWARE PENDING</span><div className="camera-empty" role="status">No flagship thermal frame is available.</div><small>USB frame format, shutter state and timing integration require implementation and verification. No temperatures are fabricated.</small><details><summary>Retained legacy thermal interface</summary><small>MLX90640 software boundary remains in engineering diagnostics. It is a different sensor and does not establish Lepton / PureThermal compatibility.</small></details></article>
    <article><b>DEVELOPMENT BROWSER CAMERA</b><small>Development-only local preview. Never uploaded or sent to TARK. NOT VEHICLE CAMERA.</small><div className="camera-controls"><button type="button" onClick={start} disabled={starting||active}>Start local preview</button><button type="button" onClick={stop}>Stop preview</button></div><small aria-live="polite">{state}</small>{active&&<video ref={video} className="browser-camera-video" muted autoPlay playsInline aria-label="Development browser camera preview"/>}</article></div></section>;
}
