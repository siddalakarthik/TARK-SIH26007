# 22 — TARK command platform

Architecture target: existing React + TypeScript + MapLibre frontend; FastAPI projections/REST; bounded WebSocket telemetry; local edge decisions. Laptop fleet service aggregates observations from Jetson/Pi. One-origin serving is retained where deployed. Control room is MONITORING / approved operations context, never arbitrary motor drive.

Student storage remains existing local SQLite/recording architecture with versioned extensions. Industrial scale may later use MQTT ingestion, PostgreSQL/PostGIS metadata, Redis bounded latest state and object storage; these are a migration direction, not requirements added to this demonstrator or implemented claims. OIDC/JWT/RBAC/TLS/device authentication are designed in [35](35_SECURITY_ARCHITECTURE.md).

## Pages

All rates below are proposed UI targets; source timestamps remain unchanged.

| Page | Purpose/data/widgets | Allowed actions | Forbidden actions | Update target / failure |
|---|---|---|---|---|
| Fleet Command Center | Vehicle map, states, stale peers, active incidents/conflicts, node count | Select/filter/fit fleet, inspect evidence | Direct drive, declare absent peer clear | 5 Hz latest state; retain stale markers |
| Vehicle Detail | Identity/version, route, speed source/cap, sensor/endpoint health | Inspect history/configuration revision | Change safety cap or reset endpoint | 5–10 Hz; explicit expired data |
| Live Perception Console | Radar local tracks, RGB/thermal frames, association/disagreement | Select track/frame, inspect provenance | Fake range/class or force fusion | Bounded native/inference rates; missing frames labelled |
| Incident Monitor | Severity/time/reasons, affected vehicles and evidence links | Search/filter/acknowledge receipt | Clear cause through acknowledgement | Event driven, deduplicated; ingestion gaps visible |
| Incident Replay | Session catalog, timeline, original/recomputed comparison | Play/pause/step/seek/reset/speed | Submit replay commands or overwrite live state | Isolated playback clock; corrupt/incompatible rejected |
| Mine Navigation | Map versions, closures, destinations and route feasibility | Authorized proposal/review of mission/restriction | Override local constraints or silently reopen road | On revision + 5 Hz poses; ambiguity shown |
| Operations Analytics | Actual recorded cycle/restriction/downtime metrics | Choose matched cohorts/time filters/export | Invent fleet or production counts | Query based; unavailable evidence stays unavailable |
| Maintenance/Calibration | Identity, health, calibration validity, pending service | Record approved maintenance/calibration evidence | Mark physical verification without run evidence | On change; expired calibration visible |
| Administration | Users/devices/roles/configuration signatures/version audit | Authorized provision/revoke/review | Live arbitrary motor API or uncontrolled parameter edits | Request based; failed auth/change audit retained |

Fleet map supports zoom/pan/select/all-vehicle fit, route/destination/edge, speed/state/hazard/conflict, blind curve, closures, restricted zones, GNSS quality and stale footprint. A stale vehicle persists at last known location with age/uncertainty rather than disappearing. Geographic position and radar local coordinates are not interchangeable.

Each panel has source mode REAL/SIMULATION/REPLAY and provenance. Mixed-origin snapshots show component sources individually, not a misleading universal LIVE badge. REAL does not mean physically validated. Network outage leaves local sensing active; control room displays disconnected/last received time, not stale NORMAL as current.

Keep one map instance and one subscription owner per app shell; update GeoJSON sources in place. Latest-state coalescing, bounded history, paged/virtualized event tables and isolated media decoding protect responsiveness. Measure render/queue/map latency before an “optimized” claim.
