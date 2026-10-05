# 29 — KPIs and acceptance

All new numeric thresholds below are PROPOSED VALIDATION TARGETS, not achieved performance. Existing M1 targets retain their scope. Before physical tests, approve tolerances/reference uncertainty and operating conditions; never tune a pass threshold after seeing results.

| Domain | KPI / denominator | Acceptance basis and evidence |
|---|---|---|
| Radar | Range/radial-speed/angular residual distributions; misses/false tracks per opportunity; track continuity/ID switches | M1 1/2/5/10/20 m test positions only where profile/facility permits; error tolerances from task budget and independent reference |
| RGB | Per-class/condition precision, recall, false alerts and accepted-frame availability | Locked run split; small/occluded/mine-class limits explicit; no fake fog distance |
| Thermal | Valid native frames/expected frames, FFC gaps, target contrast/pixels and false regions | 8.7 Hz is component rate, not guaranteed application delivery; temperature only qualified mode |
| Localization | Horizontal/cross-track error, FIX/FLOAT availability, wrong-edge/ambiguous-edge rates | M1 <=0.10 m horizontal-error goal only against adequate independent reference; otherwise repeatability |
| Fleet | Acquisition-age p50/p95/p99/max, duplicates/loss, conflict-warning lead time | M1 >=10 Hz publication and <200 ms p95 age target under declared load; timeout boundary checks independent of p95 |
| Motion | Angle/signed response residual, invalid-gap detection, command-response mismatch | Measured geometry/reference; never ground-truth speed label |
| System timing | Source expiry and decision/HMI transition latency | Proposed 20 Hz decision target; software fixture detection within one next tick after configured expiry |
| Endpoint | Session replay rejection, local expiry, host correlation and reset behavior | Existing V2 host limits preserved; physical time/output binding separately measured |
| Recording | Complete required records/expected records, loss counts, corrupt recovery | No MATCH on partial/incompatible session; original and recomputation distinguished |
| UI | State/action/source comprehension, viewport defects | All specified widths, actual LCD, stale/unknown/stop cases; no color-only meaning |
| Resources | CPU/GPU/RAM/temperature, queue/SSD/network utilization and tails | Concurrent workload below declared budgets; overload visible, no unbounded queues |
| Recovery | Time/evidence to restored capability; false-normal events | No authority increase from fault; valid restoration + dwell required |

Software-test policy values in [07](07_EVIDENCE_AND_DATA_CONTRACT.md) are initial scenarios, not real-motion clearance. Any missing calibration/coverage/reference keeps the associated operational metric unqualified.

## Statistical reporting

Report trials, denominator, exclusions, reference error and confidence intervals. Zero observed failures is not zero risk; approximate upper 95% binomial bound 3/n for zero failures applies only to suitably independent trials and does not certify machinery safety. Adjacent video frames are correlated. State how confidence intervals and repeated-run variability were computed.

Safety-state compliance and physical detection performance are separate tests. A perfectly deterministic replay of a wrong model is still wrong. Report abstention/UNKNOWN rates alongside accuracy, so a method cannot hide hard cases by silently omitting them.

Acceptance report links each metric to requirements R01–R18, fault case, run IDs, software/config/model/calibration/hardware versions and reviewer. This task creates plans and document checks only; no performance results are fabricated.
