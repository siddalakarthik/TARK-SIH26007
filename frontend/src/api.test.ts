import {afterEach,describe,expect,test,vi} from 'vitest';
import {connect,isSnapshot,isVehicleLocationStatus,websocketUrl} from './api';
import type {Snapshot} from './types';

const valid:Snapshot={mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'STOP',permitted_speed_mps:0,stopping_requirement_m:0.2,D_effective_m:1,reason_code:'STOP_NO_ENVELOPE',active_constraints:['no_usable_envelope']},command:{sequence:1,heartbeat:1,valid_until_ns:1_000_000_000},tracks:[{track_id:'track-1',x_m:-1,y_m:2,relative_velocity_mps:-0.5,quality:0.9,uncertainty_m:0.1}],sensors:[{device_id:'ld2450',source_mode:'SIMULATION',state:'ONLINE',age_ms:0,quality:0.9,reason:'FRESH'}],events:[{event_id:'event-1',timestamp_ns:1_000_000_000,event_type:'SAFETY_DECISION',severity:'STOP',reason:'STOP_NO_ENVELOPE'}]};
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
describe('status contract guard',()=>{
  test('accepts the bounded backend status shape',()=>expect(isSnapshot(valid)).toBe(true));
  test('rejects malformed or unsafe status data',()=>{expect(isSnapshot({})).toBe(false);expect(isSnapshot({...valid,decision:{...valid.decision,permitted_speed_mps:Infinity}})).toBe(false);expect(isSnapshot({...valid,tracks:'not-array'})).toBe(false);expect(isSnapshot({...valid,traction:'ENABLED'})).toBe(false);});
  test.each(['NORMAL','WARN','RESTRICT','UNKNOWN','STOP'])('accepts declared safety state %s',state=>{
    expect(isSnapshot({...valid,decision:{...valid.decision,state}})).toBe(true);
  });
  test('preserves backend modes, adapter sources, null measurements, and signed relative motion',()=>{
    for(const mode of ['SIMULATION','REPLAY','REAL_RADAR'])for(const source_mode of ['SIMULATION','REPLAY','REAL','REAL_HARDWARE','NOT_CONNECTED','NOT_CONNECTED_PHASE_2','FAULT','PI_UVC','PI_I2C','BROWSER_PREVIEW','UNKNOWN']){
      expect(isSnapshot({...valid,mode,sensors:[{...valid.sensors[0],source_mode,state:'DISABLED_PHASE_1',age_ms:null,quality:null}]})).toBe(true);
    }
    expect(isSnapshot({...valid,tracks:[],sensors:[],events:[],decision:{...valid.decision,active_constraints:[]},timestamp_ns:1})).toBe(true);
  });
  test('rejects unknown safety states and missing nested fields',()=>{
    expect(isSnapshot({...valid,decision:{...valid.decision,state:'GO'}})).toBe(false);
    for(const section of ['decision','command'] as const)for(const field of Object.keys(valid[section])){
      const incomplete={...valid[section]} as Record<string,unknown>;delete incomplete[field];
      expect(isSnapshot({...valid,[section]:incomplete}),`${section}.${field}`).toBe(false);
    }
    for(const section of ['tracks','sensors','events'] as const)for(const field of Object.keys(valid[section][0])){
      const incomplete={...valid[section][0]} as Record<string,unknown>;delete incomplete[field];
      expect(isSnapshot({...valid,[section]:[incomplete]}),`${section}.${field}`).toBe(false);
    }
  });
  test('rejects nonfinite, negative, and out-of-range measurements',()=>{
    for(const value of [NaN,Infinity,-Infinity,-1,'1',null]){
      for(const field of ['permitted_speed_mps','stopping_requirement_m','D_effective_m'])expect(isSnapshot({...valid,decision:{...valid.decision,[field]:value}})).toBe(false);
      for(const field of ['sequence','heartbeat','valid_until_ns'])expect(isSnapshot({...valid,command:{...valid.command,[field]:value}})).toBe(false);
      expect(isSnapshot({...valid,tracks:[{...valid.tracks[0],uncertainty_m:value}]})).toBe(false);
    }
    for(const value of [NaN,Infinity,-Infinity,'1',null])for(const field of ['x_m','y_m','relative_velocity_mps'])expect(isSnapshot({...valid,tracks:[{...valid.tracks[0],[field]:value}]})).toBe(false);
    for(const value of [NaN,Infinity,-1,1.1]){
      expect(isSnapshot({...valid,tracks:[{...valid.tracks[0],quality:value}]})).toBe(false);
      expect(isSnapshot({...valid,sensors:[{...valid.sensors[0],quality:value}]})).toBe(false);
    }
    for(const value of [NaN,Infinity,-1])expect(isSnapshot({...valid,sensors:[{...valid.sensors[0],age_ms:value}]})).toBe(false);
    for(const value of [NaN,Infinity,-1,0.5])expect(isSnapshot({...valid,events:[{...valid.events[0],timestamp_ns:value}]})).toBe(false);
    expect(isSnapshot({...valid,command:{...valid.command,sequence:0.5}})).toBe(false);
  });
  test('bounds lists and display text and rejects malformed list members',()=>{
    for(const [section,limit] of [['tracks',1024],['sensors',128],['events',100]] as const){
      expect(isSnapshot({...valid,[section]:Array(limit).fill(valid[section][0])})).toBe(true);
      expect(isSnapshot({...valid,[section]:Array(limit+1).fill(valid[section][0])})).toBe(false);
      for(const invalid of [null,{},'bad',1])expect(isSnapshot({...valid,[section]:[invalid]})).toBe(false);
      expect(isSnapshot({...valid,[section]:Array(1)})).toBe(false);
    }
    expect(isSnapshot({...valid,mode:'x'.repeat(257)})).toBe(false);
    expect(isSnapshot({...valid,tracks:[{...valid.tracks[0],track_id:''}]})).toBe(false);
    expect(isSnapshot({...valid,sensors:[{...valid.sensors[0],reason:'x'.repeat(2049)}]})).toBe(false);
    expect(isSnapshot({...valid,events:[{...valid.events[0],event_type:'x'.repeat(257)}]})).toBe(false);
    expect(isSnapshot({...valid,decision:{...valid.decision,active_constraints:Array(129).fill('constraint')}})).toBe(false);
    expect(isSnapshot({...valid,decision:{...valid.decision,active_constraints:[12]}})).toBe(false);
  });
});
describe('same-origin deployment transport',()=>{
  test('derives WSS for an HTTPS public hostname without a port assumption',()=>expect(websocketUrl({protocol:'https:',host:'tark-sih26007.example'})).toBe('wss://tark-sih26007.example/api/v1/ws'));
  test('derives WS for a local HTTP origin',()=>expect(websocketUrl({protocol:'http:',host:'tark.local'})).toBe('ws://tark.local/api/v1/ws'));
});

