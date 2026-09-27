# Prompt 3 — deterministic production-path engineering evidence

Date: 2026-09-27. SOFTWARE-ONLY / TEST_FIXTURE. No physical validation.

## 1. Executive result

All 20 required scenarios passed all 150 independent repetitions. The final
backend suite passed 322 tests (252 existing + 70 harness tests); frontend 39,
TypeScript and production build passed. Fresh strict C host tests and the
Python/C interoperability fixture passed. The evidence package independently
verifies its inventory, expected outcomes, logical digests and replay.

The existing production decision, runtime, protocol, firmware, UI and safety
implementations were not edited. This is evidence for the current provisional
Phase-1 software, not proof of a physically safe vehicle or certified system.

## 2. Baseline

- Required and actual starting HEAD: `96bf72bbfea88834c173000b271fd016b6b206e9`.
- Starting message: `CLOSE PROTOCOL FIRMWARE AND REPLAY SEMANTICS`.
- Prompt-1 ancestor: `8bff0654e2d6db3ff8414c011057274435b6b228`.
- Starting working tree: clean.
- Working branch: `tark/deterministic-evidence-harness`, created from that HEAD.
- Freeze tag `tark-software-freeze-2026-09-20` object remains
  `94b149a50d77c45d3a8b962781c503a1055a0c8f`.
- No push, tag change, hardware operation or Prompt-4 work is authorized here.

The manifest truthfully identifies the pre-commit baseline and dirty tree;
SHA-256 source fingerprints identify harness/production text with CRLF
normalized to LF; artifact fingerprints identify exact exported bytes.
It does not claim that artifacts were generated from their own future commit.

## 3. Harness architecture

`app.evidence` is an offline tool, imported by its CLI and tests, not by the
application runtime. `schema.py` defines closed bounded inputs; `catalog.py`
authors expected facts; `runner.py` drives the existing app; `controls.py`
injects negative controls; `artifacts.py` exports/verifies results.

The specification was written before implementation. Each independent run has
its own application, controlled scheduler, endpoint, client and in-memory
SQLite stores. One wrapping call counter delegates to the actual client
submit method; it does not replace protocol validation or command logic.

## 4. Production path exercised

`create_app` lifespan → `RuntimeOwner.start/_run` → `TarkSystem.tick` → ordered
normalized radar queue → `Pipeline.observe/decision/command` → EventStore and
RecordingStore → `ESP32Client.submit` → production COBS/CRC32C/canonical CBOR
codec → `ESP32ProtocolSimulator` supervision → ACK/NACK/STATUS validation →
cached REST/WebSocket publication → stopped-session `replay_recording`.

`BidirectionalSerialTransport` connection-generation, queue-flush, partial RX
and bounded partial TX methods are exercised with fake byte ports. C host tests
separately exercise the real firmware decoder/service/supervisor and encode
responses decoded by Python. Python endpoint simulation is not represented as
executing firmware or operating a physical ESP32.

Entry-point tests verify actual class/method identities and source locations.
No decision/TTC/stopping/PV-SOE calculation is copied into the harness.

## 5. Simulated boundaries

Controlled: independent monotonic clocks, scheduling releases, normalized radar
reports, protocol response delivery/reboot, fake serial ports, storage faults,
and in-process ASGI observers. No external network or hardware access is used.

Runtime mode is REPLAY to disable physical startup while using the existing
normalized non-simulation queue. Internal recording report labels retain the
production value REAL; the manifest, exports and traces explicitly label the
entire experiment TEST_FIXTURE. This is not evidence of real radar reception.

Inherited nonempty TARK_* values are rejected, except an in-memory DB. Physical
start/open boundaries and optional hardware-library imports have fail-fast
tripwires. All successful runs report zero physical-opener attempts. The
deliberate tripwire negative control blocks a call before any hardware access.

## 6. Controlled time model

Pi starts at 10,000,000,000 ns and the receiver at 1,000,000,000 ns. Each scenario
explicitly advances either clock; receiver expiration can run without incoming
frames or another Pi decision. Async queue releases drive one production tick;
there are no wall-clock sleep-based freshness assertions. WS receives have a
five-second failure bound, not a simulated-time or performance requirement.

Radar source time is distinct from processing time. Late/future/same-time
reports preserve their submitted source timestamps and insertion order.
Expected state/freshness semantics are authored from the existing contract,
not inferred from whatever output a run happens to produce.

## 7. Scenario matrix

