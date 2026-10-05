# 17 — Blind-curve and junction conflict prediction

Purpose: detect potential overlap of participating vehicles' occupation of a shared road region before direct line of sight. Not a traffic-light clearance system; not knowledge of uninstrumented vehicles.

Inputs: qualified local/peer position, route-edge candidates, direction, speed interval, acquisition age/clock uncertainty, map/reference revision, vehicle footprint and conflict geometry. A planned route is intent, not certainty: consider all plausible reachable successor edges when commitment is uncertain.

## Occupancy interval calculation

For a region entry at along-route distance d, use d in [d_min,d_max], speed in [v_min,v_max], and bounded age/motion prediction. With constant-speed assumption and v_min>0:
earliest_entry=max(0,d_min)/v_max;
latest_entry=max(0,d_max)/v_min.
Include clock/time uncertainty and any justified acceleration bounds; do not claim these are physical bounds until characterized.

Zero-speed guard: if v_max=0, never evaluate the division. A vehicle already overlapping the region remains occupied with no justified finite exit. A vehicle outside the region has no entry under the stated constant-zero-speed hypothesis; this is not clearance against possible later acceleration. If acceleration or position bounds are unavailable, retain UNKNOWN for the affected prediction. Reject negative/inverted speed intervals and nonfinite values before interval arithmetic.

Exit uses distance to region exit plus vehicle footprint. Occupancy interval is [earliest_entry, latest_exit], expanded by a configured time margin. If v_min<=0, latest exit may be unbounded; do not divide by zero or drop the stationary peer. A vehicle currently in the constrained region is occupancy evidence until a fresh qualified exit observation exists.

Opposing directions on one narrow road share the entire non-passing section. Crossing junctions use overlapping swept polygons. Merges use the shared downstream interval. Stopped vehicles retain occupancy with uncertainty. Distinct separated roads are not a conflict just because map coordinates are close.

## Result and policy

| Result | Condition | Meaning |
|---|---|---|
| UNKNOWN | Missing/stale/unbounded time, map mismatch or ambiguous reachable geometry | Cannot assess; never “clear” |
| HIGH_CONFLICT | Valid evidence of current overlap, or near-term overlapping occupancy under the predeclared high-priority rule | Strong warning, not certainty of collision |
| POTENTIAL_CONFLICT | Conservative plausible occupancy intervals overlap | Warning with source/age/region |
| NO_CONFLICT | Qualified intervals provably disjoint over stated horizon for evaluated participating peers | No predicted conflict in limited scope, NOT clearance |

A target 10 s prediction horizon and 3 s high-priority horizon may be used in software fixtures as PROPOSED VALIDATION TARGETS; real values must follow speed/geometry/latency characterization. A high-conflict rule applies to plausible cases and must not average away uncertainty. UNKNOWN from one peer cannot be hidden by NO_CONFLICT from another. Preserve the last valid warning while adding degraded/unknown status; do not silently relax due to loss.

Output includes region, involved node IDs, candidate paths, occupancy intervals, uncertainty, source ages, risk result and reasons. Local observer receives “Potential opposing vehicle in narrow section; peer age …”, not “road safe.” No centralized intersection reservation is designed as enforced right-of-way.

Validation: opposing curve, simultaneous crossing, merge, stationary occupancy, diverging routes, stale peer, wrong map, common base bias and unknown road user. Compare warning lead time against independent ground truth and report nuisance warnings as well as misses.
