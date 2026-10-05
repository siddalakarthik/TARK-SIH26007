import '@testing-library/jest-dom/vitest';
import {cleanup,render,screen} from '@testing-library/react';
import {afterEach,expect,test} from 'vitest';
import {FleetPanel,RadarScope,participantFresh} from './FlagshipDashboard';
import type {FlagshipParticipant,FlagshipSnapshot} from './types';
import type {Snapshot} from '../../types';

const vehicle:FlagshipParticipant={id:'B',name:'Node B',role:'LOCATION_ONLY',source_mode:'SIMULATION',state:'SIMULATED',position:{latitude_deg:17,longitude_deg:78},speed_mps:.8,course_deg:90,heading_deg:null,accuracy_m:3,age_ms:0,timestamp_ns:1,quality:'SIMULATED_FIX',capabilities:['GNSS']};
const empty:GeoJSON.FeatureCollection={type:'FeatureCollection',features:[]};
const data:FlagshipSnapshot={schema_version:'tark.flagship.v1',mode:'SIMULATION',source_mode:'SIMULATION',timestamp_ns:1,sequence:1,traction:'DISABLED_PHASE_1',monitoring_only:true,hardware_verified:false,scene:{id:'test',label:'Fixture',source:'SIMULATION',coordinate_system:'WGS84_DISPLAY_ANCHOR_ONLY',center:[78,17],bounds:[77,16,79,18],review_status:'NOT_SURVEYED',roads:empty,route:empty,zones:empty,waypoints:empty,hazards:empty,history:empty},participants:[vehicle],hardware:[],limitations:[]};
const snapshot:Snapshot={mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'UNKNOWN',permitted_speed_mps:0,stopping_requirement_m:0,D_effective_m:0,reason_code:'TEST',active_constraints:[]},command:{sequence:1,heartbeat:1,valid_until_ns:2},tracks:[],sensors:[],events:[]};
afterEach(cleanup);

test('rear and lateral targets remain inside a full-plane radar plot',()=>{
  const tracks=[[5,0],[-5,0],[0,5],[0,-5],[5,5]].map(([x_m,y_m],index)=>({track_id:String(index),x_m,y_m,relative_velocity_mps:0,quality:1,uncertainty_m:0}));
  render(<RadarScope snapshot={{...snapshot,tracks}}/>);
  expect(screen.getAllByTestId('radar-target')).toHaveLength(5);
  for(const target of screen.getAllByTestId('radar-target')){const circle=target.querySelector('circle')!;expect(Number(circle.getAttribute('cx'))).toBeGreaterThanOrEqual(70);expect(Number(circle.getAttribute('cx'))).toBeLessThanOrEqual(290);expect(Number(circle.getAttribute('cy'))).toBeGreaterThanOrEqual(40);expect(Number(circle.getAttribute('cy'))).toBeLessThanOrEqual(260);}
});
test('large radar observations are bounded and omissions disclosed',()=>{
  const tracks=Array.from({length:100},(_,index)=>({track_id:String(index),x_m:2,y_m:1,relative_velocity_mps:0,quality:1,uncertainty_m:0}));
  render(<RadarScope snapshot={{...snapshot,tracks}}/>);expect(screen.getAllByTestId('radar-target')).toHaveLength(50);expect(screen.getByText('50 displayed / 100 received')).toBeInTheDocument();expect(screen.getByText(/omitted observations are not treated as clear space/)).toBeInTheDocument();
});
test('nonfinite target is not rendered as a valid point',()=>{render(<RadarScope snapshot={{...snapshot,tracks:[{track_id:'bad',x_m:NaN,y_m:Infinity,relative_velocity_mps:0,quality:1,uncertainty_m:0}]}}/>);expect(screen.queryByTestId('radar-target')).not.toBeInTheDocument();expect(screen.getByText('0 displayed / 1 received')).toBeInTheDocument();});
test('unavailable participants do not look connected',()=>{render(<FleetPanel data={{...data,participants:[{...vehicle,position:null,state:'NOT_CONNECTED'}]}} selectedId="B" onSelect={()=>{}}/>);expect(screen.getByText('0 fresh / 1')).toBeInTheDocument();expect(screen.queryByText('Connected participants')).not.toBeInTheDocument();expect(screen.getByText('Position unavailable')).toBeInTheDocument();});
test('stale participant values and direction are withheld',()=>{render(<FleetPanel data={{...data,participants:[{...vehicle,age_ms:3001}]}} selectedId="B" onSelect={()=>{}}/>);expect(screen.getByText('Last known — stale')).toBeInTheDocument();expect(screen.getByText('Scene speed').parentElement).toHaveTextContent('—');expect(screen.getByText('Direction').parentElement).not.toHaveTextContent('90');});
test('stationary location-only node never gains a body heading',()=>{render(<FleetPanel data={{...data,participants:[{...vehicle,speed_mps:0,heading_deg:120}]}} selectedId="B" onSelect={()=>{}}/>);expect(screen.getByText('Direction').parentElement).toHaveTextContent('—');expect(screen.getByText('Direction').parentElement).not.toHaveTextContent('120');});
test('moving location-only node reports course, not body heading',()=>{render(<FleetPanel data={data} selectedId="B" onSelect={()=>{}}/>);expect(screen.getByText('Direction').parentElement).toHaveTextContent('90 ° course');});
test.each([null,-1,3001,Infinity,NaN])('invalid or expired participant age %s is not fresh',age_ms=>{expect(participantFresh({...vehicle,age_ms})).toBe(false);});
