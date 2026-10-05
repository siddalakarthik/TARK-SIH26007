# TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1

**SOFTWARE-EVIDENCE BASELINE / TRACTION DISABLED** — 2026-09-28.
Project TARK, problem SIH26007. Not AS-BUILT, physical validation or certification.

## Exact identity

| Field | Value |
|---|---|
| Software Git commit | `bf87304ab2080452d5446fb4b6bbfcb945cf74ea` |
| Branch | `tark/project-convergence-release` |
| Release commit | Resolve `refs/tags/tark-software-evidence-r1-2026-09-28^{commit}` after the single local release commit |
| Prompt 1 | `8bff0654e2d6db3ff8414c011057274435b6b228` |
| Prompt 2 | `96bf72bbfea88834c173000b271fd016b6b206e9` |
| Prompt 3 | `bf87304ab2080452d5446fb4b6bbfcb945cf74ea` |
| Current protocol | [Protocol V2](ESP32_PROTOCOL_V2.md); legacy frames rejected |
| Configuration | [phase1.json](../config/phase1.json), simulation, identifier UNRELEASED-PHASE1 |
| Config text SHA-256 (CRLF→LF) | `6a887ae7ad0e3099049d68d37b3d27c8ab931b48a5a9cce18378de661e0205c0` |
| Config values fingerprint (runtime mode excluded) | `f6e8471fae3618d38f7892e67f2d41eb37e155d5848bf51195e4dc06b373696e` |
| Evidence schema | 1; TEST_FIXTURE |
| Evidence inventory SHA-256 | `943c342d763f88b5fff999559447f21acb51f4d1498def0be4d7c2da16014b1d` |
| Fingerprint method | Exact bytes of [hashes.json](../evidence/prompt3/hashes.json); not a digital signature |

The [machine manifest](../release/TARK_RELEASE_MANIFEST.json) contains these
fields and [evidence authority](EVIDENCE_AUTHORITY.md) explains the deliberate
non-self-referential release-commit resolver. An absent release tag means the
release has not passed its commit gate. The final handoff gives the literal
resolved commit. No production source/configuration values were changed by R1.

Prompt-3's original manifest truthfully records the pre-commit Prompt-2 HEAD
and dirty worktree at generation. Verified source fingerprints match the
software packaged at bf87304. Its evidence is preserved, not regenerated
to claim it was generated from its own future commit.

## Software gates

| Gate | Result |
|---|---|
| Backend | 322 passed |
| Frontend | 39 passed / 9 files |
| Protocol/interoperability | 68 passed |
| Recording/replay | 35 passed |
| Prompt-1 integrity | 65 passed |
| Prompt-3 harness | 70 passed |
| Shared vectors | 36, Python and C |
| Fresh firmware host | PASS — strict protocol/service plus C/Python fixture |
| TypeScript / production build | PASS / PASS |
| Prompt-3 bundle | PASS — 20 scenarios, 150 repetitions, 85 artifacts |

Subsets are included in 322, not additional independent tests.
See [dated executions and warnings](TEST_REPORT.md).

## Physical and communication boundaries

Traction `DISABLED_PHASE_1`; permitted speed 0.0, left 0.0, right 0.0.
No hardware accessed. Physical validation and commissioning:
**PHYSICAL-VALIDATION-PENDING**. USB/boot identity/scheduling/hardware watchdog
binding remains pending; portable firmware supervision is host-tested.

Electrical: **CONTROLLED DESIGN / PRE HARDWARE COMMISSIONING**; not released
for energization or PCB fabrication. [27 HOLDs](../release/references/electrical/HOLD_REGISTER.md)
remain; none closed here. No mine certification, industrial deployment
readiness, collision guarantee or production autonomy.

[Recorded public demo](https://tark-sih26007-demo.onrender.com) is simulation/
monitoring only. Historical owner/capture evidence is retained; availability,
WSS and deployed revision were not checked here. This local R1 is not pushed
or deployed. PPT: patch sheet only. Film: audit only. Binaries unchanged.

The provisional D_env model, assumed zero vehicle speed, non-integrated TTC,
undefined production WARN policy and separate research EKF/fusion must accompany
presentations. See [claims](TARK_CLAIM_EVIDENCE_MATRIX.md) and
[limitations](KNOWN_LIMITATIONS.md).
