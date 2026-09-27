# Protocol, firmware supervision and replay correction

## A. Baseline and scope

Started: 2026-09-26. Last verification: 2026-09-27.
Starting HEAD: `8bff0654e2d6db3ff8414c011057274435b6b228`.
Starting branch: `tark/software-integrity-correction`; clean worktree.
Working branch: `tark/protocol-replay-correction`.
Freeze tag object remains `94b149a50d77c45d3a8b962781c503a1055a0c8f`.
No push, tag change, physical device access, or actuation is authorized.

Baseline SHA-256 inventories:

- `docs/ESP32_PROTOCOL_V1.md`: `7F2A4191EAAE2C6AAF24569D2D19721A420C9D47E848E51E21CDC47179D0A0D8`
- `protocol_vectors.json`: `9AB42CD91FE32459D929A222E1918E2C5E826A3D3FB7B1B79DE19C555D62113B`
- `firmware/esp32/tests/protocol_vectors.h`: `4B4FD81E0B97328D6A5319F60B5668C73C04C9485C6492881C77E85448A2BF56`

## B. Prompt-2 branch

`tark/protocol-replay-correction`, created from the exact Prompt-1 baseline.
Changes from the interrupted work were preserved, not reset or recreated.
All final gates now pass. This report accompanies the single authorized local
completion commit, `CLOSE PROTOCOL FIRMWARE AND REPLAY SEMANTICS`. No push or
freeze-tag change; Prompt 3 is not started.

## C. Before-fix reproduction ledger

Created before production edits. All fourteen issues were independently
REPRODUCED against the baseline and their corrections are now implemented.
The rows retain their original observed results; final gate status is below.

| ID | Source / reproduction | Observed baseline | Finding | Root cause / planned correction |
|---|---|---|---|---|
| PR-01 | `communication/esp32/protocol.py`; sender 8 h, receiver 12 s, then reverse | First accepted with sender absolute deadline; reverse rejects COMMAND_EXPIRED | REPRODUCED | Cross-clock comparison; bounded sender duration converted to receiver-local expiry |
| PR-02 | Same validator; 27 h lifetime | Accepted | REPRODUCED | No maximum lifetime; explicit reviewed bound |
| PR-03 | `ESP32Client.receive`; ACK `{}`, correct pending sequence, after deadline | accepted=True, MATCHED, reason UNSPECIFIED | REPRODUCED | Default success and no deadline/schema validation |
| PR-04 | `ESP32Client.submit`; 10,000 unacknowledged commands | 10,000 pending entries | REPRODUCED | No automatic expiry or count bound |
| PR-05 | `TarkSystem.sensor_snapshot`; fake running worker with no feedback | REAL / ONLINE / age 0 | REPRODUCED | Worker existence substitutes for protocol evidence |
| PR-06 | `firmware/.../command_payload.c`; fresh strict GCC DLL called via ctypes with canonical commands | C accepts 0.0/1/65504.0; rejects legal 0.1, -0.1 and signed -1 | REPRODUCED | Only unsigned integers and float16 implemented; support canonical finite float16/32/64 and signed integers |
| PR-07 | `decode_frame`; duplicate key a2617801617802, overlong integer a161781801, trailing CBOR a0a0 | All accepted | REPRODUCED | Decoded map alone does not prove canonical/complete input |
| PR-08 | `serial_transport.py`; queue frame and partial RX, close/connect with fake opener | One queued frame and four partial RX bytes retained | REPRODUCED | No connection-generation flush or command deadline at write |
| PR-09 | `protocol/service.c`; fresh strict host executable accepts at 1 s, receives zero bytes at 3 s | reason NONE, zero periodic messages | REPRODUCED | No independent expiry/status tick; add board-neutral tick, no physical scheduler claim |
| PR-10 | Actual TarkSystem recording: target at 1 s then valid empty at 2.1 s | Original NORMAL, STOP; replay NORMAL, UNKNOWN | REPRODUCED | Empty report collapsed into missing report |
| PR-11 | Actual TarkSystem recording: near target then different farther target in one tick | Original RESTRICT; replay NORMAL | REPRODUCED | Only final report retained |
| PR-12 | Actual TarkSystem: target before start, no report after start | Original NORMAL; replay UNKNOWN | REPRODUCED | Initial tracks/freshness not captured |
| PR-13 | Actual verify endpoint: 10,001 persisted records, deliberate differing final decision | MATCH, 10,000 replayed, 10,001 stored | REPRODUCED | Hard-coded prefix verified as entire session |
| PR-14 | Actual session and tick objects emitted during PR-12 | No software/schema/checkpoint/config-value identity in session | REPRODUCED | Manual configuration label is insufficient; versioned metadata and strict compatibility needed |

