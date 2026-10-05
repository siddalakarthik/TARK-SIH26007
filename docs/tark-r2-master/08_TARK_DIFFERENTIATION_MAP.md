# TARK R2 — differentiation as testable system behavior

Revision M1 • Proposed R2 capabilities, not new implementation or mine-validation claims.

The competitor matrix establishes overlap in descriptions, not exclusive prior art. The following is the intended technical case for TARK; it is not a claim that no competitor has similar work.

| Capability | Hardware enabling evidence | Proposed software behavior | Falsifiable demonstration / metric | Claim boundary |
|---|---|---|---|---|
| Evidence-quality engine | Identifiable radar/RGB/thermal/IMU/GNSS/wheel sources plus SSD | Preserve origin, acquisition time, receive time, calibration, freshness and uncertainty | Disconnect or delay each source; audit invalidation latency and recorded reason | Hardware alone does not implement this engine |
| Faults cannot increase authority | Local compute and supervisory endpoint; independent manual disconnect | Loss of relevant evidence can only preserve or reduce capability within a defined state/context | Fault injections compared to pre-fault authority, including reboot/stale peer/no-data cases | Not a mathematical safety proof or certified controller |
| Preserve disagreement | Radar geometry, visible semantics and thermal contrast | Retain contradictory hypotheses; no blind confidence averaging | Show radar-only, RGB-only and thermal-only targets; record association errors | Multiple sensors can share a common failure |
| Evidence-aware operating envelope | Characterized distance/uncertainty, wheel response, IMU and route context | Use supported distance and conservative stopping model, not sensor marketing range | Degrade contrast/health; plot reasoned envelope changes with input provenance | Robot deceleration does not establish truck stopping distance |
| Blind-curve conflict intervals | Two rover kits, base, local IP link | Route-graph conflicts with timestamp, direction, speed and uncertainty intervals | Two instrumented nodes approach a mocked junction outside mutual view; stale-peer case included | Participating vehicles only; no omniscient view of uninstrumented traffic |
| Mine navigation | RTK-capable location, IMU, driver display | Local road graph, next maneuver, destination and deviation with quality checks | Surveyed small outdoor course; incorrect route/poor fix must be shown as uncertain | No mine survey, HD map or assured lane-level performance exists yet |
| Explainable evidence replay | SSD and stable identities/time records | Record unavailable evidence, state reason, requested versus accepted action | Reconstruct an incident from immutable original observations and label recomputation | Not a “digital twin” claim based merely on animation |
| Offline local operation | Local compute, sensors, endpoint and AP | Internet/browser/control-room loss does not disable local processing | Remove internet, then AP; differentiate local capability from cooperative capability | Cooperative conflicts and RTK corrections degrade when their link is lost |
| Capability degradation | Complementary channels with separate health | RGB loss removes semantic confidence; GNSS loss removes precise global guidance; radar loss removes selected geometry authority | Per-source fault matrix and retained/lost capability indicators | Remaining sensors do not automatically cover the lost sensor's domain |
| Controlled low-visibility characterization | Rigid fixtures, contrast board, radar/thermal references, aerosol allocation | Store actual experimental conditions and matched clear/aerosol data | Range-dependent detection, false-alarm and latency statistics with repeated trials | Artificial aerosol is not Bailadila monsoon validation |

## What strengthens the submission

A strong demonstration answers **what is known, how old it is, why a warning occurred, and what capability is lost when evidence fails**. Present one coherent experiment instead of claiming that adding sensors makes the system safe. Publish failures and unsupported regions as well as successes.

No percentage improvement in safety, cycle time, production or fleet utilization is allocated to these features. Those require an operational baseline and controlled field evaluation. The prototype can measure timing, task success, nuisance warnings and evidence availability; the industrial benefit remains a hypothesis.
