import '@testing-library/jest-dom/vitest';
import {act,cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,expect,test,vi} from 'vitest';
import {ReplayPanel} from './ReplayPanel';

const fixtures=vi.hoisted(()=>({
  session:{session_id:'session-1',started_ns:1,stopped_ns:3,source_mode:'SIMULATION',configuration_hash:'hash',status:'COMPLETE' as const,max_records:10,record_count:2},
  timeline:{session_id:'session-1',source_mode:'REPLAY' as const,state:'READY' as const,configuration_hash:'hash',start_timestamp_ns:1_000,end_timestamp_ns:2_000,duration_ns:1_000,items:[
    {position:0,sequence:1,timestamp_ns:1_000,source_mode:'REPLAY' as const,original_source_mode:'SIMULATION',decision:{state:'WARN',reason_code:'FIRST',permitted_speed_mps:0},event:{event_type:'PVSOE_DECISION',severity:'INFO',reason:'FIRST'},command:{sequence:1},track_count:1},
    {position:1,sequence:2,timestamp_ns:2_000,source_mode:'REPLAY' as const,original_source_mode:'SIMULATION',decision:{state:'STOP',reason_code:'SECOND',permitted_speed_mps:0},event:{event_type:'PVSOE_DECISION',severity:'WARN',reason:'SECOND'},command:{sequence:2},track_count:2},
  ]},
}));

vi.mock('../../api',()=>({
  getReplaySessions:vi.fn().mockResolvedValue([fixtures.session]),getReplaySession:vi.fn().mockResolvedValue(fixtures.session),getReplayTimeline:vi.fn().mockResolvedValue(fixtures.timeline),startRecording:vi.fn(),stopRecording:vi.fn(),verifyReplay:vi.fn().mockResolvedValue({result:'MATCH',first_divergence:null}),
}));

afterEach(()=>{cleanup();vi.clearAllMocks();});

test('R3 decision recomputation is shown separately from legacy MATCH',async()=>{
 const api=await import('../../api');
 vi.mocked(api.verifyReplay).mockResolvedValueOnce({session_id:'session-1',result:'MATCH',first_divergence:null,
   r3_advisory:{result:'MISMATCH',reason:'R3_DECISION_DIFFERS',first_divergence:7,computation_ns:100}});
 render(<ReplayPanel/>);await screen.findByText(/Select a completed observation/i);
 fireEvent.change(screen.getByLabelText('Recording session'),{target:{value:'session-1'}});
 fireEvent.click(screen.getByRole('button',{name:'Load recording'}));await screen.findByText(/REPLAY loaded/i);
 fireEvent.click(screen.getByRole('button',{name:'Verify replay'}));
 expect(await screen.findByText(/R3 recorded vs recomputed advisory: MISMATCH at sequence 7/)).toBeInTheDocument();
});

test('loads an isolated replay timeline and supports step, seek and reset',async()=>{
  render(<ReplayPanel/>);
  await screen.findByText(/Select a completed observation/i);
  fireEvent.change(screen.getByLabelText('Recording session'),{target:{value:'session-1'}});
  fireEvent.click(screen.getByRole('button',{name:'Load recording'}));
  await screen.findByText(/REPLAY loaded: 2 normalized/i);
  expect(screen.getByText(/Source: REPLAY/i)).toBeInTheDocument();
  expect(screen.getByText(/REPLAY ITEM 1/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:'Step forward'}));
  expect(screen.getByText(/REPLAY ITEM 2/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Replay position'),{target:{value:'0'}});
  expect(screen.getByText(/REPLAY ITEM 1/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:'Reset'}));
  expect(screen.getByText(/REPLAY ITEM 1/)).toBeInTheDocument();
  expect(screen.getByText(/never an ESP32 or traction authority/i)).toBeInTheDocument();
});

test('retains unavailable state without inventing a replay session',async()=>{
  const api=await import('../../api');
  vi.mocked(api.getReplaySessions).mockResolvedValueOnce([]);
  render(<ReplayPanel/>);
  await waitFor(()=>expect(screen.getByText(/no persisted recording exists/i)).toBeInTheDocument());
  expect(screen.getByRole('button',{name:'Play'})).toBeDisabled();
  expect(screen.getByRole('button',{name:'Step forward'})).toBeDisabled();
});

test('public demo exposes replay evidence without recording controls',async()=>{
  render(<ReplayPanel recordingControlsAvailable={false}/>);
  await screen.findByText(/Select a completed observation/i);
  expect(screen.getByText(/PUBLIC DEMO: recording creation is unavailable/i)).toBeInTheDocument();
  expect(screen.queryByRole('button',{name:'Start recording'})).not.toBeInTheDocument();
  expect(screen.queryByRole('button',{name:'Stop recording'})).not.toBeInTheDocument();
});

test('plays, pauses, and stops at the end of the selected replay timeline',async()=>{
  render(<ReplayPanel/>);
  await screen.findByText(/Select a completed observation/i);
  fireEvent.change(screen.getByLabelText('Recording session'),{target:{value:'session-1'}});
  fireEvent.click(screen.getByRole('button',{name:'Load recording'}));
  await screen.findByText(/REPLAY ITEM 1/);
  vi.useFakeTimers();
  try {
    fireEvent.click(screen.getByRole('button',{name:'Play'}));
    expect(screen.getByRole('button',{name:'Pause'})).toBeEnabled();
    fireEvent.click(screen.getByRole('button',{name:'Pause'}));
    expect(screen.getByRole('button',{name:'Play'})).toBeEnabled();
    fireEvent.click(screen.getByRole('button',{name:'Play'}));
    act(()=>vi.advanceTimersByTime(500));
    expect(screen.getByText(/REPLAY ITEM 2/)).toBeInTheDocument();
    act(()=>vi.advanceTimersByTime(500));
    expect(screen.getByText(/End of replay reached/i)).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'Play'})).toBeDisabled();
  } finally { vi.useRealTimers(); }
});