### Explicit protocol revision authorization

The V1 text requires a future expiry but does not define a shared monotonic
epoch. V1 also lacks a reliable reboot/session discriminator. The user
explicitly approved a versioned session-handshake revision on 2026-09-26.
V2 rejects legacy V1 frames; Python, firmware and vectors changed together.
No physical USB or random-number source is inferred. The board-neutral service
requires an injected unique boot identity; absent that binding it stays unavailable.
Sender lifetime is bounded to the current 500 ms configured timeout and
converted to a receiver-local deadline. Replayed handshake requests must
produce a new receiver session, not revive the old one.

## D. Protocol timing after correction

The sender supplies uint64 timestamp/valid-until values. Their difference must
be positive and at most 500,000,000 ns, the existing Phase-1 timeout ceiling.
Receiver-local expiry is receipt time plus that bounded duration; overflow is
rejected. No comparison between Pi and ESP32 absolute clock epochs remains.
Pi-side enqueue/write/correlation uses Pi time; firmware supervision uses
receiver time. Heartbeat cannot extend or revive a command. Receiver rollback
fails closed. Tests cover 1 ns, zero, normal 250 ms, maximum 500 ms, maximum+1,
multi-hour lifetime, uint64 boundary and opposite 8-hour/12-second epochs.

## E. Session/reconnect contract

V2 SESSION_OPEN carries a fresh Pi request ID and configuration; SESSION_READY
echoes it and supplies a receiver boot-ID + generation session. Every valid
open advances the receiver generation, including replayed opens. Commands and
heartbeats require that exact session and strictly increasing uint32 sequences.
No sequence wrap is accepted inside a session. Disconnect retires correlation
and flushes TX/partial RX; unsatisfied response deadlines force a new handshake
even when a receiver reboot does not disconnect the serial object.

The firmware service requires a unique-per-boot identity from a reviewed board
binding. Missing identity leaves it unavailable; host tests inject fixture IDs.
Neither CRC nor the session nonce is cryptographic peer authentication. No
physical latency or synchronized-clock guarantee is claimed.

## F. CBOR accepted subset and shared vectors

Definite flat maps, at most 24 unique printable ASCII keys; keys ≤31 bytes and
nonempty text values ≤127 bytes. Canonical key ordering, shortest integers and
shortest exact finite binary16/32/64 encodings are required. Booleans/null are
distinct from numbers. Byte strings, nesting, tags, indefinite lengths,
duplicates, overlong encodings, trailing objects, NaN and ±infinity are rejected.
Command integers used as floating quantities must be exactly representable
in binary64. Field schemas and ranges match in Python/C.

There are 36 shared vectors, including COMMAND, ACK, NACK, STATUS, HEARTBEAT,
SESSION_OPEN/READY, numeric domains, TTL bounds, invalid fields, structural
CBOR errors, CRC corruption, legacy version, truncated frame and both signs
of infinity. JSON remains authoritative; the generated C header is checked
against it. Nonzero values are PROTOCOL INTEROPERABILITY TEST ONLY — NO
ACTUATION AUTHORITY. C compares decoded numbers/reasons, not only bytes.

## G. Response validation

Exact ACK/NACK/STATUS schemas; no default-success fields. Current session,
configuration and expected source are mandatory. ACK/NACK must match a pending
sequence, echoed sender timestamp and unexpired host deadline. ACK reason must
match COMMAND versus HEARTBEAT. NACK must carry an allowed rejection reason.
Applied outputs must be finite zero and output state DISABLED_PHASE_1.
STATUS has receiver time and last correlated sequence; it is telemetry only,
never current acknowledgement or a health-freshness renewal. Unknown, duplicate,
late, wrong-identity/source or malformed responses cannot become healthy evidence.

## H. Pending and transport bounds

