# 07 — Evidence, time and normalized contracts

PROPOSED R2 model, not a silent change to existing API or wire payloads.

| ObservationEnvelope field | Type / meaning |
|---|---|
| schema_version, observation_id | Version and unique observation identity |
| vehicle_id, source_id, sensor_type | Registered source owner |
| source_mode | REAL / SIMULATION / REPLAY; REAL is origin, not qualification |
| original_source_mode, replay_session_id | Required replay provenance |
| source_boot_id, sequence | Restart-aware ordered identity |
| sensor_timestamp | Nullable native value with clock_id/unit/meaning |
| host_received_at, processed_at | Host monotonic ns and host boot ID |
| clock_mapping_id, time_uncertainty_ns | Cross-clock mapping or explicitly unknown |
| calibration_id, hardware_id, software_id, configuration_hash | Applicable provenance |
| freshness_ms | Evaluated age; publication never renews it |
| validity | VALID / INVALID / UNKNOWN and reason |
| quality | NOMINAL / DEGRADED / UNKNOWN plus typed metrics |
| uncertainty | Unit-tagged covariance/bounds/provenance; null not zero |
| frame_id, units, payload | Typed bounded measurements, no unbounded media |
| loss_counter, coverage_id | Loss diagnostics and characterization reference or null |

CONNECTED != FRESH != VALID != USABLE != COVERAGE_CHARACTERIZED. Connection means transport; freshness means age; validity means measurement/schema checks; usability means fit for a specific calibrated task; coverage needs experimental evidence. Quality is not a universal AI score.

Freshness: MISSING/never seen, FRESH, AGING, STALE. Configuration absence is NOT_CONFIGURED; configured absent device UNAVAILABLE. Frozen frames are stale even if transport is open. Empty radar observations differ from missing observations.

## Clocks

Local monotonic time controls local expiry. GNSS UTC/display time is separate, with validity and conversion/leap handling. Jetson/Pi/laptop monotonic epochs differ. Local NTP/chrony may estimate shared UTC offset, but mapping error/discontinuities must be measured and recorded. Receive time is not simultaneous exposure. No PPS/shared trigger is selected.

Remote age is an interval using clock-offset uncertainty. If age cannot be bounded, prediction is UNKNOWN. Replay uses recorded virtual time and clock mappings. Future local timestamps are rejected; remote future time outside its mapped bound is invalid. No new tolerance is added to Protocol V2.

## Initial test policy — PROPOSED VALIDATION TARGETS

| Source | Intended rate | Fresh / stale age | Missing beyond |
|---|---:|---:|---:|
| Radar | Profile dependent | 150 / 300 ms | 1000 ms |
| RGB | Capture ~30, inference 10 Hz | 200 / 500 ms | 1500 ms |
| Thermal | 8.7 Hz | 300 / 600 ms | 2000 ms |
| GNSS | 5–10 Hz | 300 / 1000 ms | 3000 ms |
| IMU | 100/50 Hz | 50 / 150 ms | 500 ms |
| Wheel | 100 Hz | 50 / 150 ms | 500 ms |
| Fleet | 10 Hz | 200 / 500 ms | 2000 ms |

These are software-test profile parameters, not qualified safety deadlines. Real motion is blocked until observed timing justifies them. Removal of a required stream removes its capability. Reconnect requires fresh valid samples, identity/configuration/calibration checks and recovery dwell; merely restarting a worker does not restore authority.

Reject nonfinite numbers, invalid units/frames, negative distance/uncertainty, malformed covariance, payload overflows, duplicates/regressions and invalid quaternion norm. Missing fix is not coordinate zero. Detailed reasons use SENSOR, GEOMETRY, MOTION, LOCATION, FLEET, ENVELOPE, ENDPOINT, RECORDING and CONFIG namespaces. Preserve all reasons and choose primary deterministically via [19](19_OPERATING_AUTHORITY_STATE_MACHINE.md); do not inject new names into strict V2 schemas.
