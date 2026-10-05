# 14 — Mine navigation graph

A local, versioned road graph is authoritative for route context; an internet basemap is a backdrop, not surveyed mine geometry. No Google Maps dependency.

Node types: JUNCTION, LOAD_POINT, DUMP_POINT, WORKSHOP, FUEL, CHECKPOINT, PARKING, BLIND_CURVE_ENTRY, BLIND_CURVE_EXIT, NARROW_SECTION, RESTRICTED_AREA, HAZARD_POINT. Each node has ID, ENU/geographic geometry, datum, survey/reference uncertainty, revision and approved source.

Edge fields: edge_id, from_node, to_node, polyline, measured length_m, direction, allowed_vehicle_type, speed_limit_mps or null, grade_if_known, width_if_known, surface_condition, hazard_level, closure_state, temporary_restriction, weather_restriction, valid_from/until, source, author/reviewer and map_revision. Unknown width/grade stays null, not zero. Speed limits are restrictions, not supported safe speed.

Add conflict-region polygons/edge chainage intervals for junctions, blind curves, merges and narrow sections. Store entry/exit boundaries, directions, incompatible movements, occupancy rules and geometry uncertainty. This supports route occupancy prediction rather than Euclidean proximity alone.

## Construction and update

For a prototype, measure a permissioned marked course with independent references and map its points in the same base/datum. Label it TEST COURSE, never Bailadila map. Inspect node connectivity, duplicate IDs, polyline self-intersections, direction, positive lengths, datum consistency and routability. All edge restrictions are versioned and audited.

Operations staff may propose closures/restrictions; an authorized local workflow validates/reviews and distributes signed revisions. A driver cannot clear a closure by dismissing a banner. If update validity expires, retain conservative closure until reviewed rather than silently reopen the road. Conflicting revisions or missing signature make affected routes unavailable.

Map matching uses uncertainty corridor, direction and transition feasibility; an intersection of plausible roads is AMBIGUOUS. Unmapped position is UNMAPPED, not forced onto nearest edge. Closed roads remain visible, not deleted from incident history. Replays pin the original graph/restrictions and separately label comparison with a new revision.

Test adjacent roads, wrong datum, loop/disconnected graph, closure during a trip, invalid speed/unit and expired restriction. Unknown geometry can still support an overview, but not confident narrow-road clearance.
