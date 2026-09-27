# Replay guide — recording format 2

New recordings contain `OBSERVATION_TICK_V2` entries and a versioned session
header. Each tick records **all ordered radar reports** supplied to the live
pipeline, including source, report timestamp and normalized detections. A
report with `detections: []` is a valid empty observation; an empty outer report
list means no report arrived. Neither representation is substituted for the other.

Starting a recording snapshots the existing track/freshness/timestamp-fault and
command-sequence state under the same lock as the runtime tick. It does not
reset the live pipeline. Replay reconstructs a separate Pipeline from that
checkpoint, observes reports in order, and makes one decision/command per tick.
No hardware adapter, live TarkSystem or ESP32 client is constructed by replay.

## Compatibility and evidence

The header contains recording/input-schema versions, software ID and a
SHA-256 fingerprint of the decision/recording implementation, configuration
identifier and configuration-value fingerprint, original source mode and
initial checkpoint. Runtime mode is excluded from the configuration-value hash
so offline replay can verify a real-radar recording without starting hardware;
the original source is independently validated. These hashes identify content,
not cryptographically authenticated evidence.

Only stopped COMPLETE/FULL/INTERRUPTED sessions can be verified in full.
SQLite adds metadata without deleting old sessions. Legacy V1 sessions remain
catalogued as `LEGACY_NONDETERMINISTIC`; they are not guessed/migrated into a
deterministic result. Incompatible software/configuration/schema/checkpoint,
corrupt JSON, invalid evidence and missing/duplicate/out-of-order record
sequences produce explicit errors. An empty session cannot claim MATCH.

`RAW_FRAME_V1` diagnostic records are preserved, validated and counted, but are
not independently converted to observations during replay. Normalized report
ticks, not a second decoder pipeline, provide the decision inputs.

## Full verification and UI

`GET /api/v1/replay/sessions` lists sessions.
`GET /api/v1/replay/sessions/{id}/timeline` loads an isolated REPLAY timeline for
selection, seek, step, play/pause and reset in the existing HMI.
`POST /api/v1/replay/sessions/{id}/verify` verifies every stored record using
256-record keyset pages, up to the existing 50,000-record session bound.
There is no 10,000-record prefix reported as a whole-session result.

The verification response includes complete status, verified record/decision
counts, first/last sequence and first divergence. Only the first 100 computed
decisions are returned as a diagnostic preview; this does not limit validation.
The timeline is a bounded full-session response, not a streaming UI redesign.

Deterministic comparison includes the entire decision (state, reason,
constraints, permitted speed, envelope and stopping fields), radar health,
bounded command (including sequence/timestamps), and event except its random
`event_id`. Raw diagnostics count toward coverage but have no recomputed
decision. A plain SIM1 computation without an original comparison is labelled
`NOT_COMPARED`, not MATCH.

Replay never submits its computed command, replaces live telemetry or changes
traction. Browser/public-demo mutation restrictions remain unchanged. MATCH
means repeatability of supplied software evidence only, not validated stopping
distance, safe speed, sensors, motors or mine operation.
