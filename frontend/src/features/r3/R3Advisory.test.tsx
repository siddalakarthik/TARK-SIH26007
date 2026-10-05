import '@testing-library/jest-dom/vitest';
import {cleanup,render,screen} from '@testing-library/react';
import {afterEach,expect,test} from 'vitest';
import {R3Advisory,readAdvisory} from './R3Advisory';
const fixture=()=>({advisory:{decision_version:'TARK_R3_ADVISORY_1',state:'UNKNOWN',advisory:'HOLD_INSUFFICIENT_EVIDENCE',limiting_reason:'MOTION_UNKNOWN',source_mode:'SIMULATION',advised_speed_mps:null,stopping_requirement_m:null,motion_authority:false,hardware_verified:false,traction:'DISABLED_PHASE_1',configuration_id:'cfg',configuration_hash:'hash',software_fingerprint:'software',vehicle_profile:{profile:'R3_RESEARCH_CART',provenance:'CONFIGURED_RESEARCH'},observability:{forward_range_m:3,provenance:'CONFIGURED_RESEARCH',road_clear_claim:false},qualified_sources:['radar-a'],excluded_sources:{'rgb-a':'STALE'},semantic_observations:[{source_id:'radar-a',purposes:['RANGE'],exclusion_reason:null}],tracks:[],ttc:[],cooperative_context:[]}});
afterEach(cleanup);
test('UNKNOWN is unavailable, not zero or NORMAL; explicit separate advisory scope',()=>{
 render(<R3Advisory value={fixture()}/>);expect(screen.getByText('R3_ADVISORY')).toBeInTheDocument();
 expect(screen.getByText('UNKNOWN')).toBeInTheDocument();expect(screen.getAllByText('Unavailable')).toHaveLength(2);
 expect(screen.getByText(/not prove the road is clear/)).toBeInTheDocument();expect(screen.queryByText('NORMAL')).not.toBeInTheDocument();
});
test.each(['NORMAL','WARN','RESTRICT','STOP'])('renders %s without browser computation',state=>{
 const value=fixture();value.advisory.state=state;render(<R3Advisory value={value}/>);expect(screen.getByText(state)).toBeInTheDocument();
});
test.each([null,{advisory:{}},{advisory:{...fixture().advisory,advised_speed_mps:NaN}},{advisory:{...fixture().advisory,motion_authority:true}},{advisory:{...fixture().advisory,hardware_verified:true}},{advisory:{...fixture().advisory,state:'SAFE'}}])('invalid data never becomes usable',value=>{
 expect(readAdvisory(value)).toBeNull();render(<R3Advisory value={value}/>);expect(screen.getByRole('status')).toHaveTextContent('Unavailable or invalid');
});
test('driver contains action and reason without engineering tables',()=>{
 render(<R3Advisory value={fixture()} compact/>);expect(screen.getByText(/motion unknown/)).toBeInTheDocument();
 expect(screen.queryByText('Research speed ceiling')).not.toBeInTheDocument();expect(screen.queryByText('Local tracks')).not.toBeInTheDocument();
});
