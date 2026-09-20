# Read-Only I²C Sensor Hardware Bring-Up

## Universal safety boundary

Keep traction disabled and motor power disconnected. These steps are read-only observation and must not enable motor, ESP32 command, PV-SOE, E-stop, map or route authority.

## BNO055

1. Connect only the intended sensor and confirm the Pi I²C bus electrically.
2. Record the observed bus and address; configuration alone remains `UNVERIFIED`.
3. Capture documented chip/revision identity evidence from the actual module and record it in the integration log.
4. Set the explicit bus/address configuration, initialize with the maintained hardware library, and verify meaningful read-only samples.
5. Record actual sample rate, units, mounting orientation and calibration state.
6. Test stale, disconnect, clean close and bounded reconnect before treating the source as real observation data.

## MLX90640

1. Connect only the intended thermal module, then identify its actual bus/address and preserve discovery evidence.
2. Use the maintained driver/library behind the TARK transport. Do not infer module identity from address alone.
3. Confirm a complete 32×24 frame, finite values, update rate and temperature sanity.
4. Test frame freshness, dropout, clean close and reconnect; record optics/FOV and mounting separately.

## Identity rule

Every configured bus/address, UVC path and serial path begins `UNVERIFIED`. It can become `VERIFIED` only with recorded physical read-only evidence; it is never inferred from `/dev/video0`, `/dev/ttyUSB0`, bus 1 or a customary address.

## Implemented software boundary

The BNO055 adapter consumes the optional library's documented Euler, quaternion, linear-acceleration, gyro, and calibration properties through a strict `read_once` boundary. The MLX90640 adapter consumes its documented 768-value frame operation through a strict `read_once` boundary. Both reject malformed/non-finite data, preserve `NOT_CONNECTED` when no verified device exists, and report bounded worker errors without fabricating samples. These are software interfaces only: actual I²C enumeration, identity, calibration, mounting orientation, frame quality, and live values remain physical verification work.
