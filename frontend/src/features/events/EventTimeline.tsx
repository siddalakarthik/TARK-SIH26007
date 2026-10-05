import {useMemo, useState} from 'react';
import type {Snapshot} from '../../types';
import {Panel} from '../../components/Panel';

const WINDOW_LIMIT = 100;

function sourceTime(timestampNs: number): string {
  return Number.isFinite(timestampNs) && timestampNs >= 0
    ? `${(timestampNs / 1e9).toFixed(3)} s`
    : 'UNAVAILABLE';
}

export function EventTimeline({snapshot}: {snapshot: Snapshot}) {
  const [query, setQuery] = useState('');
  const [severity, setSeverity] = useState('');
  const [eventType, setEventType] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const window = useMemo(() => {
    // Bounded recent snapshot window, not a second unbounded event archive.
    const seen = new Set<string>();
    return snapshot.events.slice(-WINDOW_LIMIT).reverse().filter(event => {
      if (seen.has(event.event_id)) return false;
      seen.add(event.event_id);
      return true;
    });
  }, [snapshot.events]);
  const severities = useMemo(() => [...new Set(window.map(event => event.severity))].sort(), [window]);
  const eventTypes = useMemo(() => [...new Set(window.map(event => event.event_type))].sort(), [window]);
  const events = useMemo(() => {
    const search = query.trim().toLowerCase();
    return window.filter(event => (!severity || event.severity === severity)
      && (!eventType || event.event_type === eventType)
      && `${event.event_id} ${event.event_type} ${event.reason} ${event.severity}`.toLowerCase().includes(search));
  }, [window, query, severity, eventType]);
  const selected = window.find(event => event.event_id === selectedId);

  return <Panel title="Event timeline">
    <p className="event-window-note">Recent observation window · up to {WINDOW_LIMIT} records · {snapshot.mode}. Source time is not wall-clock UTC.</p>
    <div className="event-filters">
      <label>Search<input aria-label="Search events" value={query} onChange={event => setQuery(event.target.value)} placeholder="Event, reason or record ID"/></label>
      <label>Severity<select aria-label="Filter event severity" value={severity} onChange={event => setSeverity(event.target.value)}><option value="">All severities</option>{severities.map(value => <option key={value} value={value}>Severity: {value}</option>)}</select></label>
      <label>Event type<select aria-label="Filter event type" value={eventType} onChange={event => setEventType(event.target.value)}><option value="">All event types</option>{eventTypes.map(value => <option key={value} value={value}>Type: {value}</option>)}</select></label>
      <button type="button" onClick={() => {setQuery(''); setSeverity(''); setEventType('');}}>Clear filters</button>
    </div>
    <p className="event-result-count" role="status">Showing {events.length} of {window.length} recent records</p>
    {events.length === 0 ? <div className="event-empty">{window.length === 0 ? 'No events received in the current observation window.' : 'No events match these filters.'}</div> : <div className="table-scroll">
      <table className="event-table"><caption className="sr-only">Recent events, newest received first</caption><thead><tr><th scope="col">Source time</th><th scope="col">Severity</th><th scope="col">Event</th><th scope="col">Reason</th><th scope="col">Evidence</th></tr></thead>
        <tbody>{events.map(event => <tr key={event.event_id} className={event.event_id === selectedId ? 'event-selected' : undefined}>
          <td>{sourceTime(event.timestamp_ns)}</td><td><span className="event-severity">{event.severity}</span></td><td><b>{event.event_type}</b></td><td>{event.reason}</td>
          <td><button type="button" aria-label={`Inspect event ${event.event_id}`} aria-pressed={event.event_id === selectedId} onClick={() => setSelectedId(event.event_id)}>Inspect</button></td>
        </tr>)}</tbody>
      </table>
    </div>}
    {selected && <section className="event-detail" aria-label="Selected event evidence">
      <div className="event-detail-heading"><h3>Recorded event evidence</h3><button type="button" onClick={() => setSelectedId(null)}>Close evidence</button></div>
      <dl><div><dt>Record ID</dt><dd>{selected.event_id}</dd></div><div><dt>Event type</dt><dd>{selected.event_type}</dd></div><div><dt>Severity</dt><dd>{selected.severity}</dd></div><div><dt>Source time</dt><dd>{sourceTime(selected.timestamp_ns)}</dd></div><div><dt>Reason</dt><dd>{selected.reason}</dd></div></dl>
      <p>This event contract contains only the fields shown. Historical sensor frames, decision state and command sequence are not inferred from the current snapshot. Use a recorded replay session for its available synchronized evidence.</p>
    </section>}
  </Panel>;
}
