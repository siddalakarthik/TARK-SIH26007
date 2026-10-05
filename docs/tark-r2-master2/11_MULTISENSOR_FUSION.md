# 11 — Multisensor fusion and disagreement

Choose late measurement/track association, not an end-to-end black-box safety score. Each source remains independently inspectable. Radar owns measured range/radial-motion evidence; RGB supplies semantic hypotheses; thermal supplies contrast support. Localization supplies ego pose only within its uncertainty.

## Association contract

1. Reject invalid/stale/unregistered frames and unknown calibration.
2. Bring measurements to a bounded common time; prediction uncertainty includes time-offset and ego-motion error. If alignment cannot be bounded, do not associate.
3. Transform radar uncertainty into each optical image. Without elevation, use a justified projection region; never a fictitious exact pixel.
4. Gate geometric residual by covariance and calibration error. Include temporal consistency and optional class compatibility; class cannot override a failed geometric gate.
5. Solve gated costs with Hungarian assignment and explicit unassigned choices. Cost weights/thresholds are versioned after labelled evaluation.
6. Preserve MATCHED, UNMATCHED, DISAGREEMENT and UNSUPPORTED_CLASS records plus source IDs. No forced matching.

Matched support does not automatically shrink covariance: sources can share calibration, timing or ego-pose errors. Keep source covariances separate initially. Only perform a joint estimator update with justified cross-correlation; if unknown, use a conservative bound rather than naive inverse-variance averaging. Do not count a radar-derived range copied into the RGB record as a second measurement.

## Disagreement decisions

| Case | May conclude | May not conclude | Remaining capability / driver message |
|---|---|---|---|
| Radar valid, RGB absent, thermal warm | Geometric return; separately a thermal region; association only if gated | Named high-confidence person/truck automatically | Range warning: “Object ahead; class uncertain” |
| RGB truck, no matching radar | Visual truck hypothesis | Invented range or clear path from radar silence | “Visual hazard; distance unavailable”; envelope cannot rely on missing geometry |
| Thermal region only | Contrast anomaly | Person, exact temperature or distance without support | “Thermal anomaly; unclassified” |
| Radar/RGB incompatible location/time | Two hypotheses or timing/calibration failure | Average into one object | Preserve both, restrict relevant capability |
| All channels silent | No supported detections at those times | Road clear or fog penetration proved | Coverage/operating condition still requires independent qualification |

Test crossing targets, false semantic matches, correlated biases, offset timestamps, missing channels and duplicate observations. Record association cost/gates and rejected alternatives so replay explains both what was joined and what was not. More sensors may improve evidence; they do not eliminate common-mode failures.
