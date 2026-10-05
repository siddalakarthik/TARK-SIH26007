import '@testing-library/jest-dom/vitest';
import {cleanup,render,screen,within} from '@testing-library/react';
import {afterEach,expect,test} from 'vitest';
import {DriverView} from './DriverView';
import type {Snapshot} from '../../types';

const snapshot:Snapshot={mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'NORMAL',permitted_speed_mps:0,stopping_requirement_m:.5,D_effective_m:2.8,reason_code:'NORMAL_EVIDENCE',active_constraints:[]},command:{sequence:1,heartbeat:1,valid_until_ns:2},tracks:[],sensors:[],events:[]};
afterEach(cleanup);
test('SI-05 absent measured speed is not displayed as zero',()=>{
  render(<DriverView snapshot={snapshot}/>);
  expect(screen.queryByText('Current speed')).not.toBeInTheDocument();
  expect(screen.getByText('Measured speed').parentElement).toHaveTextContent('UNAVAILABLE');
});
test('SI-06 TTC is explicitly not computed, not a generic N/A',()=>{
  render(<DriverView snapshot={snapshot}/>);
  expect(within(screen.getByText('TTC').parentElement!).getByText('NOT COMPUTED')).toBeInTheDocument();
});
test.each(['WARN','RESTRICT','UNKNOWN','STOP'] as const)('driver preserves %s and never offers motion authority',state=>{
  render(<DriverView snapshot={{...snapshot,decision:{...snapshot.decision,state}}}/>);
  expect(screen.getByText(state,{exact:true})).toBeInTheDocument();
  expect(screen.getByText(/Keep traction disabled/)).toBeInTheDocument();
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});
test('driver source status matches the existing ld2450 radar identity',()=>{
  render(<DriverView snapshot={{...snapshot,sensors:[{device_id:'ld2450',source_mode:'SIMULATION',state:'ONLINE',age_ms:1,quality:1,reason:'TEST'}]}}/>);
  expect(screen.getByText('Radar').parentElement).toHaveTextContent('Online');
  expect(screen.getByText('Radar').parentElement).toHaveTextContent('SIMULATION');
});
