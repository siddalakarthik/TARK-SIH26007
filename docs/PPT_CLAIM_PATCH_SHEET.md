# SIH presentation — controlled claim patch sheet

**PATCH SHEET ONLY — BINARY NOT MODIFIED.**
No PPTX was edited, rendered as a corrected deck or falsely declared corrected.

Read-only OOXML inspection covered all six slides in each locally supplied
variant: TARK_SIH26007_PRE.pptx, TARK_SIH26007_upgraded_deck.pptx and
TARK_SIH26007_Submission_Final.pptx. Exact text and file fingerprints are in
[the retained extraction](../release/references/presentation/SLIDE_TEXT.md).
PRE provides the exact replacement anchors below; variant-specific claims are
also covered. Selection of a submission binary remains a presentation-owner
action, not authority to override the software.

Safe preservation of the original deck's layout/fonts/embedded graphics was
not established with repository tooling. Use this permitted patch-sheet route.
Any later binary correction must render and inspect all six slides before use.
Do not claim this sheet updates text embedded in images.

## Slide 1 — identity and concept

| Current claim | Evidence status | Action | Exact wording |
|---|---|---|---|
| Perception-verified safety assistance for open-cast mine vehicles | Proposed system-level concept, C58 | KEEP | Perception-verified safety assistance for open-cast mine vehicles |
| Multi-sensor perception + risk-aware operating envelope + independent safety control | Concept exceeds current production integration, C10/C19/C38 | MODIFY | Perception-aware envelope concept + tested radar software + independent isolation design |
| Proposed hardware arrangement / conceptual prototype | Correct design maturity, C43/C56 | KEEP | CONCEPTUAL PROTOTYPE — PROPOSED HARDWARE ARRANGEMENT |
| SIH26007, Smart Automation, Hardware, TARK and team ID | Supplied project identity, not a test claim | KEEP | Preserve the supplied identity fields verbatim |

## Slide 2 — proposed solution versus current implementation

| Current claim | Evidence status | Action | Exact replacement |
|---|---|---|---|
| Complementary sensing plus a reliability check before the vehicle is allowed to continue | Concept; no present motion authority, C42 | MODIFY | Perception-aware reasoning demonstrated in software; Phase-1 traction disabled |
| Fuses complementary sensing (radar + thermal + RGB) | Not production fusion, C19 | MODIFY | Radar drives the current decision path; RGB/thermal provide observation interfaces |
| Tracks hazards and relative motion | Slot-based updates, C03/C04 | MODIFY | Tracks radar target slots and reported relative velocity |
| Calculates TTC and stopping requirement | TTC helper not policy, C13/C14 | MODIFY | Parameterized stopping requirement; TTC helper outside current production policy |
| Evaluates Perception-Verified Safe Operating Envelope | Provisional model, C10 | MODIFY | Evaluates the provisional PV-SOE software model |
| NORMAL › WARN › RESTRICT › STOP | Not an implemented ordered sequence, C15 | MODIFY | Current decision states: NORMAL · RESTRICT · STOP · UNKNOWN |
| Available perception is reliable enough for vehicle to safely continue | Concept overstates present calibration | MODIFY | Our concept links perception evidence to permitted operation. This Phase-1 software demonstrates the reasoning while all motion commands remain zero. |
| BNO055 + Encoders: Orientation + ego-motion | Wheel response, not ground speed, C34 | MODIFY | Orientation interface + wheel-response contract |
| Radar/thermal/RGB hardware names and GNSS context-only | Intended parts/design, not physically identified | KEEP WITH QUALIFIER | Intended hardware; exact purchased variants and commissioning remain under HOLD / VERIFY. GNSS is observational context only. |

## Slide 3 — technical approach

| Current claim | Evidence status | Action | Exact replacement |
|---|---|---|---|
| Sensing → Edge Perception → Safety Control → Actuation | Last stage not active, C42 | MODIFY | Sensing interfaces → Pi decision software → Protocol V2 supervision → disabled output boundary |
| Track-level EKF / Fixed vs. adaptive covariance | Separate research study, C20/C21 | MODIFY | Production: radar-slot tracking. Separate study: fixed versus adaptive covariance EKF. |
| TTC / stopping requirement | C11/C14 | MODIFY | Parameterized stopping requirement; TTC NOT COMPUTED in production |
| WARN in state sequence | C15 | MODIFY | NORMAL · RESTRICT · STOP · UNKNOWN |
| Bounded command · heartbeat · timeout · CRC check · watchdog | Software versus board binding distinction, C28–C33 | MODIFY | Protocol V2: sessions · bounded expiry · COBS/CRC32C/CBOR · host-tested supervisor |
| ESP32-S3 bounded control · watchdog | Physical binding incomplete by design | MODIFY | ESP32-S3 software supervisor — board transport/watchdog binding pending |
| 4-wheel vehicle / differential-driver prototype | Intended build, not as-built | MODIFY | Proposed four-wheel differential-drive prototype |
| Physical E-stop → DC contactor → traction isolated | Design only, C38–C41 | MODIFY | Independent E-stop/contactor isolation design — physical verification pending |
| Pi = perception + reasoning / ESP32 = bounded control + watchdog / E-stop = isolation | Design/implementation mixed | MODIFY | Pi: provisional decision software. ESP32: host-tested supervision. E-stop: independent electrical design. |
| Monitoring only / no browser motion authority | Supported, C42/C46 | KEEP | MONITORING ONLY · NO BROWSER MOTION AUTHORITY |
| Submission_Final ALGORITHM CHAIN: adaptive fusion → target state → TTC | Research chain, not production | MODIFY | RESEARCH STUDY ONLY: adaptive covariance → estimated target state → TTC analysis |

