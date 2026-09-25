import '@testing-library/jest-dom/vitest';
import {cleanup,render} from '@testing-library/react';
import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import MapView from './MapView';
import type {Snapshot} from './types';
import type {VehicleLocationStatus} from './api';

const fixture=vi.hoisted(()=>({maps:[] as any[],markers:[] as any[]}));
vi.mock('maplibre-gl',()=>({default:{
  Map:class {
    sources:Record<string,any>={};
    constructor(){fixture.maps.push(this);}
    addControl(){} once(){} on(){} off(){} resize(){} remove(){}
    isStyleLoaded(){return true;}
    getSource(id:string){return this.sources[id];}
    addSource(id:string,source:any){this.sources[id]={data:source.data,setData(data:any){this.data=data;}};}
    addLayer(){}
  },
  Marker:class {
    element:HTMLElement;removed=false;
    constructor(options:any){this.element=options.element;fixture.markers.push(this);}
    setLngLat(){return this;} addTo(){return this;} getElement(){return this.element;}
    remove(){this.removed=true;}
  },
  NavigationControl:class {},ScaleControl:class {},
}}));
const snapshot:Snapshot={mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'NORMAL',permitted_speed_mps:0,stopping_requirement_m:.5,D_effective_m:2.8,reason_code:'NORMAL_EVIDENCE',active_constraints:[]},command:{sequence:1,heartbeat:1,valid_until_ns:2},tracks:[],sensors:[],events:[]};
const location:VehicleLocationStatus={state:'ONLINE',reason:'FIXTURE',breadcrumbs:[],location:{vehicle_id:'TARK-001',timestamp_ns:1,source:'SIMULATION',latitude_deg:17,longitude_deg:78,fix_type:'3D_FIX',quality:'SIMULATION',status:'ONLINE',heading_deg:90,horizontal_accuracy_m:3}};
beforeEach(()=>{fixture.maps.length=0;fixture.markers.length=0;vi.stubGlobal('ResizeObserver',class{observe(){} disconnect(){}});});
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
test.each([null,{state:'STALE',reason:'NO FRESH FIX',location:null}, {...location,state:'STALE'}])('SI-08 absent/stale location clears current marker and accuracy layer: %j',value=>{
  const view=render(<MapView snapshot={snapshot} vehicleLocation={location}/>);
  expect(fixture.markers).toHaveLength(1);
  view.rerender(<MapView snapshot={snapshot} vehicleLocation={value}/>);
  expect(fixture.markers[0].removed).toBe(true);
  expect(fixture.maps[0].sources['tark-vehicle'].data.features).toEqual([]);
  expect(fixture.maps[0].sources['tark-vehicle-trail'].data.features).toEqual([]);
  expect(fixture.maps).toHaveLength(1);
});
test('SI-08 unknown heading is not a north-pointing arrow',()=>{
  render(<MapView snapshot={snapshot} vehicleLocation={{...location,location:{...location.location!,heading_deg:null}}}/>);
  expect(fixture.markers[0].element.querySelector('.vehicle-direction').textContent).not.toBe('▲');
});

test('red team: repeated disappearance and recovery keeps exactly one map',()=>{
  const view=render(<MapView snapshot={snapshot} vehicleLocation={location}/>);
  for(let i=0;i<8;i++){
    view.rerender(<MapView snapshot={snapshot} vehicleLocation={null}/>);
    expect(fixture.markers.every(marker=>marker.removed)).toBe(true);
    view.rerender(<MapView snapshot={snapshot} vehicleLocation={location}/>);
    expect(fixture.markers.filter(marker=>!marker.removed)).toHaveLength(1);
    expect(fixture.maps).toHaveLength(1);
  }
});
