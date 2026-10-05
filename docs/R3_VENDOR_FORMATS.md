# R3 vendor-format evidence and intentional limits

Reviewed 4 October 2026. None of these sources proves the identity, firmware,
configuration or performance of a purchased device. All new test samples are
synthetic, not captures from physical R3 equipment.

## TI IWR6843

[TI mmWave SDK](https://www.ti.com/tool/MMWAVE-SDK) and TI's
[Understanding OOB output](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/1023/6153.understand_5F00_OOB_5F00_output.pdf)
describe Cartesian detected-point payloads as four little-endian floats:
x, y, z in metres and radial Doppler in m/s. `ti_cartesian_points` implements
that payload ONLY, with explicit count/length and finite-number validation.
It does not reinterpret Doppler as a full velocity vector.

The explanatory PDF is not an adequate universal packet-header authority: its
header size description and enumerated field lengths conflict, and its stats
TLV descriptions are not consistently numbered. AreaScanner polar output and
other TI firmware are not interchangeable. G04 therefore remains OPEN for
exact delivered SDK/demo version, flashed binary hash, profile/configuration,
header definition, TLV IDs and captured reference packets. No guessed complete
TI UART stream decoder was added. xWRL-family documentation is not transferred
to IWR6843 merely because both are TI products.

## CEVA BNO085 / SH-2

[SH-2 reference manual](https://www.ceva-ip.com/wp-content/uploads/SH-2-Reference-Manual.pdf)
and [CEVA's SH-2 decoding source](https://github.com/ceva-dsp/sh2/blob/main/sh2_SensorValue.c)
support the implemented payload subset: report 1 accelerometer and report 4
linear acceleration use Q8, report 2 gyro uses Q9, report 5 rotation-vector
quaternion uses Q14. Axis values begin after the four-byte report header.

`sh2_sensor_report` accepts complete report payloads **after SHTP reassembly**.
It does not invent a timestamp epoch from the payload. A timestamp from the
vendor SH-2 time-processing boundary is optional; unavailable remains null.
SPI/interrupt/reset HAL, negotiated report rates, SHTP reassembly and the chosen
embedded vendor-library build still need integration against the reviewed board
pinout. Existing BNO055 code is not reused as a BNO085 driver.

## LG290P / standard NMEA

The existing checksum-validating TARK NMEA parser is reused at an explicit
LG290P normalization boundary. GGA quality codes are preserved as standalone,
DGPS, FLOAT or FIXED where reported. HDOP is not converted to metre accuracy.
No fix means no valid coordinates; stationary course is unavailable, not body
heading. NMEA output alone does not verify a Quectel model or Waveshare board.

Receiver-specific setup/identity commands, base/rover RTCM routing and PPS
electrical/time binding are not implemented by this NMEA wrapper. Their reviewed
configuration and real capture evidence are required before commissioning.

## UVC / Lepton / PureThermal

The current code implements strict normalized frame metadata, image dimensions,
pixel format, media reference/hash, optional PTS/exposure and timestamp semantics.
Lepton 3.5 is a 160×120 image contract; documented telemetry rows must be removed
by the selected driver, never guessed. FFC state is explicit. Temperature values
are refused unless the caller identifies verified TLinear radiometry and supplies
the complete grid. No raw-count-to-temperature formula is invented.

The existing generic UVC capture boundary remains available for legacy cameras.
PureThermal firmware mode negotiation, FFC/radiometric metadata extraction and
actual media retention require device/profile-specific binding. Synthetic fixture
image metadata does NOT contain a live image. Its all-zero hash is explicitly a
synthetic placeholder, not a hash of captured media; raw inference replay refuses
to claim reconstruction from it.

## Hailo

[Hailo's Raspberry Pi examples](https://github.com/hailo-ai/hailo-rpi5-examples)
demonstrate the HailoRT `InferVStreams.infer` dictionary boundary.
`HailoProvider.bind` verifies a selected HEF hash and invokes a caller-owned SDK
context with explicitly supplied model-specific preprocessing/postprocessing.
It neither discovers PCIe devices nor guesses a model's tensor semantics.
The default runtime is UNAVAILABLE. No neural model is shipped or accuracy
claimed. Context lifecycle, supported HailoRT version, HEF/model selection and
Pi-specific measurements remain release gates.

## Reproduction

`backend/tests/test_r3_evidence.py` exercises TI/SH-2 payloads, malformed packets,
strict normalized contracts, clocks, provenance and cooperative faults.
`backend/tests/test_r3_runtime.py` exercises the synthetic eight-source manifest
and a mocked Hailo SDK context. These tests are software evidence only.
