# V9 Prompt 2 — GNSS Hardware-Ready Software Report

## Driver audit

The earlier V9 foundation had normalized GNSS location, checksum parser, health checks, simulation and map contracts. It was simulated/contract-ready but had no serial transport, continuous reader, reconnection worker, raw stream diagnostics or hardware probe. It intentionally had no real device started by default.

## Added real serial architecture

`app.gnss_driver` is the dedicated read-only boundary: optional `pyserial` transport → byte reader → bounded CR/LF framing → checksum decoder → RMC/GGA aggregation → existing `GnssLocationService`. It is one daemon thread with clean close, bounded retry, partial/multiple-line support, corrupt/oversized-input rejection and bounded raw capture. Device discovery reports candidates but leaves every candidate `UNVERIFIED`; no arbitrary port is selected.

`app.gnss_probe` is the hardware-arrival CLI. It prints candidate paths, configured selection, identity state, raw/RMC/GGA/checksum counters, timing, reconnect count and normalized fix state. It is read-only and prints `TRACTION DISABLED — PHASE 1`.

## Timing and aggregation

`GnssFix` now keeps optional `measurement_time_utc` separate from `received_monotonic_ns`; legacy `timestamp_ns` remains a compatible receive-time field. Freshness uses local monotonic receive time. RMC contributes position/speed/heading/UTC date-time; GGA contributes altitude/satellites/fix quality. Compatible sentences are merged only when coordinate and receive-window checks agree; otherwise missing fields remain absent.

## Configuration

`.env.example` documents device path, baud, serial timeout, reconnect interval, bounded raw diagnostics, maximum line length and existing health thresholds. `pyserial` is an optional `gnss` dependency, so ordinary simulation installs do not need physical serial support.

## Three reviews

1. **Functional:** mocked partial/multiple/corrupt input, aggregation, UTC handling, raw capture and probe no-device path checked.
2. **Failure/reconnect:** open failure, bounded retry, duplicate-start prevention, close and oversized-line checks passed.
3. **Safety/resources:** `gnss`, `gnss_driver` and `gnss_probe` contain no controller, ESP32, motor, PV-SOE, verification or E-stop imports. Reader uses one thread; raw in-memory history is bounded; disk capture is opt-in.

## Verification

- Backend: **39 passed**.
- Frontend: **17 passed**.
- TypeScript type check: passed.
- Vite production build: passed.

## Physical work remaining

The LC29H(AA) is not connected, identified, streamed, configured or verified. The actual baud, NMEA output, USB identity, antenna performance, receiver accuracy and disconnect/reconnect behaviour still require controlled physical bring-up. Prompt 3 should add a verified-device identity policy only after capturing real read-only probe output; it must not infer LC29H(AA) identity from a port name.
