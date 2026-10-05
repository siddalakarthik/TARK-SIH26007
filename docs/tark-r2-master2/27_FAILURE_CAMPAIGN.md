# 27 — Failure campaign

DESIGN TEST MATRIX — no injected or physical tests executed here. For every case use original source/record IDs and observe both driver and control-room projections. The control room displays the same cause, lost capability, source age and affected vehicle; it must never replace stale state with current NORMAL. All current commands remain zero.

| ID / injected fault | Expected detection | Lost capability | Remaining capability | Expected state | Driver message | Log evidence |
|---|---|---|---|---|---|---|
| F01 radar disconnected | Owner disconnect/absent data | Forward geometry | Other observations/monitoring | UNKNOWN | Forward geometry unavailable | USB/disconnect, last sample, capability change |
| F02 radar stale | Age exceeds policy | Fresh geometry | Retained last-known hazard only | UNKNOWN | Radar evidence stale | Source/receive/evaluation times |
| F03 RGB disconnected | Acquisition failure | Visual semantics | Qualified radar/thermal if independently valid | WARN or UNKNOWN if required coverage lost | Visual channel unavailable | Camera state/coverage dependency |
| F04 RGB frozen | Timestamp/sequence stall; content check secondary | New visual evidence | Other qualified sensors | WARN or UNKNOWN | Camera frame stale | Sequence/age/freeze reason |
| F05 thermal disconnected | USB failure | Thermal support | Other qualified channels | WARN or UNKNOWN | Thermal unavailable | Device status and missing frames |
| F06 thermal stale | Native time/FFC/age checks | Fresh thermal support | Other qualified channels | WARN or UNKNOWN | Thermal frame stale | FFC/time/age |
| F07 GNSS lost | No fix or expired solution | Precise global guidance | Local sensing; bounded motion evidence | UNKNOWN for navigation-dependent task | Position unavailable | Raw/normalized fix quality |
| F08 RTK corrections lost | Correction age/base link | RTK-qualified positioning | Single solution only if valid, local sensing | WARN then UNKNOWN if required accuracy lost | RTK degraded | Correction/base/reference state |
| F09 IMU invalid | NaN/norm/axes/report fault | Inertial aiding | GNSS/wheel evidence if qualified | UNKNOWN when motion required | Motion aiding invalid | Rejected sample and estimator status |
| F10 wheel sensor failed | SPI error/gap/ambiguous unwrap | Affected wheel response | Other observations | UNKNOWN; STOP in enabled phase if essential | Wheel response unavailable | Channel flags/time/response |
| F11 Wi-Fi lost | Connection/age expiry | Cooperation/corrections/control room | Independent local path | UNKNOWN for fleet-required task; no relaxation | Cooperative view unavailable | Peer/correction age and link |
| F12 second vehicle lost | Expected peer age timeout | Peer conflict assessment | Local sensing; stale marker | UNKNOWN | Peer last known; not clear | Last pose and uncertainty growth |
| F13 base lost | Base owner/correction expiry | Qualified correction source | Local sensors; GNSS native degraded state | UNKNOWN if position requirement fails | Base corrections unavailable | Base epoch/reference/age |
| F14 browser closed | Observer disconnect | Remote display only | Local sensing/decision/endpoint/recording | Unchanged unless another fault | No local fault solely from observer absence | Observer count and continuing tick |
| F15 Jetson overloaded | Deadline/queue/resource alarm | Late affected evidence | Expiry and independent cutoff | UNKNOWN or STOP in enabled phase | Processing deadline missed | Timing, drops, capability loss |
| F16 disk full | Quota/write failure | Complete recording | Local processing if isolated | WARN; STOP for a test requiring recording before continuing motion | Recording unavailable | Write error, dropped records, session status |
| F17 ESP32 link lost | Pending response/disconnect/session retirement | Endpoint confidence | Observational sensing | STOP in enabled phase; UNKNOWN capability otherwise | Endpoint unavailable | Session/sequence/timeout |
| F18 old packet | Source epoch/sequence/time rejection | That observation/request | Previously valid evidence until expiry | No increase; UNKNOWN at expiry | Stale packet rejected | Rejected ID/age |
| F19 duplicate packet | Identity/sequence duplicate | No new sample | Prior valid evidence until expiry | No increase | Duplicate ignored | Duplicate count, unchanged deadline |
| F20 wrong session | Exact V2 session mismatch | Request acceptance | Zero-output supervisor | STOP/inhibited | Session mismatch | NACK/drop reason/session |
| F21 future timestamp | Clock-bound validation | Affected timing evidence | Other independent evidence | UNKNOWN if required | Invalid observation time | Native/mapped timestamps |
| F22 bad CRC | CRC32C mismatch | That frame | Supervisor local expiry | No increase; eventual STOP/inhibited | Communication corruption | CRC counter, no false ACK |
| F23 brownout | Separate physical voltage/reset test later | Affected electronics/authority | Manual cutoff | STOP/inhibited | Restart required | Reset/boot identity/output measurement |
| F24 main compute crash | Independent endpoint expiry later | Perception/requests | Endpoint fail-disabled behavior and physical cutoff | STOP/inhibited | Local processing lost | External output/time reference |
| F25 map outdated/closure conflict | Version/validity/review check | Confident route instruction | Local sensing and overview | UNKNOWN or RESTRICT per approved task | Route unavailable/restricted | Map revisions/restriction source |
| F26 time offset unbounded | Clock mapping failure | Remote prediction/time fusion | Local-clock valid observations | UNKNOWN for dependent task | Peer timing unknown | Offset/error/clock epoch |
| F27 sensor reconnect | New epoch and identity/calibration gates | Usability until restoration | Other qualified evidence | No automatic NORMAL | Recovering source | Fresh sample counts/dwell |
| F28 unmapped road | No credible edge candidate | Turn guidance/fleet-route assurance | Local sensing | UNKNOWN for navigation-dependent task | Unmapped road | Candidate scores/map version |

## Common pass criteria and execution

Every row passes only if: detection occurs at the declared policy boundary; the stated capability is removed; no false value/freshness or increased authority appears; driver and control room agree on cause/source; required event evidence exists; queues remain bounded; and recovery requires new qualified evidence. Conditional states are resolved by the predeclared task dependency profile in 19, never chosen after the test. A known stop hazard remains latched through unrelated uncertainty.

Use deterministic software fixtures first, with injected clocks/bytes/frame objects and no physical openers. Test one fault then combinations: common hub loss; base and both rovers degrade; RGB/thermal common occlusion; disk-full with overload; reconnect plus delayed old frame. Test exact threshold minus/at/plus and malformed types, NaN/Infinity, oversized buffers and clock rollback. Distinguish valid-empty radar from missing reports.

Brownout/compute crash output claims require separately authorized physical tests in 44; software simulations establish handling logic only. Record expected versus actual outcomes, pass/fail and first mismatch without deleting failures. This plan contains no claimed pass count.
