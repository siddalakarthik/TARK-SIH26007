# MLX90640 Thermal Integration

## Status

The MLX90640 32×24 frame contract and dormant I²C boundary are **implemented** with deterministic simulation fixtures. No real thermal device, temperature, optics, field of view or calibration has been verified.

## Validity and health

A frame is accepted only when it has exactly 768 finite values. The adapter reports dimensions, sequence, source, state, freshness and reason; API responses calculate min/max/mean only from an accepted frame. Invalid or stale frames are reported as such rather than replaced with a blank image. Thermal health describes acquisition only, never scene safety or object/person classification.

## Bring-up

Keep traction disabled. Identify the real I²C address/bus, record documented identity evidence, then permit a real worker through the shared `I2cTransport`. Verify 32×24 dimensions and update rate, check temperature sanity, then test stale/dropout recovery and mounting/FOV. Install `.[thermal]` only for a real hardware host. Breakout-specific behavior remains physical verification work.
