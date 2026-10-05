# 18 — Stopping and evidence-supported operating envelope

Proposed R2 shadow model; current production R1 remains unchanged and zero-output. This is not a calibrated industrial brake model.

## Stopping relation and inversion

For speed v>=0, reaction/processing allowance tau>=0, effective deceleration a_eff>0 and margin M>=0:
D_stop = v tau + v²/(2 a_eff) + M.

Use an upper speed bound, upper latency bound, conservative lower deceleration and separately justified margin. Unknown speed/deceleration or invalid timing returns UNKNOWN, not zero stopping distance. For a prototype, obtain measured loaded coast/brake behavior under the chosen control mode; do not copy dumper braking values. Industrial a_eff depends on load, grade, adhesion, tyres, brake condition and weather; model scope must include downhill/reaction effects.

Let D = D_usable−M. If D>=0:
v² + 2 a_eff tau v − 2 a_eff D <=0;
v_supported = sqrt((a_eff tau)² + 2 a_eff D) − a_eff tau.
Numerically stable equivalent: 2 a_eff D / (sqrt((a_eff tau)²+2 a_eff D)+a_eff tau), with explicit zero/zero handling when D=0 and tau=0. If D<0, no nonnegative feasible speed satisfies the model: report insufficient margin/STOP policy, not a positive root. All inputs finite and unit-checked.

## D_usable is not nearest radar range

Separate:
- D_obstacle: lower-bound along-corridor gap to a supported obstacle footprint.
- D_coverage: contiguous distance over which target/environment-specific sensing coverage is experimentally supported.
- D_route: any qualified stopping boundary/closure/context constraint.
- D_usable: nonnegative lower bound of the relevant constraints with uncertainty/age deductions.

D_coverage requires a versioned characterization grid over range, angle, target class/size, condition and sensing health, with detection/miss/false-alarm evidence. A real run must be within that tested domain. Unobserved near zones, occlusions, unknown environment or stale calibration interrupt contiguity. No extrapolation beyond the tested envelope; no image-quality number converted to meters without calibration.

Sensor silence does not set D_obstacle to a reassuring far range. An absent obstacle measurement can leave that bound undefined; positive support can come only from qualified coverage in a narrowly controlled domain with explicit target assumptions. Before such characterization, D_coverage and supported speed remain UNKNOWN. The current nearest-radar-range model is not relabelled as validated free space.

Corridor is the bounded swept footprint over the stopping horizon using qualified heading/yaw/path assumptions, expanded by localization/track uncertainty. Unknown steering/path prevents assuming a narrow straight corridor. Uncertainty and ageing can reduce support, never increase it while other inputs are fixed.

## Authority composition

Advisory supported cap = minimum of valid envelope cap, approved map/operational restrictions and platform cap. Required unknown constraints cannot be omitted from the minimum. Peer conflict can further reduce/withdraw capability; peer silence cannot restore it. Current phase hard cap is exactly zero regardless of shadow advisory result. Label PARAMETERIZED / NOT VALIDATED until corresponding gates pass.

Test algebra boundaries, zero speed, D<M, null/NaN/Infinity, invalid a, growing uncertainty, occlusion, no-target versus missing report and common sensor failure. Record each term and binding constraint for replay. No collision guarantee, HEMM stopping distance or production benefit is inferred.
