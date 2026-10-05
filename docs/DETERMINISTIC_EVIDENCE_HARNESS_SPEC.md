# Deterministic production-path evidence specification

Schema/harness version: 1. Written before harness implementation, 2026-09-27.
Required baseline: `96bf72bbfea88834c173000b271fd016b6b206e9`.
Branch: `tark/deterministic-evidence-harness`.

## 1. Purpose and baseline

Generate reproducible, inspectable software-only evidence for existing Phase-1
behavior. Do not introduce a safety policy or physical validation claim.
Prompt-1 ancestor: `8bff0654e2d6db3ff8414c011057274435b6b228`.
Starting tree clean; original freeze tag object remains
`94b149a50d77c45d3a8b962781c503a1055a0c8f`.
Baseline gates: 252 backend, 39 frontend, 68 protocol/interoperability and 35
recording/replay tests passing; 36 shared vectors; two strict host executables
plus cross-language harness pass. TypeScript/build pass. GCC 15.2.0.

## 2. Production entry points / no duplicate algorithm

Use the actual `create_app`, `TarkSystem`, `RuntimeOwner.start/_run/latest/stop`,
`ingest_ld2450_report`, `Pipeline.observe/decision/command/health`, `ESP32Client`,
`ESP32ProtocolSimulator`, framing/codec, `BidirectionalSerialTransport`,
EventStore, RecordingStore and `replay_recording` implementations.
REST and WebSocket observers use the actual ASGI application via TestClient.
No replacement decision function and no safety monkeypatch is permitted.
Runtime-factory injection is already a supported seam; no production changes
are planned. Entry-point identity is checked by the harness tests. A wrapping
call counter delegates to the unchanged ESP32Client.submit method so attempted
live submissions during replay are detectable independently of wire writes.

## 3. Simulated boundaries and isolation

Only monotonic time/scheduling, normalized radar input, serial transport,
receiver process/response delivery, storage and network observers are controlled.
Application mode is `replay`: it bypasses physical startup, while a controlled
capture object feeds the existing normalized radar queue. The underlying
production fields may describe this queue as REAL; every artifact explicitly
labels it TEST_FIXTURE, never physical evidence. Other devices stay unavailable.
No physical sensor values, speed, TTC or position are invented.

Runner refuses nonempty inherited TARK_* configuration except an explicitly
in-memory database. It sets in-memory storage only within its execution scope.
Factories/open/start/discovery boundaries receive fail-fast tripwires; the
harness must never call them. It does not load serial/CV/I2C hardware libraries.
All storage failure experiments use isolated in-memory/temporary storage.

## 4. Controlled time and observation model

Independent integer Pi and receiver clocks, positive initial epochs, explicit
nonnegative deltas. RuntimeOwner's existing wait seam uses an asyncio queue:
one release produces exactly one production tick; async yields schedule work,
not wall-clock sleeps. Clock-only steps can expire receiver commands without
running another decision. Every action records both clock values.

Radar reports contain an explicit source timestamp (relative age may be
negative to test future data) and normalized detections. Empty report is an
explicit queued report with zero detections; NO_REPORT queues nothing.
Multiple reports retain insertion order, including equal source timestamps.
The algorithm's actual fresh/aging/stale, track-retention and state semantics
are asserted, not replaced by desired scenario names.

## 5. Protocol clock and fault model

Use production Protocol V2, no second protocol codec. The production simulator
uses the controlled receiver clock and explicit deterministic test-only boot
identities; client request nonces use a recorded deterministic sequence.
Response delivery may be held, dropped or mutated at the transport boundary.
Inject late/empty/wrong-sequence/session/config/source responses through the
actual client receive method. Missing sequence is a malformed fixed-header
case, not an invented optional CBOR field. Legacy/malformed CBOR use existing
shared vectors. Receiver reboot clears its session; sender restart retires the
client session/pending state, not the production decision history.

The reconnect case exercises the actual bounded transport with fake ports,
queued TX/partial RX and connection-generation resets. It never opens a port.
Fresh C host/protocol gates independently verify the receiver model against
firmware; Python simulation is not claimed to be physical firmware execution.

## 6. Recording and replay

Record through TarkSystem/RecordingStore V2, including initial checkpoint.
Mid-run start does not reset live state. Retain a representative portable JSON
session/record set per scenario; temporary SQLite files are not evidence output.
Replay calls the production engine on the complete session. Compare all of its
defined deterministic fields. Capture counts, range, mismatch location and
source. Monitor live submit/write/session counts before and after replay; any
mutation fails. Legacy/incompatible data is not upgraded by this harness.

## 7. Scenario and expectation schema

JSON with strict validation and forbidden unknown fields: scenario_id, title,
purpose, initial_runtime_time, initial_receiver_time, approved configuration,
initial_reports, record_from_start, observer_profile, response_policy,
steps, expected_final_state, repeat_count and expected_invariants.
Each step has one supported action, action-specific validated arguments and
explicit expected facts. Unknown actions/expectation fields, wrong types,
negative time advance and illegal recording/replay ordering fail before running.
Actions cover time/report delivery, response faults, communication/session
restart/reconnect and recording/replay; no general Python evaluation hook.

Expected facts are independently authored assertions of existing behavior,
not values copied from the resulting trace. Any mismatch is FAIL with scenario,
step, field, expected and actual. The suite stops on an authority/opener tripwire.

## 8. Trace schema and normalized comparison

