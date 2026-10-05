import '@testing-library/jest-dom/vitest';
import {act,cleanup,fireEvent,render,screen,within} from '@testing-library/react';
import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import {getVehicleCameraStatus,type CameraStatus} from '../../api';
import {CameraPanels} from './CameraPanels';

vi.mock('../../api',()=>({getVehicleCameraStatus:vi.fn()}));
const status=vi.mocked(getVehicleCameraStatus);
const disconnected:CameraStatus={source_id:'camera',source_mode:'PI_UVC',state:'NOT_CONNECTED',timestamp_ns:null,age_ms:null,resolution:null,frame_rate_fps:null,reason:'CAMERA NOT CONNECTED',stream_url:null,stream_transport:'PENDING_PI_UVC_INTEGRATION',hardware_claim:'NOT_CONNECTED'};
const online=(overrides:Partial<CameraStatus>={}):CameraStatus=>({...disconnected,state:'ONLINE',timestamp_ns:100,age_ms:0,resolution:'640x480',frame_rate_fps:30,reason:'CURRENT FRAME',stream_url:'/api/v1/cameras/vehicle-rgb/stream',hardware_claim:'REAL_PI_UVC',...overrides});
function deferred<T>(){
  let resolve!:(value:T)=>void, reject!:(reason?:unknown)=>void;
  const promise=new Promise<T>((accept,fail)=>{resolve=accept;reject=fail;});
  return {promise,resolve,reject};
}
const flush=()=>act(async()=>{});
const advance=(milliseconds:number)=>act(async()=>{await vi.advanceTimersByTimeAsync(milliseconds);});
const vehicleImage=()=>screen.queryByRole('img',{name:'Live vehicle RGB camera stream'});
let getUserMedia:ReturnType<typeof vi.fn>;
let originalMediaDevices:PropertyDescriptor|undefined;

beforeEach(()=>{
  vi.useFakeTimers({toFake:['setTimeout','clearTimeout','performance']});
  vi.spyOn(document,'hidden','get').mockReturnValue(false);
  status.mockReset().mockResolvedValue(disconnected);
  originalMediaDevices=Object.getOwnPropertyDescriptor(navigator,'mediaDevices');
  getUserMedia=vi.fn();
  Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia},configurable:true});
});
afterEach(()=>{
  cleanup();
  vi.clearAllTimers();
  vi.useRealTimers();
  vi.restoreAllMocks();
  if(originalMediaDevices)Object.defineProperty(navigator,'mediaDevices',originalMediaDevices);
  else Reflect.deleteProperty(navigator,'mediaDevices');
});

test('status polls sequentially with an AbortSignal and waits one second after completion',async()=>{
  const first=deferred<CameraStatus>();status.mockReturnValueOnce(first.promise);
  render(<CameraPanels browserPreviewEnabled={false}/>);
  expect(status).toHaveBeenCalledOnce();
  expect(status.mock.calls[0][0]).toBeInstanceOf(AbortSignal);
  await advance(2500);
  expect(status).toHaveBeenCalledOnce();
  await act(async()=>{first.resolve(disconnected);});
  await advance(999);expect(status).toHaveBeenCalledOnce();
  await advance(1);expect(status).toHaveBeenCalledTimes(2);
});

test('a hung status request is aborted after four seconds and polling recovers',async()=>{
  status.mockImplementationOnce(signal=>new Promise((_resolve,reject)=>{
    signal?.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')),{once:true});
  }));
  render(<CameraPanels browserPreviewEnabled={false}/>);
  const signal=status.mock.calls[0][0]!;
  await advance(3999);expect(signal.aborted).toBe(false);expect(status).toHaveBeenCalledOnce();
  await advance(1);
  expect(signal.aborted).toBe(true);
  expect(screen.getByText('CAMERA STATUS TIMED OUT — NO CURRENT FRAME')).toBeInTheDocument();
  expect(vehicleImage()).not.toBeInTheDocument();
  await advance(1000);expect(status).toHaveBeenCalledTimes(2);
});

test('the last frame expires at three seconds while the next request is pending',async()=>{
  status.mockResolvedValueOnce(online()).mockReturnValue(new Promise(()=>{}));
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  expect(vehicleImage()).toBeInTheDocument();
  await advance(2999);expect(vehicleImage()).toBeInTheDocument();
  await advance(1);
  expect(vehicleImage()).not.toBeInTheDocument();
  expect(screen.getByText('CAMERA STATUS EXPIRED — NO CURRENT FRAME')).toBeInTheDocument();
});

test('duplicate frame timestamps cannot refresh the frame age or prevent expiry',async()=>{
  status.mockResolvedValue(online());
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  await advance(2000);
  expect(screen.getByText(/Frame age at latest status: 2000 ms/)).toBeInTheDocument();
  expect(vehicleImage()).toBeInTheDocument();
  await advance(1000);
  expect(status).toHaveBeenCalledTimes(4);
  expect(vehicleImage()).not.toBeInTheDocument();
  expect(screen.getByText('CAMERA STATUS EXPIRED — NO CURRENT FRAME')).toBeInTheDocument();
});

test('request latency counts toward the three-second freshness limit',async()=>{
  const first=deferred<CameraStatus>();status.mockReturnValueOnce(first.promise);
  render(<CameraPanels browserPreviewEnabled={false}/>);
  await advance(2000);
  await act(async()=>{first.resolve(online({age_ms:500}));});
  expect(screen.getByText(/Frame age at latest status: 2500 ms/)).toBeInTheDocument();
  await advance(500);expect(vehicleImage()).not.toBeInTheDocument();
});

