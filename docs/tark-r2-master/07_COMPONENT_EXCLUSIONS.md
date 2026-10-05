# TARK R2 — component exclusions

Revision M1 • No optional category. These decisions apply to this demonstrator, not every eventual mine deployment.

| Component | Decision | Engineering reason |
|---|---|---|
| LiDAR | EXCLUDE | Additional geometry/calibration cost without establishing usable range in the intended aerosol domain; characterize the selected radar first |
| Ultrasonic | EXCLUDE | Short-range evidence overlaps the restricted bench domain and does not answer long haul-road observability |
| Second premium radar | EXCLUDE | Doubles integration/calibration work before one front radar is characterized |
| Rear radar | EXCLUDE | Reverse movement is outside the premium perception demonstration; do not imply rear coverage |
| Side radar | EXCLUDE | Blind-curve cooperative warning comes from participating-node location, not an invented side-looking coverage zone |
| Depth camera | EXCLUDE | Visible/active-optical depth has its own poor-visibility limitations and adds calibration/data bandwidth |
| Stereo camera | EXCLUDE | Baseline and texture dependence add another unproven range channel; radar is the selected geometry source |
| UWB | EXCLUDE | Outdoor multi-band RTK/base architecture answers this experiment; no indoor anchor network is required |
| LoRa | EXCLUDE | Local test-area Wi-Fi carries corrections and telemetry; no long-range deployment requirement is demonstrated here |
| LTE/5G modem | EXCLUDE | Internet is not required for local operation; consumer cellular adds recurring cost and coverage dependencies |
| C-V2X hardware | EXCLUDE | Research cooperative messages use local IP transport; production V2X remains a later deployment decision |
| Humidity sensor | EXCLUDE | Relative humidity is not a calibrated visibility or usable-detection-distance measurement |
| Dedicated commercial visibility sensor | EXCLUDE | Use a bounded optical-contrast reference experiment; do not call it a calibrated meteorological visibility instrument |
| Higher-resolution thermal core | EXCLUDE | 160 x 120 is enough to characterize complementary thermal contrast; additional resolution would consume protection/test budget |
| Second Jetson | EXCLUDE | Pi 3B+ is adequate for second-node GNSS/telemetry intent; no second-node AI workload selected |
| Custom PCB | EXCLUDE | Development boards and protected harnesses preserve inspectability while interfaces are characterized |
| Premium drivetrain | EXCLUDE | Retain the owned TT/L298N model subject to electrical/mechanical qualification; it represents an assistance chain, not dumper dynamics |
| Industrial PLC | EXCLUDE | A PLC would not make the overall unvalidated demonstrator a certified safety system |
| Haptic alert | EXCLUDE | Display plus simple buzzer provides two modalities; no validated haptic warning requirement yet |
| Cosmetic beacon | EXCLUDE | State text/symbol/color on the display plus buzzer is sufficient for the low-cost local HMI |
| DCA1000/raw-ADC radar capture board | EXCLUDE | The selected experiment uses documented processed UART outputs; raw-ADC algorithm research is a different workload |
| Additional GNSS receiver for dual-antenna heading | EXCLUDE | Three receivers serve two rovers and a base; IMU aids short-term orientation, with heading limitations disclosed |
| Unidentified webcam as primary RGB | EXCLUDE | Retain it only for reference/bench observation; primary research optics must be identifiable |
| Owned LD2450 as premium rear/safety radar | EXCLUDE | Bench/reference only; no inferred HEMM coverage or undocumented decoder claim |
| Bare JQC-3FC/T73 relay as rated cutoff | EXCLUDE | Contact pinout and assembled interruption performance are not verified |
| Existing unrated red switch as traction cutoff | EXCLUDE | Unknown DC interruption rating cannot support that claim |
| Damaged LM2596 | EXCLUDE PERMANENTLY | Damaged conversion hardware must never be reused |

Included additions are precisely the front sensor stack, two-rover/base positioning, IMU, wheel-sensing technology, one edge computer, HMI/buzzer, local network, recording, protected power categories and experiment fixtures. Nothing in this file silently adds another sensor to the BOM.
