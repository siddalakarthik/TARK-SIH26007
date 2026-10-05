# Quality gate — 2026-09-29

## Overall release status

**NOT READY — the required fresh firmware-host execution is blocked by Windows
Application Control (WinError 4551). No final commit or push has been made.**

This is an execution-environment blocker, not a demonstrated production algorithm
regression. Do not relabel it PASS. Do not bypass or weaken the OS security policy.
An authorized administrator must approve execution of the trusted locally built
host-test binaries, or the unchanged test suite must run in an authorized build
environment. Then rerun the full backend gate and independent study verification
before the single authorized study commit.

## Completed checks

- Official sources: current 2026 PS, guidelines and idea template archived and
  hashed; 14 conditions/outcomes extracted; no specific simulation tool mandated.
- Ten numerical studies, declared input registry, 40,000 seeded engineering
  samples, normalized cycle model, independent inverse and percentile checks.
- Study tests include invalid inputs, exact/epsilon boundaries, zero delay,
  extreme positive deceleration, monotonicity, deterministic seed prefixes,
  scenario validation, CSV round trip, deliberate exported-result corruption,
  nonzero failure exit, hash tampering and manifest maturity flags. Exact final
  count is recorded by the runner in results/numerical_verification.json.
- Independent checker recomputes 68,488 exported numeric rows, uncertainty prefix
  stability and eight headline values. These counts are checks, not hardware trials.
- Prompt-3 verification PASS: 85 artifacts, 971,433 bytes, 20 scenarios,
  150 repetitions, observer equivalence MATCH.
- Frontend: 39 tests PASS in 9 files. `pnpm run lint:types` PASS.
  `pnpm run build` PASS (51 transformed modules).
- Existing Vite warning retained: MapLibre chunk 816.49 kB exceeds the 500 kB
  advisory. No production bundling changes were made for this research task.
- Existing two backend dependency deprecation warnings retained.

## Backend / host gate chronology

1. Existing full backend suite, cache disabled, hardware environment overrides
   cleared and in-memory database: **291 passed, 31 setup errors**, 55.54 s.
   GCC could not launch its assembler in the sandbox. All 31 errors originated
   from the same strict C host fixture, not failed application assertions.
2. Approved non-sandbox retry encountered pytest shared-temp ownership conflicts:
   **259 passed, 63 setup errors**, 31.86 s. No test source was changed.
3. Approved retry using a fresh dedicated temporary directory compiled the first
   C host binary successfully, then stopped on its execution:
   **145 passed, 1 setup error**, 37.56 s (`-x`). Exact error:
   `OSError: [WinError 4551] An Application Control policy has blocked this file`.
   Blocked file, relative to the task parent:
   `work/sih-regression-1f41f1e4a2ab4078bc81d696ccac3442/protocol-host0/host_test.exe`.
   The fixture did not reach the second host binary / bidirectional C runner.

The full suite includes protocol, replay and evidence-harness tests. Python-only
paths passed in the first full run; current fresh C interoperability remains
BLOCKED, not verified merely because the historical R1 evidence verifies.

## Reproducibility / visual review

Plots are generated only from exported CSV; source-table fingerprints are stored
in results/figure_inventory.json. PNG and vector SVG are both retained. Reviewed
all figure contact sheets; corrected a clipped sensitivity-axis label, replaced
an interpolated condition-cap line with steps, and separated equal-time fault
events by ordered step so restart/recovery transitions remain visible. Final
full-size inspection confirmed the corrected sensitivity, fault and integrated
figures are readable and not clipped. Two consecutive generations produced 76
byte-identical selected artifacts; fingerprints are in
results/reproduction_check.json. All 33 study tests passed on both generations.

## Unchanged boundaries

Production tracked-file diff remains empty. All additions are confined to the
study directory and eight new study reports. R1 tag remains at its documented
commit. No application, firmware, electrical netlist, dependency lockfile or
safety configuration was edited. No hardware was accessed. Traction remains
DISABLED_PHASE_1. No physical validation or mine certification is claimed.
