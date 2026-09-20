# BNO055 IMU Integration

## Status

The BNO055 software contract and dormant I²C boundary are **implemented** and unit-tested with simulation fixtures. They are not functionally verified against hardware, validated for vehicle dynamics, calibrated, or physically verified.

## Contract and states

The normalized sample carries a monotonic receive timestamp, sequence, quaternion, derived yaw convenience, linear acceleration in m/s², angular velocity in rad/s, optional temperature, calibration state, quality and reason. Health and calibration remain separate. Possible states include `NOT_CONNECTED`, `DISCOVERED`, `INITIALIZING`, `UNCALIBRATED`, `CALIBRATING`, `ONLINE`, `STALE`, `ERROR` and `DISABLED`; a responding I²C device alone is not `ONLINE`.

## Configuration and bring-up

Set only an evidence-backed `TARK_IMU_I2C_BUS` and `TARK_IMU_I2C_ADDRESS`. The shared `I2cTransport` keeps raw bus operations behind one selected bus/address, while the adapter refuses to start a real worker before recorded identity evidence marks the candidate verified. Keep traction disabled, identify the actual device, start read-only diagnostics, verify update rate and units, record mounting orientation, then calibrate on the installed vehicle. Do not assume a breakout revision or use undocumented register assumptions. Install `.[imu]` only on a hardware host needing the optional documented library.

## Safety

IMU samples are observation data. They do not command motors, alter PV-SOE, bypass ESP32, or change E-stop behaviour. A calibrated sensor is not a safety verdict.
