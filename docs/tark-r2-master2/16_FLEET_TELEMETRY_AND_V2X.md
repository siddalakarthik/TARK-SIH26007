# 16 — Fleet telemetry and V2X

Prototype: local Wi-Fi through TL-WR902AC with Jetson Ethernet, Pi/laptop Wi-Fi. No LTE/LoRa/C-V2X hardware added. Industrial transport is abstracted from the message contract.

## Proposed message

FleetState carries schema_version, vehicle_id, boot_id, sequence, acquired_at plus clock mapping/uncertainty, sent_at, position/frame/reference, position_quality/covariance, heading/reference/validity, speed/source/uncertainty, current_route_edge and chainage, route/map revision, destination, operating_state, nearest_hazard summary, sensor_health, network_health, evidence expiry and original source mode. Use explicit nulls for unavailable data. No direct throttle, steering, reset or motor payload.

Design selection: laptop fleet service with authenticated persistent TLS WebSocket connections from Jetson/Pi, relaying bounded validated state to peers and observers. Corrections use a separate bounded stream/channel with base/reference metadata through the same local IP network. No separate direct-drive UDP/ESP-NOW path. Loss of central relay removes cooperative capability, not local sensing.

Proposed test profile: 10 Hz publication, 200 ms fresh, 500 ms stale, 2 s missing per [07](07_EVIDENCE_AND_DATA_CONTRACT.md). Published p95 age target is not a worst-case guarantee. Bound payload initially to 8 KiB/state, 16 participating nodes and latest-state queue per source for the student test profile; overflow invalidates affected cooperative coverage rather than silently dropping hazards. These are design limits, not measured capacity.

## Integrity and timing

Provision vehicle identities and per-device credentials; TLS authenticates peer/service. A checksum alone is not authentication. Reject unknown version, wrong frame/reference, invalid ranges, duplicate/out-of-order sequence, unknown identity and replayed boot session. Sequence reset requires a new authenticated boot/session record. Validate message age against clock-offset uncertainty; receipt does not make old coordinates fresh.

Extrapolate only within a bounded motion/clock model. Stale node remains on map as last-known with expanding uncertainty, age and UNKNOWN conflict capability. It does not disappear to imply empty road. A configured peer expected but absent prevents “all peers clear.” Uninstrumented vehicles always remain outside cooperative knowledge.

RTCM transport is byte-preserving under documented receiver framing; log correction age/type/base identity as available. Do not restamp old corrections or invent a correction encoder. Base/relay restart invalidates the old stream and requires reference verification.

Industrial mapping: transport-neutral mine Wi-Fi/private LTE/5G or approved V2X after coverage/security/site study. Prototype Wi-Fi throughput is not mine availability. Tests include both rovers losing base simultaneously, clock mismatch, stale relay, duplicate IDs, network bursts, unknown vehicles and malicious oversized messages.