test('out-of-order metadata removes the frame immediately',async()=>{
  status.mockResolvedValueOnce(online({timestamp_ns:200})).mockResolvedValue(online({timestamp_ns:100}));
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  expect(vehicleImage()).toBeInTheDocument();
  await advance(1000);
  expect(vehicleImage()).not.toBeInTheDocument();
  expect(screen.getByText('CAMERA STATUS UNAVAILABLE — NO CURRENT FRAME')).toBeInTheDocument();
});

test('a failed status request removes the displayed frame immediately',async()=>{
  status.mockResolvedValueOnce(online()).mockRejectedValue(new Error('offline'));
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  expect(vehicleImage()).toBeInTheDocument();
  await advance(1000);
  expect(vehicleImage()).not.toBeInTheDocument();
  expect(screen.getByText('CAMERA STATUS UNAVAILABLE — NO CURRENT FRAME')).toBeInTheDocument();
});

test('unmount aborts an in-flight status request and clears all scheduled work',async()=>{
  const first=deferred<CameraStatus>();status.mockReturnValueOnce(first.promise);
  const view=render(<CameraPanels browserPreviewEnabled={false}/>);
  const signal=status.mock.calls[0][0]!;
  view.unmount();
  expect(signal.aborted).toBe(true);
  expect(vi.getTimerCount()).toBe(0);
  await act(async()=>{first.resolve(online());});
  await advance(10000);expect(status).toHaveBeenCalledOnce();
});

test('a stream error immediately removes the image',async()=>{
  status.mockResolvedValue(online());
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  fireEvent.error(vehicleImage()!);
  expect(vehicleImage()).not.toBeInTheDocument();
  expect(screen.getByText('CAMERA STREAM UNAVAILABLE — NO CURRENT FRAME')).toBeInTheDocument();
});

test('simulation frames do not claim a live vehicle camera',async()=>{
  status.mockResolvedValue(online({source_mode:'SIMULATION',hardware_claim:'SIMULATED'}));
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  expect(screen.getByRole('img',{name:'Simulated or replay camera stream'})).toBeInTheDocument();
  expect(screen.queryByText('● LIVE VEHICLE CAMERA')).not.toBeInTheDocument();
});

test('browser preview is disabled by configuration and cannot request permission',async()=>{
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  fireEvent.click(screen.getByRole('button',{name:'Start local preview'}));
  expect(screen.getByText('DEVELOPMENT BROWSER CAMERA DISABLED BY SERVER CONFIGURATION')).toBeInTheDocument();
  expect(getUserMedia).not.toHaveBeenCalled();
  expect(screen.getByText('CAMERA NOT CONNECTED')).toHaveClass('camera-state');
  expect(screen.queryByLabelText('Development browser camera preview')).not.toBeInTheDocument();
});

test('enabled browser preview requests permission only on click and stops tracks on unmount',async()=>{
  const stop=vi.fn();const localStream={getTracks:()=>[{stop}]} as unknown as MediaStream;
  getUserMedia.mockResolvedValue(localStream);
  const view=render(<CameraPanels browserPreviewEnabled/>);await flush();
  expect(getUserMedia).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Start local preview'}));await flush();
  expect(getUserMedia).toHaveBeenCalledTimes(1);
  expect(getUserMedia).toHaveBeenCalledWith({video:true,audio:false});
  expect(screen.getByText('DEVELOPMENT BROWSER CAMERA ACTIVE — NOT VEHICLE CAMERA')).toBeInTheDocument();
  expect((screen.getByLabelText('Development browser camera preview') as HTMLVideoElement).srcObject).toBe(localStream);
  view.unmount();expect(stop).toHaveBeenCalledOnce();
});

test.each(['stop','unmount','disable'] as const)('a late browser permission result after %s stops every track',async(action)=>{
  const permission=deferred<MediaStream>();getUserMedia.mockReturnValue(permission.promise);
  const stopVideo=vi.fn(),stopOther=vi.fn();
  const view=render(<CameraPanels browserPreviewEnabled/>);await flush();
  fireEvent.click(screen.getByRole('button',{name:'Start local preview'}));
  expect(screen.getByRole('button',{name:'Start local preview'})).toBeDisabled();
  if(action==='stop')fireEvent.click(screen.getByRole('button',{name:'Stop preview'}));
  else if(action==='unmount')view.unmount();
  else view.rerender(<CameraPanels browserPreviewEnabled={false}/>);
  await act(async()=>{permission.resolve({getTracks:()=>[{stop:stopVideo},{stop:stopOther}]} as unknown as MediaStream);});
  expect(stopVideo).toHaveBeenCalledOnce();expect(stopOther).toHaveBeenCalledOnce();
  expect(screen.queryByLabelText('Development browser camera preview')).not.toBeInTheDocument();
});

test('thermal foreground identifies pending Lepton migration and keeps MLX90640 in legacy details',async()=>{
  render(<CameraPanels browserPreviewEnabled={false}/>);await flush();
  const thermal=screen.getByText('THERMAL CAMERA').closest('article')!;
  expect(within(thermal).getByText('Selected flagship: Lepton 3.5 + PureThermal 3')).toBeInTheDocument();
  expect(within(thermal).getByText('SOFTWARE MIGRATION REQUIRED · HARDWARE PENDING')).toBeInTheDocument();
  expect(within(thermal).getByText('No flagship thermal frame is available.')).toBeInTheDocument();
  const legacy=within(thermal).getByText(/MLX90640 software boundary/).closest('details');
  expect(legacy).not.toHaveAttribute('open');
  expect(legacy).toHaveTextContent('does not establish Lepton / PureThermal compatibility');
});
