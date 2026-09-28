# TARK claim/evidence matrix

Release: **TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1**.
Software source: `bf87304ab2080452d5446fb4b6bbfcb945cf74ea`.

60 distinct claim areas: 37 KEPT, 22 CORRECTED,
1 HISTORICAL. 10 rows remain HOLD / VERIFY or
PHYSICAL-VALIDATION-PENDING (a maturity subset, not additional audited claims).
Disposition describes the presentation/document change, not a software edit.
External artifacts and non-current claims are identified by the reference inventory.

Every row applies to this R1 unless explicitly marked historical/research/future.
SOFTWARE-VERIFIED means the cited controlled software tests, never physical validation.
A missing production feature is not concealed by an aspirational architecture diagram.

## C01 — LD2450 decoder

- **Claim:** Bounded published target-report decoder and normalized conversion exist.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [parser.py](../backend/app/sensors/ld2450/parser.py); [test_ld2450_parser.py](../backend/tests/test_ld2450_parser.py); [test_ld2450_adapter.py](../backend/tests/test_ld2450_adapter.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Three target slots only; no purchased-device capture or configuration-frame support.
- **Allowed presentation wording:** “Documented target reports are decoded and software-tested.”
- **Forbidden / overstated wording:** “The physical radar is validated.”

## C02 — Radar normalized observations

- **Claim:** Adapter feeds normalized report batches; SIM1 remains separate.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [parser.py](../backend/app/sensors/ld2450/parser.py); [test_ld2450_parser.py](../backend/tests/test_ld2450_parser.py); [test_ld2450_adapter.py](../backend/tests/test_ld2450_adapter.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Prompt-3 injects reports, not physical serial bytes.
- **Allowed presentation wording:** “One normalized perception boundary serves reports and fixtures.”
- **Forbidden / overstated wording:** “Prompt-3 verifies real radar reception.”

## C03 — Radar tracking

- **Claim:** Tracks retain updates by radar candidate/slot identifier.
- **Maturity:** IMPLEMENTED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No EKF, association across changing physical identities or probabilistic filter.
- **Allowed presentation wording:** “Slot-based temporal tracking is implemented.”
- **Forbidden / overstated wording:** “Robust multi-object EKF tracking runs in production.”

## C04 — Target identity

- **Claim:** Track key is ld2450:candidate_id.
- **Maturity:** IMPLEMENTED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Module slot identity is not persistent physical-object identity.
- **Allowed presentation wording:** “Radar slot IDs label the current tracks.”
- **Forbidden / overstated wording:** “The same person is identified across slot changes.”

## C05 — Sensor freshness

- **Claim:** Source timestamps determine FRESH/AGING/STALE/MISSING.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** AGING can retain NORMAL under the existing policy.
- **Allowed presentation wording:** “Freshness boundaries are regression-tested.”
- **Forbidden / overstated wording:** “Every aging observation produces WARN.”

## C06 — Future timestamps

- **Claim:** Invalid/future report or detection timestamp invalidates evidence.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Strict rejection; no invented clock tolerance.
- **Allowed presentation wording:** “Future evidence is rejected in controlled tests.”
- **Forbidden / overstated wording:** “All sensor clock systems are physically synchronized.”

## C07 — Stale evidence

- **Claim:** Old queued evidence is not restamped; expired NORMAL is unavailable to observers.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Publication unavailability and next-tick UNKNOWN are distinct.
- **Allowed presentation wording:** “Production-path stale handling is covered by EV-03/04.”
- **Forbidden / overstated wording:** “A stale sensor has proven physical braking response.”

## C08 — Runtime owner

- **Claim:** One lifespan-owned runtime advances decisions independently of readers.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [runtime.py](../backend/app/services/runtime.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Single process/worker scope; not distributed scheduling.
- **Allowed presentation wording:** “The runtime, not API polling, owns decisions.”
- **Forbidden / overstated wording:** “Arbitrary multi-worker deployment preserves single ownership.”

## C09 — Observer independence

- **Claim:** EV-16/17/18 produce identical normalized logical traces.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Controlled ASGI observers; not every schedule or browser performance.
- **Allowed presentation wording:** “REST/WebSocket observer count did not alter these scenario traces.”
- **Forbidden / overstated wording:** “Unlimited clients cannot affect any timing.”

## C10 — PV-SOE production

- **Claim:** Nearest active range minus stored uncertainty is compared with parameterized stopping requirement.
- **Maturity:** IMPLEMENTED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** D_env=D_base=D_effective; provisional, not calibrated perception extent/free space.
- **Allowed presentation wording:** “PV-SOE currently uses a simplified provisional software model.”
- **Forbidden / overstated wording:** “A calibrated safe operating envelope is verified.”

## C11 — Stopping calculation

- **Claim:** Stopping helper uses v*t + v*v/(2*a) + margin with validated numeric configuration.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Parameters are provisional and production v=0.
- **Allowed presentation wording:** “Parameterized stopping calculation is software-tested.”
- **Forbidden / overstated wording:** “Measured vehicle stopping performance is proven.”

## C12 — Vehicle speed input

- **Claim:** Production decision assumes zero; HMI measured speed is UNAVAILABLE.
- **Maturity:** IMPLEMENTED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [DriverView.tsx](../frontend/src/features/dashboard/DriverView.tsx); [OperationsApp.tsx](../frontend/src/app/OperationsApp.tsx); [DriverView.integrity.test.tsx](../frontend/src/features/dashboard/DriverView.integrity.test.tsx).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Zero is a model input, not a stationary-vehicle measurement.
- **Allowed presentation wording:** “Measured vehicle speed is unavailable; commanded permitted speed is zero.”
- **Forbidden / overstated wording:** “Vehicle speed is measured as 0.00 m/s.”

## C13 — TTC helper

- **Claim:** Closing/nonclosing and stale-track TTC helper exists.
- **Maturity:** IMPLEMENTED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Helper is not invoked by production decision policy; no comprehensive TTC safety claim.
- **Allowed presentation wording:** “A TTC helper exists outside the current decision policy.”
- **Forbidden / overstated wording:** “TTC currently governs collision intervention.”

## C14 — TTC production integration

- **Claim:** Production decision does not call the TTC helper; UI says NOT COMPUTED.
- **Maturity:** NOT IN CURRENT SCOPE. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No threshold policy added in this release.
- **Allowed presentation wording:** “TTC is not computed in the production decision path.”
- **Forbidden / overstated wording:** “The HMI displays measured live TTC.”

## C15 — WARN semantics

- **Claim:** WARN is a vocabulary/protocol value, not an executable current PV-SOE branch.
- **Maturity:** NOT IN CURRENT SCOPE. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Research-state policies do not define production thresholds.
- **Allowed presentation wording:** “Current production outputs NORMAL, RESTRICT, STOP or UNKNOWN.”
- **Forbidden / overstated wording:** “Production WARN policy is fully implemented.”

## C16 — RGB acquisition

- **Claim:** Configured UVC lifecycle, frame/health contracts and failure paths are mocked/tested.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [camera.py](../backend/app/camera.py); [test_camera.py](../backend/tests/test_camera.py); [test_runtime_adapter_lifecycle.py](../backend/tests/test_runtime_adapter_lifecycle.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No real camera frame or optical performance verified.
- **Allowed presentation wording:** “RGB acquisition software has mocked lifecycle coverage.”
- **Forbidden / overstated wording:** “Physical camera performance is verified.”

## C17 — Thermal acquisition

- **Claim:** Concrete library boundary and 768-finite-value validation have mocked coverage.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [thermal.py](../backend/app/thermal.py); [test_i2c_runtime_bootstrap.py](../backend/tests/test_i2c_runtime_bootstrap.py); [test_sensor_acquisition.py](../backend/tests/test_sensor_acquisition.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No measured temperatures, breakout compatibility or calibration.
- **Allowed presentation wording:** “Thermal acquisition/health software is exercised with fixtures.”
- **Forbidden / overstated wording:** “Thermal detects people reliably in mine fog.”

## C18 — IMU acquisition

- **Claim:** Concrete library boundary, normalized validation and lifecycle are mocked/tested.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [imu.py](../backend/app/imu.py); [test_i2c_runtime_bootstrap.py](../backend/tests/test_i2c_runtime_bootstrap.py); [test_sensor_acquisition.py](../backend/tests/test_sensor_acquisition.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No mounted calibration/dynamics or purchased-bus verification.
- **Allowed presentation wording:** “BNO055 acquisition software has fixture-based evidence.”
- **Forbidden / overstated wording:** “Vehicle orientation is physically calibrated.”

## C19 — Multisensor fusion

- **Claim:** RGB/thermal/IMU observations are not fused into the radar decision path.
- **Maturity:** NOT IN CURRENT SCOPE. **Disposition:** CORRECTED.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Separate interfaces do not establish fusion.
- **Allowed presentation wording:** “Complementary sensing is a system concept; production policy is radar-based.”
- **Forbidden / overstated wording:** “Adaptive radar/thermal/RGB fusion is deployed.”

## C20 — EKF research

- **Claim:** Supplied Simulation 2 archive contains a fixed/adaptive EKF study.
- **Maturity:** RESEARCH / SIMULATION STUDY. **Disposition:** KEPT.
- **Evidence source / source path:** [README.md](../release/references/README.md).
- **Evidence type:** Archived numerical study/source inspection (not rerun). **Release applicability:** Separate study; not production integration.
- **Known limitation:** Separate archived study, not rerun or integrated during Prompt 4.
- **Allowed presentation wording:** “We studied fixed versus adaptive covariance under synthetic conditions.”
- **Forbidden / overstated wording:** “The production TARK pipeline runs an EKF.”

## C21 — Adaptive covariance research

- **Claim:** Archived results are mixed/condition-dependent with synthetic quality signals.
- **Maturity:** RESEARCH / SIMULATION STUDY. **Disposition:** CORRECTED.
- **Evidence source / source path:** [README.md](../release/references/README.md).
- **Evidence type:** Archived numerical study/source inspection (not rerun). **Release applicability:** Separate study; not production integration.
- **Known limitation:** Quality is not measured from purchased LD2450/MLX90640 hardware.
- **Allowed presentation wording:** “Adaptive covariance improved some synthetic conditions, not all.”
- **Forbidden / overstated wording:** “Adaptive fusion universally outperforms fixed fusion in fog.”

## C22 — GNSS

- **Claim:** Reader/callback/location/source gating and checksum parsing have mocked tests.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [gnss_driver.py](../backend/app/gnss_driver.py); [location.py](../backend/app/location.py); [test_gnss_driver.py](../backend/tests/test_gnss_driver.py); [test_system.py](../backend/tests/test_system.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No receiver identity/fix/accuracy claim; aggregation limits remain.
- **Allowed presentation wording:** “GNSS is an observational location software boundary.”
- **Forbidden / overstated wording:** “LC29H hardware is verified or centimeter accurate.”

## C23 — Map

- **Claim:** Map lifecycle, invalid-fix clearing and heading availability have frontend tests.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [MapView.tsx](../frontend/src/MapView.tsx); [MapView.lifecycle.test.tsx](../frontend/src/MapView.lifecycle.test.tsx).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Provider availability/deployed version not rechecked; map is advisory.
- **Allowed presentation wording:** “Vehicle GNSS, India overview and local radar scopes are distinct.”
- **Forbidden / overstated wording:** “A map marker proves a real vehicle or validated route.”

## C24 — Browser location

- **Claim:** Device location remains separate from vehicle location.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [MapView.tsx](../frontend/src/MapView.tsx); [MapView.lifecycle.test.tsx](../frontend/src/MapView.lifecycle.test.tsx).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Browser permission/location accuracy are not GNSS commissioning.
- **Allowed presentation wording:** “DEVICE LOCATION never grants vehicle or motion authority.”
- **Forbidden / overstated wording:** “Phone location is vehicle GNSS evidence.”

## C25 — Event persistence

- **Claim:** SQLite event persistence is implemented and storage failure exercised.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [store.py](../backend/app/logging/store.py); [store.py](../backend/app/replay/store.py); [test_recording_replay.py](../backend/tests/test_recording_replay.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Random IDs and bounded retention are not signed forensic provenance.
- **Allowed presentation wording:** “Persisted events support software inspection.”
- **Forbidden / overstated wording:** “Logs prove every real-world hazard was detected.”

## C26 — Recording

- **Claim:** Format 2 preserves ordered report batches, empty reports and initial checkpoint.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [store.py](../backend/app/logging/store.py); [store.py](../backend/app/replay/store.py); [test_recording_replay.py](../backend/tests/test_recording_replay.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Legacy recordings remain catalogued but nondeterministic.
- **Allowed presentation wording:** “Current recording schema preserves the tested input semantics.”
- **Forbidden / overstated wording:** “All historical recordings are deterministically verified.”

## C27 — Replay

- **Claim:** Full bounded session verification and isolated playback are tested.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [engine.py](../backend/app/replay/engine.py); [test_replay_correctness.py](../backend/tests/test_replay_correctness.py); [REPLAY_GUIDE.md](REPLAY_GUIDE.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** MATCH is scoped to compared fields and supplied scenarios; max 50,000 records.
- **Allowed presentation wording:** “Defined controlled sessions replayed deterministically.”
- **Forbidden / overstated wording:** “Replay proves universal algorithm correctness.”

## C28 — Protocol version

- **Claim:** Protocol V2 is authoritative and rejects legacy V1.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [ESP32_PROTOCOL_V2.md](ESP32_PROTOCOL_V2.md); [protocol.py](../backend/app/communication/esp32/protocol.py); [test_protocol_correctness.py](../backend/tests/test_protocol_correctness.py); [protocol_vectors.json](../protocol_vectors.json).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Both peers require coordinated version; no auto-detected fallback.
- **Allowed presentation wording:** “Protocol V2 uses explicit sessions and receiver-local expiry.”
- **Forbidden / overstated wording:** “V1 remains the current release protocol.”

## C29 — Pi protocol client

- **Claim:** COBS/CRC32C/canonical CBOR and response correlation use bounded state.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [ESP32_PROTOCOL_V2.md](ESP32_PROTOCOL_V2.md); [protocol.py](../backend/app/communication/esp32/protocol.py); [test_protocol_correctness.py](../backend/tests/test_protocol_correctness.py); [protocol_vectors.json](../protocol_vectors.json).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Not cryptographic authentication or measured network latency.
- **Allowed presentation wording:** “Malformed, late and wrong-session feedback cannot renew tested health.”
- **Forbidden / overstated wording:** “CRC authenticates a trusted physical controller.”

## C30 — Firmware parser

- **Claim:** C parser/encoder interoperate with shared Python vectors.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [service.c](../firmware/esp32/main/protocol/service.c); [task7b_host_test.c](../firmware/esp32/tests/task7b_host_test.c); [test_protocol_correctness.py](../backend/tests/test_protocol_correctness.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Host compilation/run is not ESP-IDF board build or flash.
- **Allowed presentation wording:** “Fresh strict C host interoperability passes.”
- **Forbidden / overstated wording:** “The ESP32 was flashed and USB verified.”

## C31 — Firmware supervisor

- **Claim:** Independent periodic tick supervises receiver-local expiry and emits STATUS.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [service.c](../firmware/esp32/main/protocol/service.c); [task7b_host_test.c](../firmware/esp32/tests/task7b_host_test.c); [test_protocol_correctness.py](../backend/tests/test_protocol_correctness.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Physical scheduling and watchdog binding remain pending.
- **Allowed presentation wording:** “Board-neutral supervision is host-tested even without incoming frames.”
- **Forbidden / overstated wording:** “A physical watchdog has been verified.”

## C32 — Physical ESP32 binding

- **Claim:** Entrypoint explicitly remains UNAVAILABLE_HARDWARE_BINDING_PENDING.
- **Maturity:** HOLD / VERIFY. **Disposition:** CORRECTED.
- **Evidence source / source path:** [app_main.c](../firmware/esp32/main/app_main.c); [KNOWN_LIMITATIONS.md](../firmware/esp32/KNOWN_LIMITATIONS.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** Reviewed USB RX/TX, boot identity, serialized scheduling/disconnect are still needed.
- **Allowed presentation wording:** “The portable software boundary exists; board binding is pending.”
- **Forbidden / overstated wording:** “Plugging in any board completes the software binding.”

## C33 — Physical watchdog

- **Claim:** No actual watchdog registration/reset/timing evidence is supplied.
- **Maturity:** PHYSICAL-VALIDATION-PENDING. **Disposition:** CORRECTED.
- **Evidence source / source path:** [app_main.c](../firmware/esp32/main/app_main.c); [KNOWN_LIMITATIONS.md](../firmware/esp32/KNOWN_LIMITATIONS.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** Board-specific integration and physical test are future gated work.
- **Allowed presentation wording:** “Watchdog architecture is designed; physical binding/verification pending.”
- **Forbidden / overstated wording:** “Hardware watchdog behavior is proven by host tests.”

## C34 — Encoder software

- **Claim:** Timestamped count contract, optional wrap/jump and fault states are tested.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [encoder_contract.py](../backend/app/hardware/encoder_contract.py); [test_encoder_contract.py](../backend/tests/test_encoder_contract.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No assumed counts/revolution, ground speed or real pulses.
- **Allowed presentation wording:** “Encoder software reports wheel response contracts.”
- **Forbidden / overstated wording:** “Encoder counts are ground-truth vehicle speed.”

## C35 — Encoder wiring

- **Claim:** GPIO4/5 left and GPIO6/7 right mapping is intended design.
- **Maturity:** HOLD / VERIFY. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** H07/H08 supply/output interface and purchased variant unresolved.
- **Allowed presentation wording:** “Encoder mapping is controlled; VCC/interface are HOLD / VERIFY.”
- **Forbidden / overstated wording:** “Encoder supply voltage is established.”

## C36 — MDD10A software

- **Claim:** Simulation and disabled C motor boundary preserve zero applied outputs.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [motor_driver.c](../firmware/esp32/main/hardware/motor_driver.c); [simulators.py](../backend/app/hardware/simulators.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No physical PWM enable/brake/coast behavior inferred.
- **Allowed presentation wording:** “MDD10A software interface is disabled and software-tested.”
- **Forbidden / overstated wording:** “Physical MDD10A output is operating.”

## C37 — MDD10A physical operation

- **Claim:** Electrical target/mapping exist; powered operation is not evidenced.
- **Maturity:** PHYSICAL-VALIDATION-PENDING. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** Exact board, levels, load and motor behavior require review.
- **Allowed presentation wording:** “MDD10A operation awaits controlled physical commissioning.”
- **Forbidden / overstated wording:** “Motor operation has been validated.”

## C38 — E-stop architecture

- **Claim:** Physical NC E-stop/coil/contactor is independent of software.
- **Maturity:** DESIGNED. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** GPIO13 auxiliary status is diagnostic only.
- **Allowed presentation wording:** “Independent physical isolation is the intended electrical design.”
- **Forbidden / overstated wording:** “Software STATUS replaces physical E-stop.”

## C39 — E-stop physical test

- **Claim:** No actual E-stop interruption/isolation test evidence.
- **Maturity:** PHYSICAL-VALIDATION-PENDING. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** Do not energize traction based on these documents.
- **Allowed presentation wording:** “Physical E-stop validation is a next-phase gate.”
- **Forbidden / overstated wording:** “The prototype passes physical emergency-stop validation.”

## C40 — Contactor architecture

- **Claim:** K1 output alone is N-TRACTION12+; linkage is mechanical only.
- **Maturity:** DESIGNED. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Coil terminals are functional labels, not invented purchased terminal numbers.
- **Allowed presentation wording:** “K1 switches the intended traction path in the controlled design.”
- **Forbidden / overstated wording:** “K1 coil/polarity is ready to energize.”

## C41 — K1 physical validation

- **Claim:** K1 driver/return/suppression/contact/coil ratings remain unresolved.
- **Maturity:** HOLD / VERIFY. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** H11–H15 and H13 traction disconnection apply.
- **Allowed presentation wording:** “K1 commissioning stays on HOLD.”
- **Forbidden / overstated wording:** “K1 physically isolates power as tested.”

## C42 — Traction invariant

- **Claim:** All observed live decisions/commands remained zero and DISABLED_PHASE_1.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Nonzero protocol vectors are serialization-only tests.
- **Allowed presentation wording:** “Phase-1 zero-command invariants hold in the controlled suite.”
- **Forbidden / overstated wording:** “A software pass authorizes motion.”

## C43 — Physical vehicle

- **Claim:** A scaled vehicle is intended, not evidenced as built/tested.
- **Maturity:** PHYSICAL-VALIDATION-PENDING. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** No as-built geometry or dynamic performance evidence.
- **Allowed presentation wording:** “Physical vehicle commissioning is a subsequent phase.”
- **Forbidden / overstated wording:** “The as-built mine vehicle is ready.”

## C44 — Measured stopping distance

- **Claim:** No measured stopping dataset accompanies the software baseline.
- **Maturity:** PHYSICAL-VALIDATION-PENDING. **Disposition:** KEPT.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** Software formula and synthetic sweeps are not measurements.
- **Allowed presentation wording:** “Stopping distance must be measured under controlled conditions.”
- **Forbidden / overstated wording:** “TARK has proven braking distance.”

## C45 — Fog testing

- **Claim:** Supplied studies simulate degradation; no controlled physical fog evidence.
- **Maturity:** PHYSICAL-VALIDATION-PENDING. **Disposition:** KEPT.
- **Evidence source / source path:** [README.md](../release/references/README.md).
- **Evidence type:** Archived numerical study/source inspection (not rerun). **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** Synthetic noise/dropout is not fog optics or mine ground truth.
- **Allowed presentation wording:** “Degraded-visibility field validation is planned.”
- **Forbidden / overstated wording:** “TARK is fog tested or field validated.”

## C46 — Public dashboard software

- **Claim:** One monitoring HMI exposes role-aware views and source/availability labels.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [DriverView.tsx](../frontend/src/features/dashboard/DriverView.tsx); [OperationsApp.tsx](../frontend/src/app/OperationsApp.tsx); [DriverView.integrity.test.tsx](../frontend/src/features/dashboard/DriverView.integrity.test.tsx).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** A build/test pass does not verify external deployment.
- **Allowed presentation wording:** “The local HMI visualizes software state without motion authority.”
- **Forbidden / overstated wording:** “LIVE means a physical mine vehicle is connected.”

## C47 — Public deployment record

- **Claim:** Dossier records owner-reported public demo; film records prior genuine UI captures.
- **Maturity:** DEMONSTRATED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [PUBLIC_DEPLOYMENT.md](PUBLIC_DEPLOYMENT.md); [TARK_SIH26007_MASTER_PROJECT_DOSSIER_V1_0.docx](../release/references/dossier/TARK_SIH26007_MASTER_PROJECT_DOSSIER_V1_0.docx).
- **Evidence type:** Historical owner report/capture metadata. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Historical demo evidence only; current availability/commit not checked.
- **Allowed presentation wording:** “Recorded public simulation/monitoring demo; R1 not deployed here.”
- **Forbidden / overstated wording:** “The public site currently runs this local release.”

## C48 — Simulation

- **Claim:** Descriptive input scenarios and TEST_FIXTURE experiments are explicit.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** State-named NORMAL/WARN/etc scenario aliases are rejected.
- **Allowed presentation wording:** “Simulation demonstrates inputs and resulting modeled states.”
- **Forbidden / overstated wording:** “Choosing WARN injects an executable WARN policy.”

## C49 — Evidence harness

- **Claim:** 20 scenarios, 150 repetitions and negative controls verify the supplied bundle.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** KEPT.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Not every input/schedule; hashes are not signatures.
- **Allowed presentation wording:** “Deterministic production-path software evidence is available.”
- **Forbidden / overstated wording:** “This proves zero bugs or physical safety.”

## C50 — Mine certification

- **Claim:** No mine certification is claimed or evidenced.
- **Maturity:** NOT IN CURRENT SCOPE. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Standards references do not establish compliance.
- **Allowed presentation wording:** “Research prototype, not mine-certified.”
- **Forbidden / overstated wording:** “Mine ready or certified safety system.”

## C51 — Autonomous driving

- **Claim:** No production autonomy, autonomous steering or browser motor authority.
- **Maturity:** NOT IN CURRENT SCOPE. **Disposition:** KEPT.
- **Evidence source / source path:** [DriverView.tsx](../frontend/src/features/dashboard/DriverView.tsx); [OperationsApp.tsx](../frontend/src/app/OperationsApp.tsx); [DriverView.integrity.test.tsx](../frontend/src/features/dashboard/DriverView.integrity.test.tsx).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Navigation context is not control.
- **Allowed presentation wording:** “Monitoring and safety-assistance research, not autonomous driving.”
- **Forbidden / overstated wording:** “Autonomous mining vehicle.”

## C52 — Empty versus missing

- **Claim:** Fresh empty report without retained envelope gives STOP; no report gives MISSING/UNKNOWN.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** An empty report does not automatically delete retained tracks.
- **Allowed presentation wording:** “Empty and missing inputs retain their distinct tested meanings.”
- **Forbidden / overstated wording:** “No detected obstacle always means clear safe space.”

## C53 — Communication loss

- **Claim:** Expiry/lost/late feedback retire authority/health in controlled tests.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Last generated PV-SOE state can remain NORMAL while link health fails; no new coupling policy.
- **Allowed presentation wording:** “Communication supervision expires commands; outputs remain zero.”
- **Forbidden / overstated wording:** “Any lost ACK automatically changes PV-SOE to STOP.”

## C54 — Configuration

- **Claim:** Finite settings and positive deceleration are enforced.
- **Maturity:** IMPLEMENTED. **Disposition:** KEPT.
- **Evidence source / source path:** [pipeline.py](../backend/app/services/pipeline.py); [test_software_integrity.py](../backend/tests/test_software_integrity.py).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** UNRELEASED-PHASE1 is an identifier; values are uncalibrated.
- **Allowed presentation wording:** “Configuration has an explicit value fingerprint and provisional parameters.”
- **Forbidden / overstated wording:** “A configuration hash proves safe calibration.”

## C55 — Firmware source REAL

- **Claim:** REAL labels the production endpoint contract, not physical test maturity.
- **Maturity:** IMPLEMENTED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [ESP32_PROTOCOL_V2.md](ESP32_PROTOCOL_V2.md); [protocol.py](../backend/app/communication/esp32/protocol.py); [test_protocol_correctness.py](../backend/tests/test_protocol_correctness.py); [protocol_vectors.json](../protocol_vectors.json).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Host fixtures can preserve internal REAL labels while externally TEST_FIXTURE.
- **Allowed presentation wording:** “REAL source semantics do not mean physically verified.”
- **Forbidden / overstated wording:** “REAL proves an actual ESP32 participated in Prompt 3.”

## C56 — Electrical release

- **Claim:** Five-sheet design and independent export/connectivity checks exist.
- **Maturity:** DESIGNED. **Disposition:** KEPT.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Native CAD ERC NOT RUN; 27 HOLDs; no energization/fabrication release.
- **Allowed presentation wording:** “Controlled pre-commissioning design, not as-built.”
- **Forbidden / overstated wording:** “PCB fabrication-ready or physically verified wiring.”

## C57 — BOM/procurement

- **Claim:** Design references list target parts; purchased variants/ratings are not closed.
- **Maturity:** HOLD / VERIFY. **Disposition:** CORRECTED.
- **Evidence source / source path:** [HOLD_REGISTER.md](../release/references/electrical/HOLD_REGISTER.md); [TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf](../release/references/electrical/TARK_SIH26007_MASTER_ELECTRICAL_SCHEMATIC_SET.pdf).
- **Evidence type:** Controlled electrical design/HOLD record. **Release applicability:** R1 limitation / next-phase gate.
- **Known limitation:** PPT planning prices are historical estimates, not current quotations.
- **Allowed presentation wording:** “BOM procurement and protection ratings require verification.”
- **Forbidden / overstated wording:** “All parts/prices/ratings are final.”

## C58 — Novelty positioning

- **Claim:** Perception evidence constraining operation is the proposed system-level approach.
- **Maturity:** DESIGNED. **Disposition:** KEPT.
- **Evidence source / source path:** [README.md](../release/references/README.md).
- **Evidence type:** Archived numerical study/source inspection (not rerun). **Release applicability:** R1 declared software/design scope.
- **Known limitation:** No patent/legal novelty analysis or world-first evidence.
- **Allowed presentation wording:** “Our proposed perception-aware safety architecture.”
- **Forbidden / overstated wording:** “World-first radar, EKF or collision-prevention invention.”

## C59 — Old software freeze

- **Claim:** The 2026-09-20 freeze is preserved as historical software.
- **Maturity:** IMPLEMENTED. **Disposition:** HISTORICAL.
- **Evidence source / source path:** [TARK_SUPERSESSION_REGISTER.md](TARK_SUPERSESSION_REGISTER.md); [SOFTWARE_FREEZE_BASELINE.md](SOFTWARE_FREEZE_BASELINE.md).
- **Evidence type:** Historical Git/report record. **Release applicability:** Historical only; not current release authority.
- **Known limitation:** Later Prompt-1/2 defects superseded its blanket completion claims.
- **Allowed presentation wording:** “Historical freeze retained; R1 controls present claims.”
- **Forbidden / overstated wording:** “The old freeze proves no software gaps remain.”

## C60 — Current test counts

- **Claim:** Current backend includes 322 tests; frontend 39; subsets are not additive.
- **Maturity:** SOFTWARE-VERIFIED. **Disposition:** CORRECTED.
- **Evidence source / source path:** [evidence_summary.json](../evidence/prompt3/evidence_summary.json); [DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md](DETERMINISTIC_EVIDENCE_HARNESS_REPORT.md).
- **Evidence type:** Source inspection and referenced software regression/evidence. **Release applicability:** R1 declared software/design scope.
- **Known limitation:** Old counts describe old runs, not current release coverage.
- **Allowed presentation wording:** “Use the dated R1 test record for exact counts.”
- **Forbidden / overstated wording:** “97/25 is the current full regression result.”
