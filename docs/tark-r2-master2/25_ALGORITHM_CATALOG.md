# 25 — Algorithm catalog

All entries are selected R2 design methods, not claims of implementation. Parameters/calibration are versioned; complexity assumes bounded inputs. n=points/pixels where relevant, k=tracks, V/E=graph size, m=peers.

| ID / function | Inputs → outputs / method | Why / cost | Calibration and limitation | Failure / test |
|---|---|---|---|---|
| A01 radar clustering | Points/Doppler → clusters; gated DBSCAN | No fixed object count; typical O(n log n), worst O(n²) | Range-dependent density/epsilon; singleton handling | Sparse/clutter errors; known reflectors/multi-target |
| A02 tracking | Measurements → CV Kalman tracks, FPFᵀ+Q | Bounded state, explainable; assignment O(k³) | Q/R and ego compensation; turning | ID swaps/gaps; labelled trajectories |
| A03 fusion association | Calibrated timed evidence → matched/unmatched; Mahalanobis/Hungarian | Retains disagreement; O(k³) | Extrinsics/time/correlation | Wrong joins; offset/occlusion fixtures |
| A04 TTC | r,r_dot → valid radial r/(-r_dot) | Simple when closing; O(k) | Geometry/relative-motion validity | Zero/receding/unknown; analytic vectors |
| A05 CPA | p,v → t=−p·v/(v·v), min separation | Crossing support; O(k) | Full relative velocity/horizon | Radial-only insufficient; crossing paths |
| A06 image quality | Image → contrast/edges/sharpness/clipping | Observable degradation; O(pixels) | Scene/exposure reference; no visibility meters | Low texture/glare; held-out conditions |
| A07 RGB detection | Image → boxes/class distribution; YOLO11n candidate | Edge benchmark baseline; model-dependent | Weights/license/domain calibration | Mine class/domain shift; run-split evaluation |
| A08 thermal regions | Raw image/FFC → contrast components | Transparent initial method; O(pixels) | Noise/background/mode | Reflections/isothermal targets; reference frames |
| A09 wheel response | Angle/time/radius → signed omega and v_wheel | Direct response evidence; O(1) | Radius/sign/gap; slip not observed by angle | Wrap ambiguity; marked rotations |
| A10 localization | GNSS/gyro/wheels → planar EKF pose/covariance | Limited, inspectable state; fixed-size matrix operations | Bias/reference/lever arm/noise | Drift/common bias; reference course/faults |
| A11 map matching | Pose/covariance/history → edge candidates | Geometry+topology gating; spatial index O(log E+candidates) typical | Map uncertainty and heading | Adjacent road ambiguity; synthetic graph tests |
| A12 route planning | Valid graph/restrictions → route | Dijkstra; O((V+E)log V) | Nonnegative costs, closures | Disconnected/closed route; known shortest paths |
| A13 fleet conflict | Qualified peer paths → occupancy overlaps | Route-aware, O(m² c) for bounded candidate paths c | Position/speed/time/map bounds | Stale peer/zero speed; scenario truth |
| A14 stopping | v,tau,a,M → v tau+v²/(2a)+M | Explicit assumptions; O(1) | Actual deceleration/reaction, grade/load | Invalid a/speed; boundary/property tests |
| A15 supported speed | D_usable → quadratic inversion | Transparent monotonic cap; O(1) | Characterized coverage, not radar silence | Unknown D/M>D; analytic roundtrip tests |
| A16 state authority | Capabilities/reasons/latches → five-state result | Deterministic priority/dwell; O(reasons) | Approved thresholds/dependency profile | Recovery raises authority prematurely; transition tests |
| A17 replay | Checkpoint+ordered inputs → decisions/comparison | Same core, isolated clock; O(records) | Schema/model/config identity | Corruption/partial coverage; full-session comparison |

No algorithm name is a novelty claim. [08](08_RADAR_PERCEPTION.md)–[20](20_LOCAL_ENDPOINT_ARCHITECTURE.md) own formulas, contracts and policy. Capabilities cannot be reconstructed from one aggregate confidence score.
