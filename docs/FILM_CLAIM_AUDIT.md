# Engineering film — claim audit

**CLAIM AUDIT COMPLETE — BINARY NOT MODIFIED.**
No MP4, voice, audio, captions or storyboard original was edited or regenerated.
No voice service or public deployment was contacted.

## Reviewed sources and scope

The latest recorded user-requested output is the Liam-synchronized film,
`TARK_SIH26007_LIAM_SYNCED.mp4`: metadata reports 227.32 s, 1920×1080,
25 fps and 70 captions. Its supplied QA records a full decode pass, not a new
Prompt-4 decode or physical test. Recorded MP4 SHA-256:
`a4a6eb1fbf16fcf6b00848e05b68f180bc6f6f770522499fb1a18a8ec8f5cffe`.

Read the [Liam captions](../release/references/film/TARK_SIH26007_LIAM_SYNCED.srt),
[QA record](../release/references/film/SYNC_QA.json),
[narration](../release/references/film/FINAL_NARRATION.txt),
[technical scope](../release/references/film/TECHNICAL_SCOPE.md),
[production description](../release/references/film/production.json) and
[visual cues](../release/references/film/visual_cues.json).
The predecessor production book was also inspected: ten scenes, originally
4:40 with a different voice. Its old cue times/voice metrics are not Liam export
metadata. The original narration and Liam captions tell the same technical story.

## Statement classification

Caption ranges identify complete statements, not partial sentence fragments.
Context/title lines are included so the coverage is explicit.

| Captions | Technical statement / scope | Classification | Evidence and disposition |
|---|---|---|---|
| 1–6 | Fog/uncertainty motivates the project | SUPPORTED | Problem framing, not a measured TARK trial; retain |
| 7–9 | TARK asks how to make an informed decision | SUPPORTED | Concept statement; retain |
| 10–11 | Sensing interfaces, reasoning, bounded control, monitoring integrated | SUPPORTED WITH QUALIFIER | Software integration, not physical actuation; existing next sentence supplies scope |
| 12–13 | Conceptual hardware/software demo, no completed mine test | SUPPORTED | Retain explicit visual boundary |
| 14–18 | Radar/camera/thermal/IMU complementary roles | SUPPORTED WITH QUALIFIER | Intended device/interface roles; not live sample claims; retain concept labels |
| 19 | Encoders report wheel response, not ground speed | SUPPORTED WITH QUALIFIER | Software contract, physical pulses pending; retain |
| 20–21 | Radar decision path; other observations/health separate | SUPPORTED | Current pipeline/system source; retain |
| 22–23 | Pi asks health/freshness before use | SUPPORTED | Prompt-1 corrections and EV-03/04/05; no mounted Pi claim |
| 24–25 | Follow targets rather than every detection being new | OVERSTATED | Slot-based retention does not establish persistent physical target identity; replace A |
| 26 | Uncertainty travels with track | SUPPORTED WITH QUALIFIER | Stored resolution-derived uncertainty, not a covariance estimator; replace B |
| 27–28 | Old observation must not masquerade as current evidence | SUPPORTED | Prompt-1/3 stale publication tests; retain |
| 29–30 | Seeing versus stopping; TTC concept | SUPPORTED | Concept/helper only, not policy integration; retain |
| 31 | Demo TTC value unavailable | OUTDATED | Current exact label is NOT COMPUTED; replace C |
| 32–33 | Stopping = reaction + braking + margin | SUPPORTED WITH QUALIFIER | Parameterized formula; current speed assumption zero; replace D |
| 34–35 | Compare observable distance and stopping requirement | OVERSTATED | Nearest-target D_env is not calibrated observable free space; replace E |
| 36–38 | PV-SOE concept: weaker evidence constrains operation | SUPPORTED WITH QUALIFIER | Concept, not calibrated dynamic authority; replace F for current scope |
| 39 | NORMAL/RESTRICT/STOP/UNKNOWN visible | SUPPORTED WITH QUALIFIER | No ordered transition sequence; NORMAL not certification; retain |
| 40–41 | UNKNOWN means insufficient trustworthy information | SUPPORTED | Modeled state under existing policy; retain |
| 42 | Missing sensor/stale message must not increase permission | SUPPORTED WITH QUALIFIER | Principle and zero-output invariant, not all-sensor fault-to-STOP policy; retain with F |
| 43–44 | Pi reasoning / ESP32 software checks bounded commands | SUPPORTED | V2 host/C interoperability; no hardware claim in wording; retain |
| 45–47 | Independent E-stop through contactor in electrical design | SUPPORTED WITH QUALIFIER | Design only, H11–H15 unresolved; existing word “design” must remain |
| 48–51 | Dashboard never controls vehicle; traction disabled | SUPPORTED | Tested authority and zero outputs; retain |
| 52–53 | GNSS/intended LC29H supplies map context | SUPPORTED WITH QUALIFIER | Existing “intended” qualifier; no actual fix, RTK or accuracy claim |
| 54–55 | Local radar targets separate from geography | SUPPORTED | Map/source contract; retain |
| 56–57 | No vehicle fix → labelled India overview | SUPPORTED | Current map fallback; retain |
| 58–60 | Actual public software demo with simulation labels | SUPPORTED WITH QUALIFIER | Historical genuine captures, not current R1 deployment; replace G |
| 61 | State/health/communication/map/log/replay inspection | SUPPORTED | Implemented HMI; retain |
| 62 | Missing sensors labelled | SUPPORTED | HMI availability contracts; retain |
| 63–64 | Trace why a decision happened | SUPPORTED WITH QUALIFIER | Defined software evidence, not signed exhaustive forensic record; retain |
| 65–67 | One integrated testable software system | SUPPORTED | Current code and tests; retain |
| 68–70 | Trust verifiable evidence / title | SUPPORTED | Engineering principle, not guarantee; retain |