| ID | Existing behavior tested | Repetitions |
|---|---|---:|
| EV-01 | Fresh report; one event/command per tick; replay | 10 |
| EV-02 | AGING retains the current NORMAL semantics | 5 |
| EV-03 | Stale evidence cannot publish current NORMAL | 10 |
| EV-04 | Queued old report keeps its source timestamp | 10 |
| EV-05 | Future report faults health | 5 |
| EV-06 | Valid empty report is FRESH, no envelope → STOP | 10 |
| EV-07 | Missing report remains MISSING / UNKNOWN | 5 |
| EV-08 | Multiple ordered reports in a single tick | 5 |
| EV-09 | Equal source timestamps retain report order | 5 |
| EV-10 | Response loss, pending expiration, receiver expiry | 10 |
| EV-11 | Late ACK cannot renew communication health | 5 |
| EV-12 | Invalid ACKs; valid NACK/STATUS semantics | 5 |
| EV-13 | Receiver reboot and old/duplicate rejection | 10 |
| EV-14 | Sender reset retires pending authority | 5 |
| EV-15 | Transport reconnect flushes partial RX/queued TX | 5 |
| EV-16 | Zero-observer canonical scenario | 10 |
| EV-17 | Same inputs with one REST observer | 10 |
| EV-18 | Same inputs with multiple REST/WS observers | 10 |
| EV-19 | Mid-run recording checkpoint | 5 |
| EV-20 | Full loss/expiry/reconnect/fresh-recovery story | 10 |

## 8. Scenario results

EV-01 through EV-20: PASS, no skipped scenario or failed repetition.

The actual exported EV-01, EV-03, EV-06, EV-10, EV-16, EV-17, EV-18 and EV-20
trace files were inspected, not merely their test exit codes. EV-05, EV-08,
EV-09 and EV-19 recording details were also checked.

- EV-03: after 1.1 s without a tick, the LAST GENERATED NORMAL snapshot is
  marked publication unavailable; the next tick emits UNKNOWN / STALE.
- EV-04: the consumed report's last-seen time remains 8,000,000,000 ns at a
  processing time of 10,000,000,000 ns; it does not become fresh.
- EV-05: INVALID_OBSERVATION_TIMESTAMP / STALE / UNKNOWN, zero command.
- EV-06 versus EV-07: FRESH/STOP for a valid empty observation without a retained
  envelope, versus MISSING/UNKNOWN for no observation. EV-20 also preserves
  existing retention: an empty report does not automatically delete old tracks.
- EV-08 preserves both reports and their distinct times. EV-09 preserves both
  equal-time updates (5 m then 2 m) in the recording.
- EV-10: no new command at the clock-only expiry step; receiver reports
  COMMAND_EXPIRED, pending commands expire, and host health is NOT_CONNECTED.
  The last generated safety state can remain NORMAL while link health fails;
  the harness does not invent a communication-to-safety policy. All commands
  remain zero. Current client health and last-tick snapshot fields are separate.
- EV-20: fresh → aging → empty → stale/UNKNOWN → response loss → receiver expiry
  → transport/session renewal → fresh/NORMAL recovery → stopped recording/replay.

## 9. Repeatability results

150 independently constructed runs, deterministic seed 42. Every repetition
matches its scenario's complete logical trace digest. No nondeterminism was
observed in the compared fields.

Only top-level run_id, scenario_id and observer_reads are excluded from the
trace digest. Event/storage UUIDs are omitted at named trace projections, not
by recursively discarding fields. Controlled timestamps, full decisions,
health/freshness, tracks, command values/sequences, protocol sessions, terminal
states, receiver expiry, event semantics/counts and replay remain included.
Host durations are outside the logical trace. Portable recordings retain UUIDs
and receive independent file hashes.

## 10. Observer-independence results

EV-16/17/18 digest:
`fd21d3e2f028a5bfe7264865da2631f1d262cdd0046769a7ee41ecf88765bfef`.

Each has the same five ticks, five persisted events and five production command
submissions. EV-17 reads five REST endpoints per step. EV-18 uses three REST
readers plus three simultaneous WS connections over two reconnect cycles per
step. Every observer boundary compares before/after live authority and counts.
No observer drives time, reports, sequence, location or command generation.

## 11. Protocol-fault results

Production Protocol V2 is unchanged. EV-11 rejects a late ACK after session
retirement. EV-12 covers empty payload, missing fixed-header sequence data,
wrong sequence/session/configuration/source and malformed canonical CBOR.
None renews last_exchange_ns; valid NACK is DEGRADED and STATUS is telemetry,
not renewed round-trip health. EV-13 rejects duplicate and old-session commands
across receiver reboot. EV-14 supersedes pending sender-session work.

