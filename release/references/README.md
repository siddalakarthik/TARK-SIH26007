# Controlled reference inventory and applicability

These are read-only reference copies or extractions, not new engineering
releases. Original binaries remain unchanged. Portable content fingerprints
are recorded in [REFERENCE_HASHES.json](REFERENCE_HASHES.json).
Copied text hashes normalize CRLF→LF for Git checkout portability; original
raw hashes are retained separately. PDFs/DOCX use exact bytes.

## Electrical — current intended design, within HOLDs

Source package identifier: `TARK_SIH26007_ELECTRICAL_REV1_0`, corrected
five-sheet set, revision 1.0, dated 2026-09-21. This selected reference subset
does not purport to redistribute its entire editable/generation package.

- [Five-sheet PDF](electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf)
- [Canonical connectivity](electrical/TARK_SIH26007_CANONICAL_CONNECTIVITY.json)
- [HOLD register](electrical/HOLD_REGISTER.md) / [node table](electrical/NODE_TABLE.md)
- [Source resolutions](electrical/SOURCE_REGISTER.md)
- [Project ERC report](electrical/TARK_SIH26007_PROJECT_ERC_REPORT.md)
- [Independent saved-export audit](electrical/TARK_SIH26007_INDEPENDENT_EXPORT_AUDIT.md)
- [PCB logical interface definition](electrical/TARK_SIH26007_PCB_INTERFACE_DESIGN_DEFINITION.md)

Status: CONTROLLED DESIGN / PRE HARDWARE COMMISSIONING.
NOT RELEASED FOR ENERGIZATION OR PCB FABRICATION. Native CAD ERC: NOT RUN.
Recorded checks: 21 project checks, 70 independent export checks, 49/49 expanded
paths, 20 required traces. These are document/connectivity checks, not measured
electrical tests. 27 HOLD items remain.

C01/C02 preserve the user-approved topology and names:
F1/common output `N-PROTECTED12+`; F2 output `N-LOGIC12+`;
K1 main output only `N-TRACTION12+`; F3 output `N-ESTOP-FUSED+`;
coil `K1-COIL+`/`K1-COIL-`. PS1 IN− remains isolated
`PS1-IN-RETURN-HOLD`, source open; OUT− is intended `N-LOGIC-GND`
with physical terminal identity HOLD. No topology changed.

The source register's software reference to the old freeze/Protocol V1 is
historical context, not current software authority. The new
[Protocol V2](../../docs/ESP32_PROTOCOL_V2.md) governs software only.
Exact purchased component datasheets have not closed these HOLDs.

## Dossier/manual/architecture — historical explanatory sources

[Master dossier V1.0 DOCX](dossier/TARK_SIH26007_MASTER_PROJECT_DOSSIER_V1_0.docx),
[PDF](dossier/TARK_SIH26007_MASTER_PROJECT_DOSSIER_V1_0.pdf) and
[old index](dossier/TARK_SIH26007_MASTER_PROJECT_INDEX.md) are preserved.
Their old freeze, Protocol V1, TTC/tracking/scenario and electrical-reference
claims are superseded as enumerated in the
[supersession register](../../docs/TARK_SUPERSESSION_REGISTER.md).
Do not use old binary content alone as current implementation or wiring authority.

The supplied LEGO manual V2 and original twenty-document software-architecture
package remain external historical design sources, not copied/reissued here.
The inspected architecture chain includes aspirational TTC/fusion/physical
transport work; current source and the R1 matrix control implemented scope.
The earlier manual's Pi Pin-1 sensor-power instruction is explicitly superseded
by electrical source resolution C03: Pin 1 has NO EXTERNAL POWER.

## Presentation — historical source text, not an edited deck

[Slide text and exact PPTX fingerprints](presentation/SLIDE_TEXT.md) cover
the three supplied six-slide variants. The
[PPT patch sheet](../../docs/PPT_CLAIM_PATCH_SHEET.md) provides factual corrections.
No newest-file assumption gives any deck engineering authority.

## Film — historical communication record

[Liam captions](film/TARK_SIH26007_LIAM_SYNCED.srt) and
[QA metadata](film/SYNC_QA.json) identify the later synchronized output.
[Original final narration](film/FINAL_NARRATION.txt),
[technical scope](film/TECHNICAL_SCOPE.md), [production plan](film/production.json)
and [original timing cues](film/visual_cues.json) explain its predecessor.
Original 4:40 timings are not the later Liam export's 227.32 s timeline.

No film/audio binary is copied, edited or newly certified by this release.
Historical metadata can retain old file paths; current navigation does not
depend on those paths. [Film claim audit](../../docs/FILM_CLAIM_AUDIT.md)
controls proposed corrections, not the unchanged binary.

## Separate numerical research studies

The following supplied archives were inspected in place, not installed/run or
imported into the production application. They remain external source
artifacts identified by exact fingerprint; no new numerical results are claimed.

| Source archive | SHA-256 | Observed scope |
|---|---|---|
| TARK_PV_SOE_SIMULATION_1_FINAL_VERIFIED.zip | `24c5c0b1d4f761e87883c13eb5fac6c20ce6e727c87245f56e6ac3228aa8b15b` | Parameter sweeps for stopping/envelope concept; all inputs are assumptions |
| TARK_SIH26007_SIMULATION_2_FINAL_VERIFIED.zip | `426e6c62064d40147259386a1db9b883705eaebee1ee513c8f98229a38e26905` | EKF fixed/adaptive covariance; synthetic exogenous quality; archived verification/results |
| simulation3_safety.zip | `a4be2002e1ff39b80dfef5a78da5ba154e7b586125e27de2765e05290c15a4f2` | Numerical fault/state simulation with assumed timing, not physical safe-stop validation |

Simulation 2 contains `ekf_simulation.py` with EKF and adaptive_R,
README/REPORT/VERIFICATION_REPORT and archived CSV/JSON outputs.
Its supplied interpretation is MIXED / CONDITION-DEPENDENT: adaptive position
error is better at C1–C4 and slightly worse at C0. Quality signals are synthetic,
not inferred from actual sensors. The retained [study excerpt](research/SIMULATION2_VERIFICATION.md)
is an archived report, not a new R1 execution. Simulation 1/3 WARN or fault-state
policies do not define current production policy. Research supports the
concept; Prompt-3 evidence supports the actual software path.