JSONL entries: schema_version, run_id, scenario_id, step_number/action,
logical_runtime_time, receiver_time, source=TEST_FIXTURE, input report(s),
observation presence/kind/source time, publication availability, actual last
generated decision, health/freshness, tracks, bounded command/sequence,
event/tick counts, location-step count, protocol session/outcome/terminal state,
communication health, receiver expiry/reason, recording sequence/count,
replay result and observer before/after counts where applicable.

Logical digest includes controlled times, observations, health, tracks, complete
decision, command, sequence, event semantics and counts, protocol state/session,
communication health, and replay result. Exclude ONLY run/scenario labels,
observer-read bookkeeping and nondeterministic host performance fields.
Random event/storage UUIDs are omitted from the trace projection at named
locations; event semantics/record sequence remain. Protocol IDs are deterministic
fixture inputs and remain INCLUDED. No generic recursive key stripping.

Representative recording exports preserve UUIDs; these exports have content
hashes but are not themselves repeatability digests. No safety-relevant field
may be discarded to manufacture equality.

## 9. Observer equivalence

EV-16 has no REST/WS reads; TestClient only hosts application lifecycle.
EV-17 performs one REST reader's bounded reads. EV-18 performs multiple REST
reads and simultaneous WebSocket observers with bounded connect/disconnect
cycles. They all use the SAME scenario inputs/ticks and protocol clocks.
Reads happen after controlled production steps and cannot drive the scenario.
Compare full logical digests and tick/command/event/location/protocol counts,
not merely final state. Wall-clock WS envelope timestamps are not decision data.

## 10. Required scenarios

| ID | Purpose |
|---|---|
| EV-01 | Fresh evidence / one decision-command-event / replay |
| EV-02 | Existing AGING semantics without invented WARN |
| EV-03 | Stale evidence cannot publish current NORMAL |
| EV-04 | Late queued report retains old source age |
| EV-05 | Future timestamp rejected/faulted |
| EV-06 | Explicit valid empty report |
| EV-07 | Missing report, contrasted with EV-06 |
| EV-08 | Ordered multi-report batch |
| EV-09 | Equal-source-time ordered updates |
| EV-10 | Communication loss and expiry without incoming command |
| EV-11 | Late ACK never becomes timely success |
| EV-12 | Malformed/wrong ACK health/correlation |
| EV-13 | Receiver restart and old-session rejection |
| EV-14 | Sender-session restart and stale pending authority |
| EV-15 | Actual transport reconnect flush |
| EV-16 | Zero-observer canonical baseline |
| EV-17 | One-observer equivalent run |
| EV-18 | Multiple-observer/reconnect equivalent run |
| EV-19 | Mid-run recording checkpoint |
| EV-20 | Full fresh/aging/empty/stale/loss/expiry/recovery/replay story |

Five independent repetitions minimum, ten for EV-01/03/04/06/10/13/16/17/18/20.
Use seed 42 for deterministic fixture identities, not hidden global randomness.
Each repetition has a separate application, scheduler, client, receiver and DB.
Store all repetition digests/results; retain one full representative trace and
recording per scenario to bound committed artifacts.

## 11. Manifest, package and verification

Output controlled text under evidence/prompt3: manifest.json,
evidence_summary.json, scenarios/, runs/, traces/, replay/, hashes.json, README.md.
Manifest records UTC creation, git HEAD/branch/dirty status, source fingerprints,
package/tool versions, protocol/config/scenario identities, Python/platform,
seed, schema, disabled traction and hardware_access/physical_validation=false.
Build-time dirty status is truthful: evidence is generated before its containing
commit, and source hashes identify the exact harness/production bytes used.
No circular claim that pre-commit artifacts were generated from their own commit.
Export text uses explicit LF newlines; a scoped Git rule preserves those bytes.
Text source fingerprints normalize CRLF to LF (as production replay already
does), with the normalization declared in the manifest. Artifact hashes remain
hashes of exact bytes; no artifact normalization occurs during verification.

SHA-256 inventory covers all artifacts except itself, using relative paths,
sizes and content hashes. These are fingerprints, not signatures. Verification
checks required inventory coverage, missing/extra files, trace/result/digest
agreement, config identity, all iterations and observer equivalence. A tampered
deterministic field, replay mismatch, wrong config or wrong protocol must fail.
CLI exits zero only for complete passing evidence, nonzero for FAIL/ERROR.
Default output refuses overwrite; reproduce into a fresh directory.

## 12. Failure tests, limits and gates

Test schema, unknown action, wrong expectations, illegal order, manifest/hash
inventory, missing artifacts, deterministic exclusions, tamper/replay/config/
version negative controls, physical-opener/zero-output/replay tripwires, storage
failure and runtime worker failure. Failed worker publication/readiness must
be unavailable; cached NORMAL cannot remain current. Fault injection changes
external storage/scheduler behavior only, never safety code.

Measure scenario host duration, counts and artifact sizes as development-host
diagnostics, NOT WCET, real-time or physical response guarantees. Inspect EV-01,
03,06,10,16–18,20 artifacts manually. Run complete backend/frontend, TypeScript,
production build and fresh strict C/vector/interoperability gates. Commit only
after all gates and file/privacy audits pass; exactly one local commit, no push.

## 13. Invariants and limitations

Every live tick: DISABLED_PHASE_1; permitted speed/left/right exactly zero.
No browser, replay or harness actuation authority; no hardware access. Tripwire
failure stops immediately. No sensor commissioning or certification claim.
This measures existing simplified provisional algorithms, not physical braking,
fusion, TTC validity, watchdog hardware or transport latency. Prompt 4 remains
separate. A new out-of-scope safety/concurrency defect triggers the stated stop
condition instead of an undocumented redesign.