EV-15/20 use the actual transport reset/flush and bounded partial-write logic:
old-port bytes remain zero, old partial RX cannot complete a stale frame,
queued authority is dropped, and only the newly submitted frame reaches the
new fake port. No physical USB/session identity is claimed.

## 12. Replay results

Every repetition records/stops/replays through production implementations and
reports MATCH. The exported 20 representative full sessions independently
replay MATCH during artifact verification. Replay leaves live submit count,
wire-write count, sequence, pending/terminal state, session and event counts
unchanged.

EV-19 starts recording at checkpoint sequence 2; its two saved commands remain
sequences 3 and 4. No live-state reset is used to manufacture repeatability.
The existing Prompt-2 replay tests, including full-session handling beyond
10,000 records, remain unchanged and pass in the full suite.

## 13. Negative controls

All ten exported controls passed: deliberate decision tamper changes the
digest; changed recorded envelope produces MISMATCH at decision index 1;
wrong config identifier/value fingerprint and legacy protocol version reject;
physical opener and nonzero-output tripwires reject; wrong expected sequence
900 fails explicitly; storage and worker failures publish HTTP 503 on status
and readiness without increased authority.

Harness tests additionally reject invalid scenario schemas/actions/types,
illegal recording order, non-isolated environment, missing/extra artifacts,
nested unlisted hashes.json, rehashed deterministic-field tamper, wrong
manifest config/protocol/source identity, missing repetitions, observer digest
changes and replay mismatch. Rehashing bytes alone cannot suppress semantic
checks. Hashes are fingerprints, not cryptographic signatures of provenance.

## 14. Safety invariant results

All observed live commands and decisions: permitted speed = 0, left = 0,
right = 0; traction and receiver output state = DISABLED_PHASE_1.
Browser and replay have no command authority. No physical opener was reached
in any scenario. No hardware, COM/USB/I2C, sensors, motors or firmware flashing
were accessed. No physical or mine-certification claim is made.

## 15. Software-only performance diagnostics

Exported 150-run host diagnostics: sum 15.244383 s; mean 0.10162922 s/run;
minimum 0.040002 s; maximum 0.768906 s. Runs include ASGI/SQLite setup,
observer work and replay; these values are not control-loop benchmarks.

The package contains 85 text artifacts, 982,419 bytes including hashes.json
(971,433 inventoried bytes excluding that self-excluded inventory). Histories
are short and bounded. No RAM, embedded latency, WCET, physical braking time
or real-time guarantee is inferred from these measurements.

## 16. Full regression results

| Gate | Result |
|---|---|
| Prompt-3 harness | 70 passed in final full run |
| Backend full | 322 passed, 0 failed/skipped, 48.74 s |
| Unchanged Prompt-1 integrity | 65 passed within full suite |
| Protocol/interoperability | 68 passed within full suite |
| Recording/replay | 35 passed within full suite |
| Shared protocol vectors | 36, exercised by Python and fresh C decoder |
| Strict host protocol/shared vectors | PASS, freshly compiled |
| Strict host session/service/supervisor | PASS, freshly compiled |
| C/Python command-response interoperability | PASS, freshly compiled fixture |
| Frontend | 39 passed / 9 files, 6.25 s |
| TypeScript | PASS |
| Production frontend build | PASS, Vite build 4.48 s |
| Artifact generation / independent verification | PASS, 20 scenarios / 150 repetitions |

Commands: `pytest -q -p no:cacheprovider --tb=short`, `pnpm test`,
`pnpm run lint:types`, `pnpm run build`; evidence CLI below. Python commands
were executed with the existing bundled Python 3.12.14 and existing project
site-packages. Before pytest import, inherited TARK_* variables were cleared
and TARK_DATABASE_PATH=:memory: was set. No dependencies were installed.
The first focused harness run was 69/69; one added hash-inventory regression
brings the final harness count to 70. Earlier full run: 321/321; subsequent
full runs: 322/322 in 48.16 s and final LF-export run 322/322 in 48.74 s.

The unchanged `test_protocol_correctness.py::host` fixture compiles fresh
host_test, task7b_host_test and interop_host with GCC 15.2.0 using
`-std=c11 -Wall -Wextra -Werror`, and runs both host executables plus the
cross-language cases. The first full-run binaries were also executed directly:
`host protocol/shared semantic vectors PASS` and
`host session/periodic supervisor PASS`. Final full run freshly rebuilt/passed
the same fixture again.

