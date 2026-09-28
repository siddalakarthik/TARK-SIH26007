# TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1

Release date: 2026-09-28. Software-only, traction disabled.
This report controls claims, not physical energization.

## 1. Release identity

Software commit `bf87304ab2080452d5446fb4b6bbfcb945cf74ea`.
Branch `tark/project-convergence-release`. The single release commit is
resolved by `tark-software-evidence-r1-2026-09-28^{commit}`; absent tag means
not released. [Manifest](TARK_RELEASE_MANIFEST.md) contains all identifiers
and fingerprints. The old freeze tag remains unchanged.

## 2. Scope

Documentation, claim reconciliation, release-control metadata and read-only
reference copies only. No source behavior, frontend strings, firmware behavior,
electrical topology, configuration values, dependencies or deployment changed.
The radar comment in .env.example is documentation only.

## 3. Architecture

Sensors → Pi normalized radar/health/freshness → slot tracking → provisional
PV-SOE/stopping → bounded zero command → Protocol V2 supervision.
Separate REST/WebSocket monitoring, GNSS/map observations and isolated replay.
The browser, replay and evidence harness acquire no actuation authority.

## 4. Implemented software

Radar target-report decoding, configured adapter lifecycles, observation/health
contracts, runtime owner, state/command software, host/C protocol supervision,
SQLite events, format-2 recording/replay and shared HMI exist. The
[60-claim matrix](TARK_CLAIM_EVIDENCE_MATRIX.md) gives exact source/test paths.
Software scope is not physical readiness.

## 5. Prompt-1 corrections

At `8bff0654e2d6db3ff8414c011057274435b6b228`: nine reproduced integrity
issues corrected, including stale/future evidence, observer-driven execution,
numeric configuration, speed/TTC wording, scenario aliases, stale HMI/map
state and public recording mutation. [Dated evidence](SOFTWARE_INTEGRITY_CORRECTION_REPORT.md)
is preserved; 65 integrity tests remain in the current suite.

## 6. Prompt-2 protocol/replay corrections

At `96bf72bbfea88834c173000b271fd016b6b206e9`: fourteen reproduced defects
corrected. Explicit approved V2 sessions, bounded receiver-local TTL, canonical
CBOR compatibility, strict response/deadline validation, bounded correlation,
transport generation flushing and periodic supervision. Recording checkpoints,
ordered batches/empty reports, compatibility and full-session verification
replace the earlier replay gaps. [Correction evidence](PROTOCOL_FIRMWARE_REPLAY_CORRECTION_REPORT.md).

## 7. Prompt-3 deterministic evidence

20 scenarios, 150 repetitions, 70 harness tests and 85 exported artifacts.
Coverage includes stale/future reports, valid-empty/missing, communication loss,
late ACK, session restart, reconnect, observer independence, recording/replay
and zero commands. Ten negative controls challenge digests/replay, identity,
source boundaries, expected results and storage/runtime failure.
[Original report](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md) and
[bundle](../evidence/prompt3/README.md) remain unchanged.

The bundle retains truthful pre-commit provenance; source fingerprints match
bf87304. Prompt 4 verifies rather than regenerates it.

## 8. Current protocol

[ESP32_PROTOCOL_V2.md](ESP32_PROTOCOL_V2.md) is the sole current specification.
The old V1 filename retains a historical migration snapshot with an explicit
superseded banner. Shared vectors and current Python/C implementations are
unchanged. ACK is software acceptance, not physical operation; REAL source
is endpoint semantics, not physical verification.

## 9. Current dashboard/demo

Current strings: measured speed UNAVAILABLE, TTC NOT COMPUTED,
DISABLED_PHASE_1, MONITORING ONLY and PARAMETERIZED / NOT VALIDATED.
Disconnect clears current-looking telemetry; missing/stale fixes remove current
map evidence. No source strings needed editing. The
[UI guide](UI_GUIDE.md) now explains those terms.

Recorded public URL is simulation/monitoring only. No network check,
deployment, push or current-public-commit claim occurred. Existing film stills
are historical captures, not a new R1 public demonstration.

## 10. Research/simulation work

External numerical studies 1/2/3 explore stopping envelopes, adaptive covariance
and fault-state logic. Fingerprinted source inventory separates them from
production. Adaptive study results are mixed/condition-dependent under
synthetic quality signals; no production EKF/fusion or measured fog claim follows.

## 11. Electrical/hardware status

