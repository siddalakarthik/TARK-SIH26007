# 15 — Driver navigation

Position/quality + qualified heading + road graph → candidate edges → current edge/chainage → destination → route → maneuvers → driver guidance. It is assistance, not autonomous steering or a source of motor commands.

## Method selection

Choose Dijkstra as primary for the small local mine/course graph: nonnegative costs, no admissible-heuristic assumptions, straightforward closure handling, O((V+E)log V) with a heap. A* is a later performance-equivalent option only if its heuristic is proven a lower bound for the chosen cost. No need to add algorithm complexity before graph scale requires it.

Edge cost = travel-time estimate from an approved planning speed plus nonnegative operational penalties. Exclude closed/wrong-direction/incompatible edges. Unknown safe speed is not replaced by map limit; routing estimates are explicitly PLANNING ETA. No production-loss percentage follows from a shorter graph path.

Map matching: geometric/covariance gate, heading compatibility when valid, and continuity from the last edge using reachable distance. Score candidates with normalized residuals and topology. Require configured separation between best candidates; otherwise keep alternatives and AMBIGUOUS. Do not use a hard snap to hide RTK degradation.

## Guidance rules

| State | Message/action |
|---|---|
| Unique current edge and valid route | Proceed straight; show current road/destination |
| Approaching qualified junction | Prepare left/right, then turn left/right based on verified topology |
| Near destination along route | Destination ahead; arrival needs bounded position and route tolerance |
| Closed next edge | Route blocked; compute alternate, never command a turn onto closed road |
| Off route with valid location | Recalculating with route revision |
| Invalid/poor GNSS | GNSS degraded; withhold precise maneuver |
| Multiple edges/unmapped | Position uncertain; show overview and last known context |

Maneuver trigger distance depends on speed, reaction allowance, localization/map uncertainty and junction geometry, not a hardcoded universal number. Freeze targets before testing. If heading at rest is unavailable, keep orientation unknown rather than spinning a precise arrow.

A requested destination is operational context only. Route service runs outside the local decision deadline and cannot raise an envelope. Failed route computation leaves local sensing active. Internet routing/geocoding is not required; offline graph and locally available lawful tiles work independently.

Tests: start at junction, adjacent edge ambiguity, reverse direction, missing position, route closure, unreachable destination, map-revision mismatch and route failure. Log selected edge, alternatives, costs, reasons and displayed message for replay.
