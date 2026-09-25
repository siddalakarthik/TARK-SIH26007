import {afterEach,describe,expect,test,vi} from 'vitest';
import {connect,isSnapshot,isVehicleLocationStatus,websocketUrl} from './api';

const valid={mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'STOP',permitted_speed_mps:0,reason_code:'TEST'},command:{sequence:1},tracks:[],sensors:[],events:[]};
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
describe('status contract guard',()=>{
  test('accepts the bounded backend status shape',()=>expect(isSnapshot(valid)).toBe(true));
  test('rejects malformed or unsafe status data',()=>{expect(isSnapshot({})).toBe(false);expect(isSnapshot({...valid,decision:{...valid.decision,permitted_speed_mps:Infinity}})).toBe(false);expect(isSnapshot({...valid,tracks:'not-array'})).toBe(false);expect(isSnapshot({...valid,traction:'ENABLED'})).toBe(false);});
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
