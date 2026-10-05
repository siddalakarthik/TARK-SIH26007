# Master-2 — localization, navigation and cooperative fleet logic

## 1. Physical positioning topology

Use the three frozen Waveshare 33000/LG290P kits: rover A on the main demonstrator, rover B with the Pi peer, and one fixed base linked to the laptop. Each uses its supplied active GNSS antenna. The AP distributes corrections and peer/observer data locally; no internet subscription is required by this design.

The base relay forwards only the documented correction stream for the identified receiver/firmware configuration. One owner per serial device handles input/output; no competing readers. Receiver commands, supported RTCM messages and rates must match the actual firmware's manufacturer documentation. No speculative binary format or pasted command sequence is invented here. [Quectel LG290P documentation](https://www.quectel.com/product/gnss-lg290p/)

Log base identity, coordinates, datum/reference, antenna reference point, configuration version, correction sequence/time and movement/tamper status where actually observable. The system cannot know the base moved merely because software calls it fixed; include a physical setup check and receiver-consistency tests. Base averaging/survey-in is not a substitute for independently established absolute coordinates.

If corrections stop, the receiver may transition between RTK FIX, FLOAT and standalone/no-fix states. Preserve what it reports and the correction age. Never hold a green FIX label indefinitely or substitute simulated coordinates.

## 2. Localization design

Use GNSS as the absolute-position observation, gyro/inertial evidence for short-term orientation/motion prediction, and qualified wheel response for bounded consistency/odometry. A practical initial R2 planar filter state is `[east, north, speed, yaw, gyro_bias]`, with covariance and explicit assumptions. Pitch/roll and raw acceleration remain separate evidence when a planar model is inadequate.

Prediction uses real elapsed time and a motion model whose limitations are retained. GNSS position/velocity updates require reported validity, time mapping and characterized uncertainty; do not invent a covariance from the RTK label. Wheel observations are rejected/down-weighted on slip/mismatch. Magnetometer-based yaw can be rejected under disturbance; gyro-only yaw then accumulates uncertainty.

Do not feed both a BNO085 fused orientation and its contributing raw gyro as independent observations without accounting for correlation. Stationary single-antenna GNSS does not supply reliable heading; course over ground is qualified only with adequate motion and velocity quality. At initialization or after a long outage, heading can legitimately be UNKNOWN.

A missing filter input must grow uncertainty or invalidate capability, not reset speed to zero. Dead reckoning is bounded by characterized duration/error; it does not promise long GNSS-denied navigation. Keep raw receiver output alongside the fused estimate for diagnosis.

## 3. Mine map and route representation

Use a versioned local road graph rather than interpreting ordinary public-map geometry as surveyed mine roads.

| Record | Required information |
|---|---|
| Map header | Map ID/revision, coordinate reference/datum, survey/reference uncertainty, effective period, approval/source |
| Node | ID, coordinates, type: junction/loading/dumping/holding; reference uncertainty |
| Directed edge | Polyline, permitted direction, usable width/clearance if known, measured length, grade/curvature if known, restriction/closure references |
| Destination | Named loading/dumping/holding node and actual access rules; no invented address |
| Conflict zone | Polygon/edge relationship, priority/hold rule, clearance assumptions and uncertainty |
| Restriction | Source, start/end validity, authorized issuer and affected edges; unknown validity does not silently reopen a road |

Absent width/slope/restriction data stays unknown. Do not auto-create drivable edges from a background map. Map updates are reviewed, signed/authenticated where deployed, versioned and recorded; they are not browser motor commands. Cached stale maps display their age and limitations.

## 4. Map matching and guidance algorithm

Project qualified position into local ENU; compensate antenna lever arm using reliable orientation or expand uncertainty when unavailable. Find candidate road segments consistent with position uncertainty, travel direction and connectivity. Score candidates using distance, heading consistency and prior route continuity; retain multiple candidates when the evidence does not separate them.

Choose a route using Dijkstra/A* on approved open edges, with nonnegative costs for distance/expected traversal and permitted restrictions. Cost assumptions are visible; the shortest line through a closed or unknown road is not a valid route. Any cloud routing service remains an optional external information path, not local safety authority or a required new purchase.

Generate next-turn instruction from the directed graph's manoeuvre geometry and qualified along-route progress. Distances must state their reference, not alternate silently between Euclidean and along-route distance. A deviation warning requires sustained position uncertainty outside the permissible route corridor; do not oscillate guidance around a junction from GNSS jitter.

If localization becomes ambiguous: retain the last-known marker as historical, show age/uncertainty, stop confident turn prompts and report NAVIGATION UNAVAILABLE/UNCERTAIN. Existing India overview remains the no-vehicle-location view; browser device location is never substituted as vehicle position.

## 5. Cooperative peer state

Proposed peer records contain vehicle ID, session/boot epoch, sequence, source/origin, timestamp and clock-quality estimate, position/covariance or bound, velocity/heading validity, footprint, route/map revision, along-route state and health. Fields unsupported by rover B remain null/unknown; a carried peer is not a fully sensed second dumper.

Use bounded latest-state storage per peer and sequence/session checks. Authenticity is a separate requirement from CRC or a vehicle-name string. Do not reuse the Pi↔ESP32 motor protocol as an unauthenticated broadcast control channel. Peer traffic is observational; local code applies its own validity and capability constraints.

For peer age, convert clocks only with a measured/bounded relationship. Include source age, link delay and clock uncertainty. Unknown clock quality prevents precise time-to-conflict claims even if position packets arrive regularly.

## 6. Blind-curve / junction conflict prediction

Identify overlapping route conflict regions using graph topology and expanded vehicle footprints. For each participating vehicle estimate earliest entry and latest exit times, including position, speed, acceleration assumptions, vehicle length, timing and map uncertainty.

For a simple forward constant-speed case, entry interval can use conservative distance/speed bounds. For example `t_entry_min = max(0, d_min) / v_max` when v_max is valid and positive; a finite latest entry requires a positive justified lower speed bound. A stopped/ambiguous/reversing peer cannot be assigned a reassuring finite ETA by division through zero. General motion needs bounded prediction over a finite horizon.

Warn when occupancy-time intervals overlap after the selected temporal margin, not merely when two GNSS points are close. Account for same-lane following, opposing traffic in a narrow section, crossing junctions and loading/dumping queue geometry. Distinguish a vehicle already occupying the zone from one approaching it.

Loss/staleness of a relevant peer changes the result to COOPERATIVE COVERAGE DEGRADED/UNKNOWN, not junction clear. Retain an age-expanded last-known occupancy only within a justified bound; beyond it, position is unknown. No finite expanded bubble can guarantee coverage for unconstrained motion. Uninstrumented vehicles remain local-sensing hazards.

Priority/hold instructions are advisory in this demonstrator. There is no claim of distributed mutual exclusion, autonomous right-of-way reservation or remote braking. Conflicting route/map revisions must be detected and shown; no optimistic merging.

## 7. Example experiment, explicitly not a measured result

Two physical rover nodes follow marked approaches toward a known junction, at low controlled speed and without real collision risk. A visual obstruction makes them mutually unseen while GNSS sky view remains adequate. Record independent reference trajectories, correction/fix quality, link age, computed occupancy intervals, warning time and nuisance warnings. Repeat with stale peer data, lost corrections, ambiguous heading and mismatched map revisions.

The outcome can support a bounded claim about this course and these participants. It does not prove radio/GNSS coverage through Bailadila pit walls or conflict-free mine operation.
