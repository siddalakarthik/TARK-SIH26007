import {describe,expect,test,vi} from 'vitest';
import {connect,isSnapshot,isVehicleLocationStatus,websocketUrl} from './api';

const valid={mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'STOP',permitted_speed_mps:0,reason_code:'TEST'},command:{sequence:1},tracks:[],sensors:[],events:[]};
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
    expect(locations).toEqual([simulated]);
    stop();
    vi.unstubAllGlobals();
  });
});
test('rejects browser-device and invalid coordinate vehicle contracts',()=>{
  expect(isVehicleLocationStatus({state:'ONLINE',reason:'x',location:{vehicle_id:'TARK-001',timestamp_ns:1,source:'BROWSER_DEVICE',latitude_deg:17,longitude_deg:78,fix_type:'3D_FIX',quality:'x',status:'ONLINE'}})).toBe(false);
  expect(isVehicleLocationStatus({state:'ONLINE',reason:'x',location:{vehicle_id:'TARK-001',timestamp_ns:1,source:'GNSS',latitude_deg:99,longitude_deg:78,fix_type:'3D_FIX',quality:'x',status:'ONLINE'}})).toBe(false);
});
