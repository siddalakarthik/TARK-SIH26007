# R3 reasoning — adversarial design review before implementation

4 October 2026. Output A for the controlled perception/advisory phase.

## Decisions and attack surface

- Keep the legacy decision object, engine, simulation, protocol and zero-output
  control path intact. Add `TARK_R3_ADVISORY_1` beneath the R3 extension.
- Consume only the existing locally admitted EvidenceChannel. Never trust a
  caller's generic `qualified` flag. Compute purpose grants from its current
  health/time/calibration plus modality-specific uncertainty and semantics.
- A fresh empty radar frame is not clearance. A positive operating envelope
  requires a separately identified coverage model for every required hazard
  class. Default coverage is UNKNOWN. Configured fixture ranges are research
  assumptions, never manufacturer range or measured fog performance.
- Use bounded deterministic nearest-neighbour track association, not an opaque
  Kalman filter. Retain position error bounds; do not invent covariance. Body
  frame is x forward, y left, z up and requires an explicit source transform.
- Radar Doppler stays radial. Two position samples can support an explicitly
  conditional fixed-body-axes relative-motion estimate only with qualified
  angular-motion evidence and configured model bounds. Otherwise TTC is null.
- RGB/thermal semantics require versioned inference metadata. Image boxes do
  not supply range. Association requires time, calibrated projection, FOV and
  uncertainty compatibility; ambiguous candidates stay POSSIBLE/UNRESOLVED.
- Cooperative positions remain a separate list, not radar tracks. Conflict
  requires a reviewed configuration-defined geographic conflict zone, position
  uncertainty and correction policy. Expiry removes positions, not just a badge.
- Speed from encoders is WHEEL RESPONSE and needs a configured count convention,
  measured/research scale and slip allowance. No silent ground-speed claim.
- Degradation cannot increase capability. Loss of previously supporting evidence
  holds the prior ceiling or degrades it. Recovery requires distinct accepted
  frames and configured dwell. A vanished hazard is not automatically a clearance.
- Research stopping model: response distance + constant-deceleration distance +
  configured margin. Unknown ego speed or insufficient observability produces
  UNKNOWN, not a made-up numerical speed/TTC. Critical distance can still justify
  STOP without knowing full target motion.
- Record configuration, software, input provenance and initial reasoning state.
  Replay restores an isolated channel and engine; no live callback or actuator.
  Compare deterministic decisions, excluding measured execution latency.

## Required checks

25 named fixture scenarios, parameter-sweep monotonicity, duplicate/order/time/
calibration faults, no ghost peer, no Doppler-as-vector, nullable TTC, restart and
checkpoint replay, public read-only authority, existing backend/frontend suites,
TypeScript/build and a browser review of the minimal HMI changes.

## Release boundary

All default numeric research parameters need explicit provenance. No exact
camera/thermal accuracy, real-fog range, full-scale HEMM braking, model accuracy,
physical synchronization or mine readiness is asserted. No physical device is
opened. This phase implements reasoning, not device commissioning.