describe('WebSocket observation messages',()=>{
  test('accepts only normalized vehicle updates and never accepts a browser device source',()=>{
    const states:string[]=[],locations:unknown[]=[];
    class Socket {
      static instance:Socket;
      onopen:((event:Event)=>void)|null=null;
      onmessage:((event:MessageEvent)=>void)|null=null;
      onerror:((event:Event)=>void)|null=null;
      onclose:((event:CloseEvent)=>void)|null=null;
      constructor(){Socket.instance=this;}
      close(){}
    }
    vi.stubGlobal('WebSocket',Socket);
    const stop=connect(()=>{},state=>states.push(state),location=>locations.push(location));
    Socket.instance.onopen?.(new Event('open'));
    Socket.instance.onmessage?.(new MessageEvent('message',{data:JSON.stringify({type:'status',payload:valid})}));
    const simulated={state:'ONLINE',reason:'VALID SIMULATION FIX',breadcrumbs:[{latitude_deg:17.385,longitude_deg:78.4867,timestamp_ns:1,source:'SIMULATION'}],location:{vehicle_id:'TARK-001',timestamp_ns:1,source:'SIMULATION',latitude_deg:17.385,longitude_deg:78.4867,fix_type:'3D_FIX',quality:'SIMULATION',status:'ONLINE',heading_deg:90,horizontal_accuracy_m:4}};
    Socket.instance.onmessage?.(new MessageEvent('message',{data:JSON.stringify({type:'location_update',payload:simulated})}));
    Socket.instance.onmessage?.(new MessageEvent('message',{data:JSON.stringify({type:'location_update',payload:{...simulated,location:{...simulated.location,source:'BROWSER_DEVICE'}}})}));
    expect(states.at(-1)).toBe('CONNECTED');
    expect(locations).toEqual([simulated,{state:'UNKNOWN',reason:'INVALID LOCATION UPDATE',location:null,breadcrumbs:[]}]);
    stop();
    vi.unstubAllGlobals();
  });
});
test('rejects browser-device and invalid coordinate vehicle contracts',()=>{
  expect(isVehicleLocationStatus({state:'ONLINE',reason:'x',location:{vehicle_id:'TARK-001',timestamp_ns:1,source:'BROWSER_DEVICE',latitude_deg:17,longitude_deg:78,fix_type:'3D_FIX',quality:'x',status:'ONLINE'}})).toBe(false);
  expect(isVehicleLocationStatus({state:'ONLINE',reason:'x',location:{vehicle_id:'TARK-001',timestamp_ns:1,source:'GNSS',latitude_deg:99,longitude_deg:78,fix_type:'3D_FIX',quality:'x',status:'ONLINE'}})).toBe(false);
});

