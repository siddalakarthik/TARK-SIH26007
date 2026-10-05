# Judge-ready technical Q&A

Use with the [R1 manifest](TARK_RELEASE_MANIFEST.md) and
[claim/evidence matrix](TARK_CLAIM_EVIDENCE_MATRIX.md). Do not imply that a
software pass closes a physical HOLD.

## 1. What exactly is implemented?

A radar-centered software pipeline, health/freshness, provisional PV-SOE, zero commands, Protocol V2 Python/C supervision, persistence/recording/replay, sensor interfaces and a monitoring HMI. The claim matrix separates each implemented boundary from physical work.

## 2. What is PV-SOE today?

A simplified software comparison: nearest active radar range minus stored uncertainty, clamped at zero, versus parameterized stopping requirement. It is not yet calibrated free-space observability or a validated safe operating envelope.

## 3. Where is TTC used?

A helper exists, but the production decision path does not call it. The dashboard correctly says NOT COMPUTED. We do not claim TTC-based intervention.

## 4. Do you use EKF in production?

No. The supplied separate numerical study compares fixed and adaptive covariance. Production tracks are keyed by receiver target slot, not EKF state or guaranteed physical-object identity.

## 5. Did adaptive covariance always win?

No. The archived study is condition-dependent: adaptive position error improved at C1–C4 and was slightly worse at C0. Its quality signals are synthetic, not actual radar/thermal measurements.

## 6. What happens when radar becomes stale?

Original observation time is retained. An expired NORMAL snapshot is unavailable at publication; the next decision uses STALE health and UNKNOWN. AGING behavior is deliberately unchanged and can still be NORMAL under the existing model.

## 7. Can dashboard clients change decisions?

No. A single lifespan-owned runtime advances the pipeline; REST/WebSocket observers read cached snapshots. Controlled zero/one/multiple-observer scenarios produced identical normalized logical traces.

## 8. What if Pi↔ESP32 communication stops?

The host retires expired pending work and health; the board-neutral receiver tick expires commands without waiting for a new frame. Phase-1 outputs remain zero. We do not claim link loss automatically changes the independent PV-SOE state or that physical watchdog timing is verified.

## 9. How does expiry work with different clocks?

Protocol V2 validates a positive sender duration of at most 500 ms and constructs expiry from receiver-local receipt time. It does not compare absolute Pi and ESP32 epochs. Transport delay and actual physical timing are not thereby measured.

## 10. How are reboots and old commands handled?

A session combines an injected unique-per-boot identity and a generation incremented for every valid open. Old-session/duplicate traffic is rejected. The physical board still needs a reviewed fresh-identity source and serialized binding.

## 11. Does CRC authenticate the controller?

No. CRC32C detects corruption. Sessions address tested stale-session replay under the identity assumption; neither mechanism is cryptographic peer authentication.

## 12. Can replay change motors?

No. Replay reconstructs an isolated Pipeline and never submits computed commands to live transport. Tests check that replay leaves live sequence, submissions and state unchanged.

## 13. What does replay MATCH prove?

Repeatability of the defined compared decision, health, command and event fields for compatible supplied sessions. It does not prove universal correctness, physical sensor validity or stopping safety.

## 14. What has actually been physically tested for this release?

No physical hardware was accessed or tested in this release pass. Host C execution is not an ESP32 flash or physical USB test. No sensor, motor, encoder, E-stop, K1 or vehicle verification is claimed.

## 15. Is TARK autonomous?

No. It is safety-assistance research with monitoring-only interfaces and permanently disabled Phase-1 outputs. It does not autonomously steer a mine vehicle.

## 16. Why LD2450?

It is the project's selected low-cost prototype radar with an implemented documented target-report boundary. That choice is not a claim of industrial suitability, fog range or mine certification; those need separate evaluation.

## 17. What if no obstacle is detected?

A valid empty report and a missing report are different. With no retained usable track, fresh empty input yields STOP/no envelope; missing input yields MISSING/UNKNOWN. An empty report does not instantly erase retained tracks. We do not equate no detection with clear safe space.

## 18. What does NORMAL mean?

The available modeled evidence satisfies the current provisional policy branch. It is not certified safety or motion authorization. Permitted speed and both commands are still zero.

## 19. Is WARN implemented?

It exists in the broader vocabulary and protocol schema but has no executable current PV-SOE branch. State-named simulator aliases are rejected rather than pretending to exercise a WARN policy.

## 20. Is speed measured?

Not in the current production decision model. It assumes zero for stopping calculations; the HMI says measured speed UNAVAILABLE and separately shows commanded permitted speed.

## 21. Does GNSS affect safety control?

GNSS provides observational map context. It does not command motors or change PV-SOE. Browser DEVICE LOCATION is separate from vehicle location. No RTK-fixed or centimeter-accuracy claim is made.

## 22. What do camera, thermal and IMU currently do?

Their software boundaries acquire/validate observations and report health through mocked/tested lifecycles. They are not fused into the current radar decision policy; no physical sample/calibration is claimed.

## 23. What does REAL mean in a record?

It denotes the production source/endpoint contract, not physical verification. Prompt-3 experiments are externally TEST_FIXTURE even where internal normalized reports preserve REAL labels.

## 24. What exactly is tested?

The dated R1 record lists 322 backend and 39 frontend tests, including protocol, replay, integrity and evidence-harness subsets. The supplied bundle verifies 20 scenarios over 150 repetitions, plus negative controls. These counts describe controlled software checks.

## 25. How strong is the stale-data evidence?

Tests reproduce old queued reports, future timestamps, valid-empty/missing distinctions and publication expiry through actual runtime/pipeline paths. That supports the exercised software property, not physical stopping.

## 26. Are the evidence files tamper-proof?

No. Content hashes and semantic verification detect many changes, including tested rehashed decision tampering. Hashes are not signatures and do not prevent a deliberate wholesale replacement of evidence and expectations.

## 27. What remains for the ESP32 board?

Reviewed USB RX/TX, unique boot identity, serialized scheduling/disconnect hooks, SDK integration and physical watchdog binding/testing. app_main truthfully remains unavailable rather than fabricating a hardware implementation.

## 28. Can you build directly from the electrical package?

Not as an energized or fabricated release. It is controlled pre-commissioning design with 27 HOLD/restriction entries. Purchased-part evidence, ratings and independent review must precede any authorized build/energization.

## 29. Is the E-stop software-controlled?

The intended primary NC E-stop/contactor isolation path is independent of Pi/ESP32. GPIO13 auxiliary status is diagnostic only. Physical isolation and coil/driver details remain under HOLD.

## 30. What do encoders measure?

Wheel-response counts through a tested software contract. Without verified geometry, pulses, electrical interface and slip analysis they are not ground-truth vehicle speed.

## 31. Is the public site this release?

Not asserted. A historical public simulation/monitoring URL is recorded. R1 is local, not pushed or deployed; this pass performs no network verification of its current availability or revision.

## 32. What is the proposed differentiation?

Perception evidence constraining permitted operation at the system level. We do not claim radar, EKF, TTC or watchdogs as inventions, nor claim legal novelty.

## 33. What remains next?

Purchased-part verification, electrical HOLD review, board/sensor integration and measured vehicle/braking/degraded-visibility evidence. Any future production policy improvement is separately scoped and must regenerate applicable evidence.

## 34. Does this release mean zero bugs or mine readiness?

No. It freezes a defined software-evidence scope and makes its limits explicit. It is neither a blanket completion claim nor industrial deployment/certification approval.