Client pending limit 64; terminal and seen-response histories 256. Explicit
ACKNOWLEDGED/REJECTED/EXPIRED/SUPERSEDED/PROTOCOL_ERROR outcomes. Correlation
is locked. TX queue ≤64, frame ≤640 bytes, payload ≤512. Queued items carry
connection generation/deadline; stale items are dropped. Partial writes may
finish only in the same connection before deadline. Zero/invalid counts or
exceptions reset transport; partial RX and queued tails do not cross reconnect.
Serial write timeout is explicit. Reset-callback failures close opened objects
instead of leaking them. Shutdown remains bounded and does not falsely report
a live worker as stopped.

## I. Communication-health semantics

Recent validated ACK → ONLINE; correlated NACK → DEGRADED; expired exchange
→ STALE, or NOT_CONNECTED after retiring its session. No exchange/handshake
alone → NOT_CONNECTED. Worker liveness is independent. Expired accepted feedback
is not shown as the current command result. Simulator is SIMULATION; firmware
endpoint is REAL, which is not physical-verification evidence.

## J. Board-neutral firmware lifecycle

Service receive → bounded frame/CBOR validation → session/config/sequence/TTL
checks → supervisor → canonical ACK/NACK. Independent service tick supervises
expiry without incoming data and emits STATUS on a 250 ms interval. Disconnect
clears the session. Malformed input, rollback, rejection and timeout leave
logical output disabled. The C service contains no device APIs or GPIO writes.

`app_main` initializes disabled state and explicitly reports
UNAVAILABLE_HARDWARE_BINDING_PENDING. USB RX/TX choice, unique boot identity,
serialized scheduling and actual hardware watchdog binding are not invented.
No ESP-IDF build/flash or physical watchdog verification is claimed.

## K. Replay recording semantics

New V2 ticks retain every ordered normalized report with source/timestamp and
batch order. Valid empty detection lists are explicit reports, distinct from
no report. Mid-run recording snapshots tracks, last-seen time, timestamp-fault
state and command sequence under the existing runtime tick lock. The live
pipeline is not reset. Replay reconstructs a separate Pipeline and invokes
the unchanged observation/decision/command logic in the original order.

Complete verification iterates 256-record keyset pages through the entire
bounded session (up to 50,000 records), never a 10,000-record prefix. Coverage
counts/range and first divergence are returned; only the decision preview is
limited to 100 entries. A deliberate mismatch at record 10,001 is found both
through the engine and actual verify route. Raw diagnostic records are counted
and validated, not independently decoded into a second observation pipeline.

## L. Deterministic comparison

Compare the complete decision object, radar health, bounded command, and event
except random event_id. This includes state, reason, constraints, permitted
speed, envelope/stopping fields, freshness, timestamps and sequence. Replay
does not compare random storage IDs. Plain SIM1 computation is NOT_COMPARED
until compared against original decisions. Empty/missing/batch/mid-run/mixed/
future/same-time/stale scenarios reproduce original deterministic evidence.

## M. Compatibility and corruption

Format 2 / ORDERED_RADAR_REPORTS_V2, software ID/fingerprint, configuration
identifier/value fingerprint, original source mode and initial checkpoint are
required. Mode is excluded only from the configuration-value fingerprint so
real recordings can be replayed offline without hardware startup; source is
validated independently. Hashes identify content, not signed evidence.

SQLite metadata migration preserves old sessions. Legacy V1 without sufficient
initial state is LEGACY_NONDETERMINISTIC, never fabricated into MATCH. Unsupported
version/configuration/source/checkpoint, corrupt JSON/evidence and record-order
gaps fail explicitly. Corrupt catalogs return a controlled API error, not a
server crash. Replay creates no TarkSystem/transport and cannot submit commands.

## N. Exact files changed

43 intended files (paths relative to repository root):