No affirmative physical-validation statement was found in the reviewed spoken
script. The classification PHYSICAL CLAIM NOT EVIDENCED is therefore not needed
for a quoted narration row; conceptual imagery must remain visibly conceptual.

## Exact replacement narration — only changed lines

A — captions 24–25: “We retain radar observations by the receiver's target slots
over time. Those slots are not guaranteed identities of physical objects.”

B — caption 26: “Each track carries the reported resolution-derived uncertainty,
without a production fusion filter.”

C — caption 31: “The current dashboard marks TTC as NOT COMPUTED because it
does not yet drive the production decision policy.”

D — captions 32–33: “The parameterized stopping calculation adds reaction
distance, braking distance and margin. Today's decision model assumes zero
vehicle speed; these are not measured braking results.”

E — captions 34–35: “Today's provisional envelope compares nearest active radar
range, reduced by stored uncertainty, with that stopping requirement.”

F — captions 36–38: “PV-SOE is our perception-aware operating-envelope concept.
The current simplified software model demonstrates that reasoning, while every
Phase-1 motion command remains zero.”

G — captions 58–60: “These are genuine captures of our earlier public software
demonstration, with simulation labels visible. The current local software
release is backed by deterministic production-path evidence.”

No other narration replacement is required. In a later authorized production,
the closing evidence statement may be strengthened, but it is not falsely
marked revised here. Timing must be rechecked after any later voice revision.

## Storyboard / metadata alignment

| Source element | Result and required future correction |
|---|---|
| Scenes 1–3 physical artwork | Keep CONCEPTUAL / SOFTWARE DEMONSTRATOR and radar-versus-observation lanes; no measured ranges/temperatures/pulses |
| Scene 4 “Track the target” | Use “Track radar slots”; retain illustrative, non-probabilistic uncertainty styling |
| Scene 5 old “N/A”/observable bar | Future render must say NOT COMPUTED and PROVISIONAL ENVELOPE; do not relabel old UI stills as newly captured |
| Scene 6 state highlights | Four implemented states, zero-output strip; no executable WARN sequence or calibrated shrinking-envelope claim |
| Scene 7 software/physical/HMI lanes | Current communication label Protocol V2; USB/boot identity/watchdog binding pending; no physical contactor operation animation as evidence |
| Scene 8 geography | Keep intended GNSS and local radar separation, no fabricated fix or satellite-lock claim |
| Scene 9 genuine UI stills | Dated historical captures; R1 has not been deployed in this pass |
| Scene 10 baseline | Reference R1 evidence rather than the superseded broad freeze; no physical verification checkmark |
| Predecessor 4:40 production book / cue times | Historical predecessor only; Liam captions/QA define the later 227.32 s output |
| technical scope “TTC N/A” | Historical UI wording superseded by Prompt-1 NOT COMPUTED; original preserved |

The film remains a historical communication artifact accompanied by this audit.
Its binary is not declared updated or compliant with the replacement wording.
