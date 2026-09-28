> ARCHIVED RESEARCH REPORT — copied text from VERIFICATION_REPORT.md in the
> fingerprinted Simulation 2 archive. Not rerun by R1, not production evidence.

# Simulation 2 Verification Report

## Source package
TARK SIH26007 Simulation 2 — Fixed-Covariance EKF vs Quality-Adaptive-Covariance EKF

## Verification performed
- Python syntax compilation: PASS
- Standalone pytest suite: 12/12 PASS
- Full supplied package output set present: 8 PNG plots + required CSV/JSON outputs
- Calibration-result consistency: PASS (best calibration row matches chosen parameters)
- Five degradation result tables present for position RMSE, velocity RMSE and TTC
- 100 paired Monte Carlo runs per degradation level in the supplied completed output
- Ground-truth leakage structural check: PASS
- Reproducibility design: deterministic SHA-256-based seed generation
- Reduced-run end-to-end execution using the same code path: PASS
- Reduced run completed all calibration, sanity, Monte Carlo, statistics, CSV and plot stages

## Independent checks
The supplied completed output reports:
- Position RMSE: adaptive is better at C1-C4 and slightly worse at C0
- Velocity RMSE: adaptive is worse at C0 and better at C1-C4
- TTC error: adaptive is worse at C0 and better at C1-C4
- Track retention is 100% for both filters at every degradation level, so it is not discriminating
- NEES shows the fixed filter becomes strongly overconfident as degradation increases

## Important interpretation limitation
The sensor-quality variables are synthetic exogenous signals conditioned on degradation level.
They are not learned from actual LD2450/MLX90640 measurements. Therefore the study supports:
“given a reasonably informative quality signal, adaptive covariance can improve estimation under these synthetic conditions.”
It does NOT support:
“the real sensors will automatically produce these quality values,”
or any real-world mine performance claim.

## Claim boundary
Simulation 2 is a concept-stage estimator/uncertainty experiment. It does not validate the complete physical PV-SOE safety system, real fog physics, actual sensor performance, vehicle dynamics, or mine deployment.
