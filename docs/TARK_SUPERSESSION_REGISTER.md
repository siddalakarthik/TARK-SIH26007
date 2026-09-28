# Authority and supersession register

Current identity: **TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1**.
Preserve history; do not reinterpret old results as new tests.

| Earlier document/release | Earlier role | Current authority | Why / disposition | Retained? |
|---|---|---|---|---|
| Freeze 2d319e7 / tag tark-software-freeze-2026-09-20 | September 20 software freeze | R1 manifest + bf87304 software | Later adversarial reproduction found defects; no blanket completeness carry-over; old tag unchanged | Yes |
| QA commit 962365e | Scoped public HMI fixes | Source ancestry + dated QA report | Fixes preserved; 97/25 and external-access statements describe that run | Yes |
| Prompt 1, 8bff0654 | Runtime/integrity correction | R1 combined scope + Prompt-1 evidence | Its 162 count/deferred Prompt 2 are historical; corrections remain applicable | Yes |
| Prompt 2, 96bf72bb | Protocol V2 and replay correction | R1 combined scope + current V2 spec | 252 was its full count; Prompt 3 later adds evidence harness | Yes |
| Prompt 3, bf87304 | Deterministic evidence package | R1 manifest references same unchanged source/evidence | Not invalidated; pre-commit manifest provenance retained, no regeneration | Yes, unchanged |
| ESP32_PROTOCOL_V1.md | Filename once held V1, then V2 migration text | ESP32_PROTOCOL_V2.md | Explicit superseded notice; old body preserved, not a second active protocol | Yes |
| Old FINAL/V9/PUBLIC closure reports | Stage completion/deployment narratives | R1 report and TEST_REPORT | Historical banner on each; old “complete/deployment ready” language not reaffirmed | Yes |
| firmware/esp32/TEST_REPORT.md | Early 10-test/V1 host evidence | R1 test record + fresh current C fixture | Old timeout description/count not current V2 semantics | Yes |
| Master dossier V1.0 and old master index | Human project reference at 2d319e7 | PROJECT_STATUS, matrix, release index | See section-specific corrections below | Read-only copies; binaries unchanged |
| Original software architecture package | Intended system design | Current source and V2/replay/runtime docs | TTC/fusion/board scheduling design intent is not implementation proof | External history |
| Earlier one-sheet electrical presentation | Wiring illustration | Corrected five-sheet set and H01–H27 | C01/C02 canonical names, C03 Pi Pin-1 correction, return and physical-pin HOLDs | Preserved externally |
| LEGO manual V2 / earlier V8 wiring prose | Build sequence | Five-sheet/HOLD authority for wiring | Any Pin-1 power allocation or unresolved coil/supply instruction is superseded; no energization release | Preserved externally |
| PRE / upgraded / Submission_Final PPTX | SIH communication | PPT_CLAIM_PATCH_SHEET + matrix | Old EKF/fusion/TTC/watchdog/maturity/count claims need exact text patches | Binary unchanged |
| Final 4:40 film production book | Director plan/predecessor timings | Latest Liam captions/QA for output identity; FILM_CLAIM_AUDIT for claims | Different voice/timing; old UI “N/A”/baseline no longer current | Yes |
| Liam synchronized film | Historical software demonstration | Film audit + current R1 matrix | Slot tracking/envelope/TTC/deployed-version qualifiers required; no re-render | Binary unchanged |
| Numerical studies 1/2/3 | Concept-stage research | Their own declared synthetic scope only | Not current production fusion, WARN, fog or physical E-stop evidence | External archives fingerprinted |

## Dossier section corrections (binary not edited)

| Section | Superseded claim | Current controlled statement |
|---|---|---|
| Cover/source authority/10/23/24/40/42/49/55/57 | Old freeze, V1, 97/25 counts, old index | Use R1 manifest, V2 and dated R1 tests; source is bf87304 |
| 3/4/24/28/31/35 | End-to-end TTC/WARN presented as implemented | TTC helper not production policy; NOT COMPUTED in HMI; WARN vocabulary only |
| 8 | 50/70/100 maturity percentages | Use subsystem maturity and explicit gates, not a completion percentage |
| 16/17 | F3 fed by N-LOGIC12+; PS1 input-return labels | Controlled F1 common N-PROTECTED12+, F2 N-LOGIC12+, F3 N-ESTOP-FUSED+; PS1-IN-RETURN-HOLD remains open |
| 26 | Stable track identifiers imply object identity | Receiver target-slot key only, not persistent physical identity/EKF |
| 37 | NORMAL/WARN/RESTRICT/UNKNOWN/STOP scenario names | Descriptive input scenarios; state aliases rejected by Prompt 1 |
| 38 | Broad handling/lifecycle assurance | Tested cases only; no universal concurrency/field guarantee |
| 46/47/52 | Build sequence before detailed purchased-part closure | H01–H27 and next-phase authorization govern; no energized build released |

## Current-facing corrections

README, protocol references, UI/run/simulation/limits/fault guidance, public-demo
status and test landing page now point to R1. The .env.example radar note is a
comment-only clarification of the existing decoder; every configuration value
is unchanged. Old source registers/raw reference paths are historical provenance,
not developer-local dependencies of current navigation.

No archival evidence or tag was deleted. Supersession changes authority, not
the historical fact that a report or test existed.
