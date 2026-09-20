import '@testing-library/jest-dom/vitest';
import {render,screen} from '@testing-library/react';
import {expect,test} from 'vitest';
import {SensorMatrix} from './SensorMatrix';
test('sensor matrix accepts backend radar health using sensor_id without crashing',()=>{render(<SensorMatrix snapshot={{mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'NORMAL',permitted_speed_mps:0,stopping_requirement_m:0,D_effective_m:1,reason_code:'NORMAL_EVIDENCE',active_constraints:[]},command:{sequence:1,heartbeat:1,valid_until_ns:1},tracks:[],events:[],sensors:[{sensor_id:'radar',source_mode:'SIMULATION',state:'ONLINE',age_ms:0,quality:1,reason:'SIMULATION'}] as never}}/>);expect(screen.getByText('RADAR')).toBeInTheDocument();expect(screen.getByText('ONLINE')).toBeInTheDocument();});

test('long machine status tokens retain their dedicated no-wrap treatment',()=>{render(<SensorMatrix snapshot={{mode:'SIMULATION',traction:'DISABLED_PHASE_1',decision:{state:'NORMAL',permitted_speed_mps:0,stopping_requirement_m:0,D_effective_m:1,reason_code:'NORMAL_EVIDENCE',active_constraints:[]},command:{sequence:1,heartbeat:1,valid_until_ns:1},tracks:[],events:[],sensors:[{device_id:'camera',source_mode:'NOT_CONNECTED_PHASE_2',state:'NOT_CONNECTED',age_ms:null,quality:null,reason:'HARDWARE PENDING'}]}}/>);expect(screen.getByText('NOT_CONNECTED')).toHaveClass('status-token');});