```text
backend/app/communication/esp32/protocol.py
backend/app/communication/esp32/serial_transport.py
backend/app/communication/esp32/usb.py
backend/app/config.py
backend/app/domain/models.py
backend/app/main.py
backend/app/replay/engine.py
backend/app/replay/store.py
backend/app/services/system.py
backend/tests/test_api.py
backend/tests/test_integration.py
backend/tests/test_protocol.py
backend/tests/test_protocol_correctness.py
backend/tests/test_protocol_vectors.py
backend/tests/test_recording_replay.py
backend/tests/test_replay_correctness.py
docs/ESP32_PROTOCOL_V1.md
docs/PROTOCOL_FIRMWARE_REPLAY_CORRECTION_REPORT.md
docs/PROTOCOL_IMPLEMENTATION.md
docs/REPLAY_GUIDE.md
docs/TEST_REPORT.md
firmware/esp32/KNOWN_LIMITATIONS.md
firmware/esp32/PROTOCOL_IMPLEMENTATION.md
firmware/esp32/README.md
firmware/esp32/main/app_main.c
firmware/esp32/main/command/command_supervisor.c
firmware/esp32/main/command/command_supervisor.h
firmware/esp32/main/protocol/command_payload.c
firmware/esp32/main/protocol/command_payload.h
firmware/esp32/main/protocol/response.c
firmware/esp32/main/protocol/response.h
firmware/esp32/main/protocol/service.c
firmware/esp32/main/protocol/service.h
firmware/esp32/main/protocol/tark_protocol.c
firmware/esp32/main/protocol/tark_protocol.h
firmware/esp32/main/status/status.c
firmware/esp32/tests/host_test.c
firmware/esp32/tests/interop_host.c
firmware/esp32/tests/protocol_vectors.h
firmware/esp32/tests/run_host_tests.sh
firmware/esp32/tests/task7b_host_test.c
protocol_vectors.json
scripts/generate_protocol_vectors.py
```

## O. Focused tests and fresh C execution

Before the final four negative vectors were added: 164 focused tests passed
(protocol/vector/interoperability 68, replay-correctness 31, unchanged Prompt-1
integrity 65). Production logic has not changed since that pass.

After the shared inventory reached 36 vectors: standalone strict fresh host
protocol/shared-vector and service/supervisor executables both compiled and
ran successfully, exit 0. Python vector/header checks also pass. The latest
pytest cross-language fixture now also compiles and runs successfully. Earlier
Windows Application Control failures are retained as historical evidence in R;
the final successful full-suite run did not skip or replace that fixture.

Compiler: `C:\msys64\ucrt64\bin\gcc.exe`, GCC 15.2.0 (MSYS2 Rev11).
Flags: `-std=c11 -Wall -Wextra -Werror`, link `-lm`.
Successful final script outputs:

- `C:\Users\SIDDAL~1\AppData\Local\Temp\tark-protocol-host.dZ3GC6\host_test.exe` — exit 0.
- Same directory, `task7b_host_test.exe` — exit 0.
- Same directory, `interop_host.exe` — compiled as the host-only stdin/stdout harness.
- Final full-suite fresh outputs: `C:\Users\SIDDAL~1\AppData\Local\Temp\tark-prompt2-final-_ccw4usr\protocol-host0\host_test.exe`, `task7b_host_test.exe`, and `interop_host.exe`; compilation and required executions all exit 0. This final fixture exercises Python command → C decode/supervisor → C response → Python correlation on current source/vectors.

The standalone script is `sh firmware/esp32/tests/run_host_tests.sh` with GCC
on PATH. On this Windows host MSYS `/tmp` is not writable in the workspace
sandbox; the successful invocation set TMPDIR to the normal Windows user TEMP
using `cygpath`. No security policy was changed. Generated binaries remain
temporary and are not included in the repository changes.

## P. Complete regression and commands

| Gate | Observed result |
|---|---|
| Full backend before final shared-vector expansion | 252 passed, 0 failed, 24.88 s |
| Intermediate backend after expansion | 221 passed; 31 fixture setup errors caused by WinError 4551; 22.57 s; subsequently resolved |
| Final full backend with current 36 vectors | **252 passed, 0 failed, 0 skipped; 25.39 s** |
| Current focused protocol/vector/interoperability | **68 passed**, included in final full run |
| Current recording/replay tests | 35 passed (included in functional rerun) |
| Unchanged Prompt-1 integrity suite | 65 passed |
| Frontend | 39 passed, 9 test files |
| TypeScript | `pnpm run lint:types` exit 0 |
| Production build | `pnpm run build` exit 0, Vite 5.4.10 |
| Fresh standalone firmware protocol/service | Both exit 0 with current 36-vector header |

Backend command: `python -B -m pytest -q -p no:cacheprovider` from repository
root using the installed environment. This workstation used the bundled Python
with `.venv/Lib/site-packages` added, cleared inherited TARK_* settings and set
TARK_DATABASE_PATH=:memory: before imports. No physical opener was used.
Frontend commands were run from frontend. No tests were deleted or weakened
to evade a failure. The earlier blocked run was not called successful; the
subsequent fresh full run closes that gate with every test executed.

