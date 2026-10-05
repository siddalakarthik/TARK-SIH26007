# 23 — Incident recording, explainability and replay

Preserve [R1 recording format 2](../REPLAY_GUIDE.md); it currently reconstructs radar observation ticks and a checkpoint. It is not silently renamed full R2 multisensor replay.

## R2 recording design

Record versioned normalized radar reports/tracks; RGB original frame/event references; thermal raw frame/mode/FFC; GNSS and corrections/reference status; IMU; both wheel channels; incoming fleet evidence; map/restriction changes; clocks; health; state/envelope/reasons; requested/accepted/applied command; endpoint status; network/resource failures; driver-visible projection and acknowledgement. Physical response is unknown unless measured; an ACK is not a response measurement.

Each session has software/model/firmware/configuration/calibration/hardware identities, schema version, original source modes, coordinate/datum and clock mappings, deterministic initial checkpoints and record-sequence bounds. Checkpoint includes all temporal histories: track state, filter covariance/bias, peer expiry, state hysteresis/latches, route/map revision, command sequence, and deterministic seeds where used.

Configurable incident windows begin with a bounded ring (example pre=10 s, post=10 s). Trigger pins the pre-window, records event and extends post-window under a maximum session budget. Overlapping incidents may reference shared immutable chunks; do not duplicate unbounded video. Stream-specific byte/age quotas and minimum free-space thresholds must be configured before run. Stop/mark recording degraded on capacity failure, never fabricate completeness.

Metadata SQLite transactions reference chunk files with hashes, byte lengths, acquisition range, format and committed state. Write temporary chunk then atomic finalize where filesystem supports it; recover interrupted manifests without claiming missing frames were recorded. Hashes identify content, not forensic authentication.

## Replay modes

ORIGINAL RECORDING replays preserved observations/projections. REPLAY COMPUTATION reconstructs the declared decision-input stream using the recorded checkpoint and virtual clock. For deterministic decision replay, store normalized detector outputs; rerunning GPU perception is a separate model-comparison experiment and need not be bit-identical.

Catalog → selected session → compatibility/integrity scan → timeline → play/pause/step/seek/reset/speed. Seek loads a valid checkpoint then processes intermediate records; never jump filters straight to the target observation. Replay cannot construct real device adapters, an endpoint client or publish its state as live.

MATCH means all declared fields/records in the comparison scope agree. MISMATCH identifies first divergence, expected/actual and scope. UNKNOWN/NOT_COMPARED means incomplete/incompatible evidence or no original comparison. Corrupt chunks, missing/duplicate/out-of-order sequence, wrong hashes, unsupported versions and invalid checkpoints produce explicit errors. No prefix-only match is reported as full-session match.

## Every incident must answer

What happened; which evidence existed, was missing or stale; what the model believed; why the state changed; what the driver saw; what request reached the endpoint; what ACK/status returned; what physical response was actually measured. Link every answer to source IDs/time and retain conflicting evidence.

Retention is bounded and role-controlled. Protect original recordings from accidental mutation; exports redact private faces/location where required. Actual media bandwidth and NVMe performance are validation items, not inferred from 500 GB capacity.
