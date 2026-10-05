# SIH SIMULATION JUDGE QA

Analytical/sensitivity research only. Assumed inputs are not measured NMDC values. Physical validation pending; production R1 remains unchanged and traction remains DISABLED_PHASE_1.

## 1. Is any simulator mandated?

No specific tool/method was mandated in the official 2026 PS, guidelines and template reviewed; Digital Twin is optional.

## 2. Where does 3–5 m come from?

Official PS background describes visual visibility. Four metres is a derived midpoint, not a separately measured condition.

## 3. Does 3 m visibility mean 3 m radar range?

No. Visual and trustworthy perception ranges are independent study variables.

## 4. Are these NMDC braking values?

No. All vehicle response, deceleration and reserve sets are assumed sensitivity inputs.

## 5. Is the cap a safe driving instruction?

No. It is a bound within an unvalidated constant-deceleration model.

## 6. What is live motor output?

Exactly zero in the R1 evidence. DISABLED_PHASE_1 remains unchanged.

## 7. Is TTC controlling the live vehicle?

No. Encounter TTC here is a research relative-motion metric, not new production behavior.

## 8. Does the system avoid oncoming impact?

Not guaranteed. The target never brakes; continuing oncoming motion eventually reaches a stopped ego.

## 9. What does negative clearance mean?

A predicted model overlap before the finite horizon; no post-impact physical model is implemented.

## 10. Are slopes included?

No unsupported grade/friction inputs are introduced. Validate effective deceleration over actual conditions.

## 11. Is uncertainty failure share accident probability?

No. It is the negative-margin fraction over arbitrary independent engineering input distributions.

## 12. How was sample count chosen?

Prespecified prefix sizes through 40,000 and stated fraction/percentile stability tolerances; not tuned to attractive results.

## 13. How are headline numbers checked?

Independent bisection, exported-row arithmetic, percentile interpolation and cycle recomputation; corruption must be rejected.

## 14. Can we claim production gains?

Only normalized cycle/throughput indices under declared shares, speeds and dwell assumptions; no tonnage/MTPA forecast.

## 15. Can halt-and-recover be better?

Yes. Assumed dwell and recovery capability determine the result. No universal superiority claim is justified.

## 16. What is the Pareto interpretation?

At fixed resource assumptions, increasing speed consumes margin; optimize only inside nonnegative model margin.

## 17. Has sensor fusion been integrated?

No new fusion/EKF is implemented or credited. Archived fusion research is not a production capability.

## 18. Is this a mine digital twin?

No. It is a reproducible longitudinal and operational sensitivity study, without calibrated mine geometry or plant dynamics.

## 19. What remains for hardware?

Identity, wiring/voltage/HOLD resolution, sensor calibration, range/freshness, loaded stopping and delay measurement, physical watchdog/E-stop and supervised trials.

## 20. Can this be reproduced without equipment?

Yes. Run the isolated study command and verifier, then R1 regression commands. No COM/USB/I2C access is required.