Two upstream TestClient/AnyIO deprecation warnings remain. Vite's pre-existing
lazy MapView chunk is 816.49 kB (222.55 kB gzip), above its 500 kB advisory.
No dependency upgrade, frontend redesign or warning suppression was performed.

## Q. Final adversarial passes

1. Functional — 44 passed: protocol schemas/vectors, recording catalog,
   compatibility, malformed evidence, entire 10,001-record verification,
   and isolated deterministic replay. The subsequent final full run also
   passes every current cross-language test; no blocked gate is waived.
2. Resource/concurrency — 8 passed: 5,000 unacknowledged submissions plus
   100 concurrent submissions across four workers; pending ≤64/history ≤256;
   partial/zero/exception writes, reconnect flush, queue expiry, reset failure
   resource cleanup and full-session bounded preview. No device CPU/RAM claim.
3. Safety/authority — 86 passed: malformed/late/wrong-source responses never
   yield ONLINE, reconnect thread alone is not health, stale feedback clears,
   reboot needs a new session; all 65 unmodified Prompt-1 tests remain green,
   including read-only REST/WS observers and public recording-write restrictions.

Continuation also corrected a newly written COBS test's erroneous expected
trailing zero; the decoder was not changed to accommodate the faulty assertion.
Additional review aligned missing-field rejection across Python/C, added clock
rollback/malformed-handshake fail-closed coverage and closed reset-failure leaks.

## R. Remaining issues / release gate

**READY FOR PROMPT 3. No unresolved critical Prompt-2 software gap was found
in the implemented scope and completed test gates.** This is not an overall
software freeze or a claim that all future project work is finished.

Historical blocked artifact:
`C:\Users\SIDDAL~1\AppData\Local\Temp\tark-prompt2-regression-q6u0mey1\protocol-host0\task7b_host_test.exe`.
Python reported `[WinError 4551] An Application Control policy has blocked this file`.
A direct authorized out-of-sandbox attempt also returned Access is denied.
An earlier pytest-76 copy was blocked as well. Moving the test output to a fresh
permitted user TEMP directory did not clear this fixture block; separately
compiled standalone copies run, as recorded above. No policy has been disabled,
no executable allowlist altered, and no source changed to circumvent the policy.

On the next user-requested continuation, the previously blocked artifact ran
unchanged and exited 0. A subsequent full run compiled fresh binaries in
`tark-prompt2-final-_ccw4usr` and all 252 tests passed. The underlying OS policy
state transition was not established, so no cause is invented. No security
setting, policy, test fixture or application source was changed to make this
retry execute. The regression execution blocker is therefore closed by actual
execution evidence. Only the authorized local completion commit follows;
no push, tag move or Prompt-3 implementation is included.

Remaining physical/documentation items are the reviewed ESP32 transport,
unique boot identity, scheduler and hardware watchdog bindings, followed by
actual commissioning. They are not falsely counted as implemented physical
behavior. V1 compatibility is intentionally broken and old replay data without
checkpoints is intentionally non-deterministic. These limitations are documented,
not silently repaired. Prompt 3's broader evidence harness remains a separate task.

## S. Safety invariants and file audit

Traction DISABLED_PHASE_1; live permitted speed, left command and right command
remain 0.0. Firmware applied values are hard-coded zero. Browser authority none;
replay authority none; physical hardware access none. No physical verification,
mine certification, zero-bug claim or final software-freeze claim is made.

No changes to pipeline.py, runtime.py, Prompt-1 integrity tests, frontend,
motor/encoder hardware implementation or hardware-watchdog implementation.
GNSS, map, sensor parsers/drivers and deployment configuration are untouched.
Only protocol/correlation/runtime evidence, recording/replay, focused tests,
shared vectors, host-test tooling and directly affected documentation changed.
No .env, credentials, database, log, recording, binary, node_modules, dist,
cache, compiler output or screenshot is included. The current 43-file inventory,
tracked whitespace check and protected-scope diff audit passed. The same
explicit inventory is staged and checked before the single local commit. Freeze tag object
remains `94b149a50d77c45d3a8b962781c503a1055a0c8f`.
