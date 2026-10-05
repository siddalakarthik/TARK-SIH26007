# Test Report

## Current R1 software-evidence gate — 2026-09-28

Current software commit: `bf87304ab2080452d5446fb4b6bbfcb945cf74ea`.
Prompt 4 is documentation/release control only. Earlier result sections below
are HISTORICAL BASELINE records, not present counts or blanket completion claims.

| Gate | Current result |
|---|---|
| Prompt-3 artifact verification | PASS; 20 scenarios, 150 repetitions, 85 artifacts, 971433 inventoried bytes |
| Full backend | 322 passed, no failed/skipped tests |
| Protocol/interoperability | 68 passed, included in full suite |
| Recording/replay | 35 passed, included in full suite |
| Prompt-1 integrity | 65 passed, included in full suite |
| Prompt-3 harness | 70 passed, included in full suite |
| Shared protocol vectors | 36 consumed by Python and fresh C fixture |
| Strict C protocol/service/supervisor | PASS; freshly compiled and executed via test_protocol_correctness.py::host |
| C/Python bidirectional interoperability | PASS in that same fresh fixture |
| Frontend | 39 passed, 9 files |
| TypeScript | PASS |
| Production build | PASS; existing 816.49 kB lazy MapView advisory |

Execution used bundled Python 3.12.14 plus the existing project site-packages,
with inherited TARK_* variables cleared and TARK_DATABASE_PATH=:memory: before
app import. No packages were installed. Commands were the evidence verifier,
`pytest -q -p no:cacheprovider --tb=short`, `pnpm test`,
`pnpm run lint:types`, `pnpm run build`. Fresh C compilation uses GCC 15.2.0
with `-std=c11 -Wall -Wextra -Werror`, then runs protocol/service binaries and
stdin/stdout interop. No OS security policy was changed.

Initial convergence run on September 27: backend 52.40 s; frontend 5.90 s;
Vite build 4.61 s. Final September 28 recheck: backend 322 passed in 70.90 s;
frontend 39 passed in 6.57 s; TypeScript PASS; Vite build PASS in 5.63 s.
Prompt-3 verification again PASS before that full rerun. Two upstream TestClient/AnyIO
deprecation warnings persist; no test weakening or dependency upgrade.
Prior separate shell-helper WinError 4551 is retained in Prompt-3 history and
is not called a pass; the canonical fresh pytest host fixture passes.

All tests are software-only. No COM/USB/I2C/camera/vehicle/E-stop test occurred.
See [manifest](TARK_RELEASE_MANIFEST.md) and [scope](EVIDENCE_AUTHORITY.md).

## Historical stage records (retained below)

## Prompt-2 protocol/firmware/replay correction — 2026-09-27

Current details: [correction report](PROTOCOL_FIRMWARE_REPLAY_CORRECTION_REPORT.md).
The older results below are dated historical evidence, not current gate status.

- Final backend regression: **252 passed, 0 failed, 0 skipped**, 25.39 s,
  including the current 36 shared vectors and fresh C interoperability fixture.
  An intermediate run had 221 passes and 31 setup errors due to Windows
  Application Control (WinError 4551). The same previously blocked artifact
  subsequently ran unchanged, followed by the fully passing fresh rebuild/run.
- Fresh standalone GCC 15.2.0 protocol and service/supervisor tests both run
  successfully with the current 36 shared vectors; the final cross-language
  pytest gate also passes. Strict `-std=c11 -Wall -Wextra -Werror`
  compilation remains required; no security policy or test assertion was weakened.
- Current functional rerun: 44 passed; resource/concurrency: 8 passed;
  safety/authority: 86 passed. Replay coverage: 35 tests. All 65 Prompt-1
  integrity tests remain unchanged and passing.
- Frontend: 39 passed; TypeScript and production build pass. Existing MapView
  chunk-size advisory and two upstream Python deprecation warnings remain.
- No hardware accessed. All Prompt-2 gates pass for the single authorized local
  completion commit. No push or freeze-tag change; Prompt 3 remains separate.

Last final-master audit run: 2026-09-15.

## Software and communication closure update — 2026-09-20

- Backend regression: **97 passed**. This includes documented LD2450 binary
  decoding, physical-vs-simulation source gating, decoder recovery, encoder
  count-contract and existing API/WebSocket/protocol/replay coverage.
- Frontend regression: **23 passed**; TypeScript check and Vite production
  build passed using the already-installed local tools. The MapView bundle-size
  advisory remains non-blocking.
- Firmware: strict GCC `-std=c11 -Wall -Wextra -Werror -fsyntax-only` passed
  for the protocol, response, service, supervisor and safe hardware-boundary
  sources. Fresh host executables compiled successfully, but this workstation's
  application-control policy prevented execution; no pass claim is made for
  those newly compiled executables.

| Check | Result | Status |
|---|---|---|
| Backend configuration, safety pipeline, API, WebSocket, map safety and deployment tests | 30 passed | VERIFIED |
| Frontend contract, map/device-location/camera readiness and HMI interaction tests | 17 passed | VERIFIED |
| Frontend production build | Vite build passed | VERIFIED |
| ESP32 C source compilation, protocol supervisor and safe hardware-boundary tests | GCC `-Wall -Wextra -Werror -fsyntax-only` passed | VERIFIED |
| ESP32 host executable behavior | CRC-32C, sequence/expiry/heartbeat, safe MDD10A zero-output, simulated encoder freshness and watchdog-boundary checks passed | VERIFIED |
| Local HMI same-origin telemetry | Browser loaded and connected at `http://localhost:8000` | VERIFIED |
| Two-tab local HMI | Two tabs independently connected; traction stayed disabled | VERIFIED |
| Responsive HMI | 320–1920 px CSS viewport checks; no document overflow after mobile event-row fix | VERIFIED |
| Browser console | No error/warning messages observed in local HMI | VERIFIED |
| Static production-source transport audit | No hard-coded production localhost/URL-token transport dependency | VERIFIED |
| Frontend bundle credential audit | No `TARK_ACCESS_TOKEN` or test token in compiled frontend assets | VERIFIED |
| Docker build/runtime | Docker CLI not installed on this workstation | NOT VERIFIED |
| Render Blueprint static validation | Docker runtime, `plan: free`, `/ready`, public-demo profile | VERIFIED |
| Render/public HTTPS/WSS | No hosting account/hostname available | NOT VERIFIED |
| Physical mobile/external network | No external device/network test available | NOT VERIFIED |

The final-polish backend run completed with **30 passed** and three non-failing warnings: two upstream TestClient deprecation warnings and one sandbox-denied pytest-cache write. The frontend completed with **17 passed** and a production build. They are not TARK test failures. The MapLibre lazy-loaded bundle remains approximately 808 kB before gzip; it is loaded only when the Map view opens. This is documented as a non-blocking performance observation, not a Raspberry Pi measurement. OpenFreeMap Liberty India-overview checks passed at 320, 360, 390, 412, 768, 1024, 1280, 1440 and 1920 px with no document-level horizontal overflow. No geographic vehicle data is fabricated and radar remains in a separate local-coordinate scope.

Simulation-only truth remains intact: no test run validates real LD2450 serial communication, ESP32 USB operation, physical actuator response, encoder response, motor operation, physical E-stop, timing, stopping distance, or mine safety behavior.
