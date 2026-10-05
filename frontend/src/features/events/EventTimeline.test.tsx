import '@testing-library/jest-dom/vitest';
import {cleanup, fireEvent, render, screen, within} from '@testing-library/react';
import {afterEach, expect, test} from 'vitest';
import {EventTimeline} from './EventTimeline';
import type {Snapshot} from '../../types';

const base: Snapshot = {
  mode: 'SIMULATION', traction: 'DISABLED_PHASE_1',
  decision: {state: 'UNKNOWN', permitted_speed_mps: 0, stopping_requirement_m: 0,
    D_effective_m: 0, reason_code: 'CURRENT_REASON', active_constraints: []},
  command: {sequence: 55, heartbeat: 55, valid_until_ns: 0}, tracks: [], sensors: [],
  events: [
    {event_id: 'one', timestamp_ns: 1_000_000_000, event_type: 'PVSOE_DECISION', severity: 'INFO', reason: 'FIRST_REASON'},
    {event_id: 'two', timestamp_ns: 2_000_000_000, event_type: 'RADAR_STALE', severity: 'WARN', reason: 'SECOND_REASON'},
    {event_id: 'three', timestamp_ns: 3_000_000_000, event_type: 'PVSOE_DECISION', severity: 'WARN', reason: 'THIRD_REASON'},
  ],
};
afterEach(cleanup);

test('uses source-relative time and makes the recent window explicit', () => {
  render(<EventTimeline snapshot={base}/>);
  expect(screen.getByText('3.000 s')).toBeInTheDocument();
  expect(screen.getByText(/Source time is not wall-clock UTC/)).toBeInTheDocument();
  expect(screen.getByRole('status')).toHaveTextContent('Showing 3 of 3 recent records');
  expect(screen.queryByText('00:00:03.000')).not.toBeInTheDocument();
});

test('search, severity and type filters combine and clear without inventing results', () => {
  render(<EventTimeline snapshot={base}/>);
  fireEvent.change(screen.getByLabelText('Filter event severity'), {target: {value: 'WARN'}});
  fireEvent.change(screen.getByLabelText('Filter event type'), {target: {value: 'PVSOE_DECISION'}});
  expect(screen.getByRole('status')).toHaveTextContent('Showing 1 of 3');
  expect(screen.getByText('THIRD_REASON')).toBeInTheDocument();
  expect(screen.queryByText('SECOND_REASON')).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Search events'), {target: {value: 'MISSING'}});
  expect(screen.getByText('No events match these filters.')).toBeInTheDocument();
  expect(screen.queryByText('PVSOE_DECISION')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name: 'Clear filters'}));
  expect(screen.getByRole('status')).toHaveTextContent('Showing 3 of 3');
});

test('selected evidence only shows the event fields, never current decision as historical evidence', () => {
  render(<EventTimeline snapshot={base}/>);
  fireEvent.click(screen.getByRole('button', {name: 'Inspect event two'}));
  const detail = screen.getByRole('region', {name: 'Selected event evidence'});
  expect(within(detail).getByText('SECOND_REASON')).toBeInTheDocument();
  expect(within(detail).getByText('two')).toBeInTheDocument();
  expect(within(detail).queryByText('CURRENT_REASON')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name: 'Close evidence'}));
  expect(screen.queryByRole('region', {name: 'Selected event evidence'})).not.toBeInTheDocument();
});

test('retains at most 100 recent records and deduplicates a repeated record identity', () => {
  const events = Array.from({length: 120}, (_, index) => ({...base.events[0], event_id: `record-${index}`, reason: `REASON_${index}`}));
  events.push({...events[119]});
  render(<EventTimeline snapshot={{...base, events}}/>);
  expect(screen.getByRole('status')).toHaveTextContent('Showing 99 of 99');
  expect(screen.queryByText('REASON_0')).not.toBeInTheDocument();
  expect(screen.getAllByText('REASON_119')).toHaveLength(1);
  expect(screen.getAllByRole('row')).toHaveLength(100);
});

test('empty and invalid timestamps render truthfully, and removed selected records do not linger', () => {
  const {rerender} = render(<EventTimeline snapshot={{...base, events: [{...base.events[0], timestamp_ns: NaN}]}}/>);
  expect(screen.getByText('UNAVAILABLE')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name: 'Inspect event one'}));
  rerender(<EventTimeline snapshot={{...base, events: []}}/>);
  expect(screen.getByText('No events received in the current observation window.')).toBeInTheDocument();
  expect(screen.queryByRole('region', {name: 'Selected event evidence'})).not.toBeInTheDocument();
});