test('red team: bounded reconnect storm ignores old socket callbacks and clears timers',()=>{
  vi.useFakeTimers();vi.setSystemTime(10_000);
  const values:unknown[]=[],states:string[]=[];
  class Socket {
    static all:Socket[]=[];
    onopen:(()=>void)|null=null;onmessage:((e:{data:string})=>void)|null=null;
    onerror:(()=>void)|null=null;onclose:((e:{code:number})=>void)|null=null;
    constructor(){Socket.all.push(this);} close(){}
  }
  vi.stubGlobal('WebSocket',Socket);
  const stop=connect(value=>values.push(value),state=>states.push(state));
  for(let i=0;i<8;i++){
    const current=Socket.all.at(-1)!;
    current.onopen?.();current.onmessage?.({data:JSON.stringify({type:'status',payload:valid})});
    expect(states.at(-1)).toBe('CONNECTED');
    current.onclose?.({code:1006});current.onclose?.({code:1006});
    expect(states.at(-1)).toBe('RECONNECTING');
    const count=values.length;
    current.onmessage?.({data:JSON.stringify({type:'status',payload:valid})});
    expect(values).toHaveLength(count);
    expect(vi.getTimerCount()).toBe(1);
    vi.advanceTimersByTime(1000);
    expect(Socket.all).toHaveLength(i+2);
  }
  stop();expect(vi.getTimerCount()).toBe(0);
});

test('red team: silent telemetry becomes degraded without a disconnect',()=>{
  vi.useFakeTimers();vi.setSystemTime(10_000);
  let socket:any;
  class Socket {constructor(){socket=this;}close(){}}
  vi.stubGlobal('WebSocket',Socket);
  const states:string[]=[];
  const stop=connect(()=>{},state=>states.push(state));
  socket.onopen();socket.onmessage({data:JSON.stringify({type:'status',payload:valid})});
  vi.advanceTimersByTime(4000);
  expect(states.at(-1)).toBe('DEGRADED');
  stop();expect(vi.getTimerCount()).toBe(0);
});