Read-only reference subset preserves the corrected five-sheet design,
canonical connectivity, source resolutions and all 27 HOLD/restriction entries.
Status: CONTROLLED DESIGN / PRE HARDWARE COMMISSIONING. Native CAD ERC NOT RUN.
Document/export audits are not electrical tests. No energization or fabrication
release. H01/H02/H27 permanent restrictions are not assignments to be “completed.”

ESP32 physical RX/TX, fresh boot identity, scheduling/disconnect and hardware
watchdog binding remain pending reviewed board integration. No hardware accessed.

## 12. Known limitations

Nearest-track D_env is not calibrated free-space observability. Decision speed
is assumed zero. TTC helper does not drive policy; WARN lacks executable
semantics; AGING can retain NORMAL. Empty observations can retain prior tracks.
Communication failure is not a newly added PV-SOE transition.
Sensor interfaces/identity review, GNSS aggregation and bounded persistence
are not field-validation claims. See [limits](KNOWN_LIMITATIONS.md).

No no-bugs, certification, physical braking, fog, safe-speed, collision-prevention
or production-autonomy guarantee is permitted.

## 13. Physical next phase

[Thirteen gates](PHYSICAL_VALIDATION_NEXT_PHASE.md) cover purchased parts,
electrical HOLDs, sensors, board binding, watchdog, E-stop/isolation, separately
authorized vehicle commissioning, encoders, braking, stopping, fog, calibrated
perception and physical PV-SOE. No such work is performed here.

## 14. Test/evidence summary

Current gates: backend 322; frontend 39/9 files; protocol/interoperability 68;
replay 35; Prompt-1 integrity 65; harness 70; shared vectors 36. Fresh strict
GCC protocol/service and Python/C interop pass. TypeScript/build pass.
Subsets are included in 322. See [execution record](TEST_REPORT.md).
Existing two upstream Python deprecations and lazy MapView chunk advisory are
not suppressed; no claim of zero bugs or measured embedded performance.

## 15. Release artifacts

[Release index](TARK_RELEASE_INDEX.md) links manifests, claims, status,
maturity, authority, supersession, V2, evidence, tests, reference copies,
physical handoff, site copy, judge Q&A and checklist. No MP4/PPTX/PDF was edited;
PDF/DOCX reference copies are unchanged source artifacts.

PPT: PATCH SHEET ONLY — BINARY NOT MODIFIED.
Film: CLAIM AUDIT COMPLETE — BINARY NOT MODIFIED.

## 16. Authority/supersession

Manifest controls identity; source controls behavior; evidence controls
demonstrated scope; V2 controls communication; electrical design and purchased
datasheets control intended physical work within HOLDs. Dossier/presentations
cannot override them. Nineteen older stage reports/freeze records carry visible
historical notices; Prompt-1/2 reports retain scoped-evidence notices.
The [register](TARK_SUPERSESSION_REGISTER.md) enumerates external binary/prose
corrections rather than silently rewriting history.

## 17. Exact claims permitted

“Production-path stale-data handling is covered by deterministic software scenarios.”
“Observer count did not alter the normalized logical trace in EV-16/17/18.”
“Protocol V2 uses explicit sessions and bounded receiver-local expiry.”
“Defined compatible software sessions replayed deterministically.”
“Observed Phase-1 live commands remained zero throughout the controlled suite.”

## 18. Exact claims not permitted

“Physically validated mine vehicle.” “Measured stopping/fog performance.”
“Physical E-stop/watchdog verified.” “Production EKF fusion.” “TTC-driven
production collision control.” “Mine-ready/certified.” “Guaranteed collision
prevention.” “The public deployment runs this local R1.” “Zero bugs.”

## 19. Reproduction instructions

[Evidence authority](EVIDENCE_AUTHORITY.md) describes environment isolation.
From installed project environment, no hardware configuration:

```text
python scripts/run_evidence_harness.py --verify evidence/prompt3
python -B -m pytest -q -p no:cacheprovider --tb=short
```

From frontend: `pnpm test`, `pnpm run lint:types`, `pnpm run build`.
Protocol tests compile and execute fresh strict C host binaries.
The bundle must not be overwritten. Future production changes require renewed evidence.

## 20. Final release gate

Software-evidence scope is eligible for the single local commit after final
reference/claim/file-scope and regression gates. The
[checklist](../release/RELEASE_CHECKLIST.md) records those gates.
The annotated tag is created only after that commit; neither is pushed.
Hardware/physical validation and presentation binary patches remain outside
the completed software-evidence scope. A missing/failed required gate prohibits
the commit/tag; do not infer release merely because this report exists.