Windows limitation recorded accurately: a separate invocation of
`firmware/esp32/tests/run_host_tests.sh` passed host_test but its task7b_host_test
was denied; direct retry returned `OSError`, WinError **4551**,
**An Application Control policy has blocked this file**. That shell-helper
attempt is BLOCKED, not counted as passed. The existing approved pytest
temporary-directory fixture independently compiled and successfully executed
both tests. No security policy was disabled, no blocked binary was relocated,
no tests were skipped, and no source was changed to bypass the restriction.

Non-fatal existing warnings: two upstream Starlette/TestClient/AnyIO
deprecations and the existing lazy MapView bundle-size advisory (816.49 kB).
No frontend change or dependency upgrade was made for these warnings.

## 17. New defects found

No new production defect identified in the executed coverage. This is not a
zero-bugs claim. No safety-policy, architecture or concurrency redesign was
needed. During harness development, the shared-vector selector was corrected
to its actual `legacy_version` name and inventory exclusion was narrowed to
the single root hashes.json; a nested-hash-file regression covers the latter.
The release audit also found Git line-ending conversion could change hashed
artifact bytes; explicit LF export plus the scoped Git rule fixes this, and
text source hashes declare CRLF-to-LF normalization. Final evidence was freshly
regenerated and verified after that harness-only correction.

## 18. Files changed

New only:

- `.gitattributes` (scoped evidence-byte preservation; no application rules)
- `backend/app/evidence/__init__.py`
- `backend/app/evidence/schema.py`
- `backend/app/evidence/catalog.py`
- `backend/app/evidence/runner.py`
- `backend/app/evidence/controls.py`
- `backend/app/evidence/artifacts.py`
- `backend/tests/test_evidence_harness.py`
- `scripts/run_evidence_harness.py`
- `docs/DETERMINISTIC_EVIDENCE_HARNESS_SPEC.md`
- `docs/DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md`
- 85 controlled text artifacts under `evidence/prompt3/`.

No pre-existing tracked file, production algorithm, firmware, frontend,
configuration, dependency or deployment file was changed. Generated frontend
build/cache files stay ignored and are not release changes.

## 19. Evidence artifact inventory

`evidence/prompt3/manifest.json`, `evidence_summary.json`, `negative_controls.json`,
`hashes.json`, `README.md`; 20 scenario definitions, 20 repetition result files,
20 representative JSONL traces and 20 portable full recording/replay exports.
No database, binary, credential, absolute user directory, raw physical input
or environment-secret value is included. Synthetic protocol nonces/session
identifiers are deterministic fixture values, not credentials.

From repository root in the existing project Python environment:

```text
python scripts/run_evidence_harness.py --output <fresh-output-directory>
python scripts/run_evidence_harness.py --verify evidence/prompt3
python -m pytest -q -p no:cacheprovider backend/tests/test_evidence_harness.py
```

The CLI refuses an existing output directory and unsafe inherited TARK_*
configuration. It returns nonzero on failure and never overwrites a prior
bundle. Source fingerprints are checked against the current checkout during
verification; regenerate separately after any source/configuration change.
Exports explicitly use LF, and the scoped Git attribute preserves LF for this
inventoried package so checkout cannot silently alter hashed bytes. Text source
fingerprints explicitly normalize CRLF to LF, like production replay; artifact
hashes do not normalize bytes. A regression checks LF exports on Windows.

## 20. Limitations

This validates deterministic behavior of the current simplified provisional
software, not the adequacy of its physical safety model. GNSS/camera/thermal/
IMU commissioning, encoder pulses, motors, USB binding and physical watchdog/
E-stop behavior remain unverified. No physical radar decoder claim follows
from feeding normalized reports. Host C regression is not ESP32 hardware.
Observation-free safety interpretations are exactly the existing policy.

No second pipeline or protocol implementation was introduced. Repeatability
is shown for these controlled scenarios and compared fields, not every
possible input or host schedule. WS observer testing is ASGI-level, not a
browser rendering/performance test. Windows application control can block
particular fresh executables; future runs must report any denial truthfully.

## 21. Prompt-4 readiness

READY FOR PROMPT 4.
All requested software evidence gates have passed; no new production defect
or unresolved scenario mismatch was found. The separate shell-helper OS denial
does not replace the successfully executed canonical fresh-host fixture.

Release action: exactly one local commit,
`BUILD DETERMINISTIC ENGINEERING EVIDENCE HARNESS`.
No push, tag movement, physical validation or Prompt-4 implementation.
