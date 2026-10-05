import '@testing-library/jest-dom/vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,expect,test,vi} from 'vitest';
import {R3Evidence,EvidenceWhy} from './R3Evidence';
import {readR3} from './contract';

function fixture(){return {schema_version:'TARK_READINESS_1',source_mode:'SIMULATION',active_profile:'R3_PI5_ADVISORY',profile_id:'R3_PI5_ADVISORY',hardware_claim:'HARDWARE_UNVERIFIED',traction:'DISABLED_PHASE_1',configuration_bundle_id:'cfg',software_version:'software',calibration_bundle:[],experiment:null,timeline:[],
  explanation:{decision_scope:'LEGACY_RADAR_RESEARCH_PIPELINE',decision_state:'UNKNOWN',primary_reason:'UNKNOWN_STALE',reason:'R3 sources do not participate in the legacy decision.',motion_authority:false},
  sources:[{source_id:'gnss-b',part_number:'LG290P',mode:'SIMULATION',evidence_origin:'SYNTHETIC_FIXTURE',expected:true,detected:false,identity_verified:false,driver_ready:true,producing:true,fresh:true,plausible:true,time_valid:false,calibration_valid:false,qualified:false,qualified_for:[],clock_state:'TIME_UNSYNCED',calibration_state:'MISSING',fault_reason:'TIME_UNQUALIFIED',age_bound_ns:null,rate_hz:null,counters:{drops:2,invalid:1},queue_depth:1,connection_state:'CONNECTED',health_state:'ONLINE'}]};}
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
test('readiness distinguishes connected, fresh, time and calibration with no invented accuracy',()=>{
  render(<R3Evidence value={fixture()}/>);
  expect(screen.getByText(/TIME_UNQUALIFIED/)).toBeInTheDocument();
  expect(screen.getByText(/HARDWARE UNVERIFIED/)).toBeInTheDocument();
  expect(screen.getByText(/ordinary local wi-fi/i)).toBeInTheDocument();
  expect(screen.queryByRole('button',{name:'Create experiment'})).not.toBeInTheDocument();
});
test.each([null,{schema_version:'wrong'},{...fixture(),sources:[{...fixture().sources[0],qualified:true}]},{...fixture(),sources:[{...fixture().sources[0],rate_hz:NaN}]},{...fixture(),sources:[{...fixture().sources[0],identity_verified:true}]}])('malformed or contradictory evidence remains unavailable',value=>{
  expect(readR3(value)).toBeNull();render(<R3Evidence value={value}/>);expect(screen.getByRole('status')).toHaveTextContent('Unavailable or invalid');
});
test('structured explanation shows scope and UNKNOWN, not browser-computed safety',()=>{
  render(<EvidenceWhy value={fixture()}/>);fireEvent.click(screen.getByText('Why? Evidence scope'));
  expect(screen.getByText('UNKNOWN')).toBeInTheDocument();expect(screen.getByText(/do not participate/)).toBeInTheDocument();
});
test('local experiment form posts only metadata and current bundle',async()=>{
  const fetcher=vi.fn().mockResolvedValue({ok:true});vi.stubGlobal('fetch',fetcher);
  render(<R3Evidence value={fixture()} engineeringWrites/>);
  fireEvent.click(screen.getByText('Create a local experiment'));
  for(const label of ['Experiment ID','Experiment title','Scenario','Operator','Test / visibility condition'])fireEvent.change(screen.getByLabelText(label),{target:{value:'fixture'}});
  fireEvent.click(screen.getByRole('button',{name:'Create experiment'}));
  await waitFor(()=>expect(fetcher).toHaveBeenCalledOnce());
  const [url,options]=fetcher.mock.calls[0];expect(url).toBe('/api/v2/r3/experiments');
  const body=JSON.parse(options.body);expect(body.configuration_bundle).toBe('cfg');expect(body.expected_sources).toEqual(['gnss-b']);expect(body).not.toHaveProperty('command');
  expect(await screen.findByText(/Experiment created/)).toBeInTheDocument();
});

test('experiment catalog is read-only and separates recorded results from hardware claims',async()=>{
  const fetcher=vi.fn().mockResolvedValue({ok:true,json:async()=>[{experiment_id:'exp-1',status:'COMPLETE',recording_id:'record-1',summary:{recorded_ticks:12,replay_result:{result:'MATCH'}}}]});
  vi.stubGlobal('fetch',fetcher);render(<R3Evidence value={fixture()}/>);
  fireEvent.click(screen.getByRole('button',{name:'Load experiment catalog'}));
  expect(await screen.findByText(/R3 replay: MATCH/)).toBeInTheDocument();
  expect(fetcher.mock.calls[0][0]).toBe('/api/v2/r3/experiments');
  expect(fetcher.mock.calls[0][1]).not.toHaveProperty('method');
  expect(screen.getByText(/not physical results/)).toBeInTheDocument();
});

test('invalid experiment catalog cannot appear verified',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>[{experiment_id:'x',status:'SAFE',recording_id:null}]}));
  render(<R3Evidence value={fixture()}/>);fireEvent.click(screen.getByRole('button',{name:'Load experiment catalog'}));
  expect(await screen.findByText(/catalog unavailable or invalid/)).toBeInTheDocument();
  expect(screen.queryByLabelText('Recent experiments')).not.toBeInTheDocument();
});