Keep the local decision and monitoring lanes separate. Do not add an arrow
from the browser or GNSS to motor authority.

## Slide 4 — maturity, studies and evidence

| Current claim | Evidence status | Action | Exact replacement |
|---|---|---|---|
| Tracking (EKF); Adaptive uncertainty fusion | Not production, C03/C19 | MODIFY | Radar-slot tracking; separate adaptive-covariance research |
| TTC + stopping requirement | C11/C14 | MODIFY | Parameterized stopping requirement; TTC helper not integrated |
| Independent MCU / heartbeat watchdog / E-stop | Software/design versus physical | MODIFY | Host-tested command supervision; independent physical isolation design; board/watchdog/contactor verification pending |
| DIGITAL DEMONSTRATION + VALIDATION | Ambiguous maturity | MODIFY | SOFTWARE EVIDENCE + SEPARATE NUMERICAL STUDIES |
| Simulation 1/2/3 | Archived numerical studies | KEEP WITH QUALIFIER | Separate concept-stage studies: stopping envelope; fixed/adaptive EKF; fault-state logic. Not current production-policy validation. |
| Deployed — public sim/monitoring demo | Historical deployment record; R1 not pushed | MODIFY | Recorded public simulation/monitoring demo — availability and deployed revision not rechecked for R1 |
| Traction DISABLED_PHASE_1 (safe-state) | Zero-output invariant, not physical safe-state guarantee | MODIFY | Traction: DISABLED_PHASE_1 — zero software commands |
| frozen 2d319e7 / 97 backend / 25 frontend | Historical, C59/C60 | MODIFY | TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1. Software bf87304…; 322 backend / 39 frontend software tests; Protocol V2. Exact release identity: release manifest. |
| Test evidence | Current controlled evidence | MODIFY | 20 production-path scenarios · 150 repetitions · deterministic replay · fresh C host interoperability · no physical validation claim |
| LIVE DASHBOARD SCREENSHOT / placeholder | Not proof of a current deployment | REMOVE PLACEHOLDER CLAIM | Genuine captured software demo — retain capture date, revision if known, SIMULATION and traction-disabled labels |
| Submission_Final: adaptive keeps error lower C0–C4 | Archived study explicitly mixed | MODIFY | Synthetic study: adaptive covariance improved position error at C1–C4 and was slightly worse at C0. This is not measured sensor or fog performance. |
| Physical prototype, fog chamber, measured performance future | Supported limitation | KEEP | Physical prototype, fog chamber and measured performance remain future work. |

## Slide 5 — benefits and boundaries

| Current claim | Evidence status | Action | Exact replacement |
|---|---|---|---|
| Improved awareness / complementary perception / risk-aware envelope | Intended benefits, not measured outcomes | KEEP WITH QUALIFIER | Intended benefits of the proposed architecture |
| FAIL-SAFE BOUNDED CONTROL | Physical guarantee implied, C29/C33 | MODIFY | BOUNDED SOFTWARE SUPERVISION + INDEPENDENT ISOLATION DESIGN |
| Permitted operation becomes conservative with inadequate evidence | Concept; current authority always zero | MODIFY | PV-SOE explores evidence-constrained operation; current Phase-1 commands remain zero in every state. |
| Low-cost prototype validates the architecture (Submission_Final) | Physical validation not evidenced | MODIFY | A low-cost prototype is planned for controlled physical evaluation of the architecture. |
| ≤ ₹60,000 / ₹59,522 arithmetic | Historical planning estimate, not purchased BOM/quote | MODIFY | Historical prototype budget estimate; purchased parts, protection ratings and current quotations remain HOLD / VERIFY. |
| No autonomy, mine certification or collision guarantee; operator responsible | Supported boundaries | KEEP | Preserve these exclusions without weakening them. |
| GNSS map context only | Supported | KEEP | GNSS supports context only; it has no collision-control authority. |

## Slide 6 — references and access

| Current claim | Evidence status | Action | Exact replacement |
|---|---|---|---|
| Standards/papers/manufacturer references | Background references, not compliance evidence | KEEP WITH QUALIFIER | Background references; neither standards compliance nor purchased-part verification is claimed. |
| MLX90640-D55/BAB, ESP32 board variant | Variant differences not closed by software | MODIFY | Intended family/model; confirm exact purchased variant against the electrical HOLD register. |
| All links checked/live; GitHub unavailable/private | Historical access claims, not rechecked | MODIFY | References retained from the source deck. Link availability and repository access must be checked separately before submission. |
| Master build/dossier links as final authority | Historical materials | MODIFY | Current controlled release: TARK_RELEASE_INDEX.md. Older dossier/manual are historical and subject to the current claim/HOLD records. |
| Simulation 1/2/3 links | Separate research | KEEP WITH QUALIFIER | Concept-stage numerical studies, separate from the production-path software evidence |
| Public demo link | Recorded URL, not new verification | KEEP WITH QUALIFIER | Public simulation/monitoring demo — not physical vehicle operation; R1 deployment not asserted |
| Deferred high-grade options | Not current scope | KEEP | Future options, not installed or verified components |

The existing Git remote identifies the source repository. This pass neither
changes its visibility nor checks external access. Final binary publication is
a separate task; this audited text is not a certification or slide-layout pass.
