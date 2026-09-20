# V9 Prompt 5 — I²C Sensor Hardware-Ready Report

## Architecture

One optional `I2cTransport` now owns selected Linux bus/address open, close, byte/block read/write, bounded errors and clean release. One `I2cSensorWorker` supplies bounded polling/retry and duplicate-worker prevention. Both BNO055 and MLX90640 adapters retain their normalized contracts and may start a real worker only after explicit identity verification evidence is recorded.

## Identity policy

`DeviceIdentity` supports transport location, manufacturer/product, chip/revision, serial and USB VID/PID fields. Every I²C, camera and GNSS configuration begins `UNVERIFIED`; paths and addresses identify candidates only. No C920s, LC29H(AA), BNO055 or MLX90640 values were invented.

## Readiness and maturity

- Software driver/transport: **implemented; functional in mocked tests**.
- Simulation/replay: retains separate source semantics.
- Physical BNO055/MLX90640/camera/GNSS: **not physically verified**.

## Safety and next step

The I²C adapters are observation-only and have no controller, ESP32, motor, PV-SOE, verification or E-stop dependency. The next prompt should begin only after captured physical discovery and documented identity evidence are available, then configure read-only real adapters with traction still disabled.

## Verification

| Check | Result |
| --- | --- |
| Full backend suite | 46 passed |
| Focused I²C/IMU/thermal/camera/GNSS-driver checks | 10 passed |
| Frontend suite | 17 passed |
| TypeScript type check | passed |
| Vite production build | passed |

The final identity audit found no hard-coded `/dev/video0`, `/dev/ttyUSB0`, BNO055 or MLX90640 address assumption. The authority audit found no sensor/map/routing path into controller, ESP32 command generation, motor output, PV-SOE, verification or E-stop code.
