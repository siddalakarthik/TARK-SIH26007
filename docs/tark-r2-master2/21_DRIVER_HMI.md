# 21 — Driver HMI

R2 presentation specification for the existing React/TypeScript/MapLibre application. No frontend code is changed. Driver views are glanceable; engineering detail belongs to the supervisor.

## Hierarchy

Top fixed band: REAL / SIMULATION / REPLAY, vehicle identity, application phase and data age. State/action/reason dominate using text + icon/shape + position + color. NORMAL never becomes “SAFE.” Current applied speed cap remains 0 / DISABLED_PHASE_1 even if a shadow model is displayed.

Primary cards: operating state, qualified supported speed with maturity, current speed with source or unavailable, nearest relevant hazard, distance source, valid TTC or NON_CLOSING/UNKNOWN/INVALID. Distinguish calculated advisory cap from authorized command cap. No last-good value displayed as current after expiry.

Navigation band: current road, destination, next turn, distance to turn with reference/quality, route revision and GNSS quality. Ambiguous matching suppresses the maneuver and shows Position uncertain. Local radar x/y visualization is separate from geographic map; no radar point acquires fake latitude/longitude.

Critical health strip: geometry/position/endpoint availability and loss of essential evidence. Network indicator appears prominently when corrections/cooperation is affected, not merely as decoration. Unavailable location gives a labelled India overview, not a marker at invented coordinates. Browser-device location remains a different observer source and never supplies vehicle state.

## Warning behavior

| Priority | Visual | Audible design | Interaction |
|---|---|---|---|
| STOP | Persistent state/action, no hidden modal | Distinct high-priority bounded pattern, characterized later | Acknowledge records receipt only; no resume |
| UNKNOWN | Evidence insufficient and lost capability | Fault pattern distinct from obstacle warning | Inspect reason; cannot override |
| RESTRICT | Cap and binding reason | Rate-limited attention pattern | No speed-increase control |
| WARN | Hazard/action with valid source/time | Short attention pattern | Acknowledge without clearing evidence |
| NORMAL | Qualified model state, phase/provenance visible | No continuous sound | Monitoring only |

No haptic hardware added. Buzzer failure retains visible warning. Audibility and nuisance rate need actual testing; labels are not evidence an alert was heard. STOP information remains readable without flashing; motion/animations are optional and restrained.

## Responsive and projector acceptance

Test 320, 375, 430, 768, 1024, 1440 and 1920 px widths plus actual 1024×600 panel. At narrow widths stack state/action first, then speed/hazard/navigation; do not compress all cards into tiny text. Map has explicit nonzero minimum height and contained controls. No horizontal overflow, overlap, color-only meaning or stale-as-live media.

Large-text/projector mode changes spacing/typography, not telemetry semantics or authority. Empty/loading/error states say what is missing and retain connection/source status. Keyboard focus, visible labels and screen-reader state announcements must be tested without flooding announcements at telemetry rate. These are planned checks, not performed UI tests.
