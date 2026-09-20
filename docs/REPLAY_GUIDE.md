# Replay Guide

The replay engine accepts deterministic `SIM1` fixtures and persisted normalized `OBSERVATION_TICK_V1` recordings. A completed session can be selected through `/api/v1/replay/sessions/{id}/timeline`; the response is explicitly marked `REPLAY`, has ordered item positions and duration bounds, and is rejected when its configuration hash differs from the active configuration. The HMI can load, seek, step forward/backward, play, pause and reset this isolated timeline. Replay never modifies live telemetry, ESP32 transport, traction, or motor authority.

Only normalized observation ticks are replayable. Raw LD2450 vendor bytes can be retained as `RAW_FRAME_V1` diagnostic evidence, but they are not decoded or converted to replay observations without a reviewed vendor frame specification. Empty, malformed, corrupt, out-of-order, or configuration-incompatible recordings are rejected rather than represented as live or simulated data.

Replay is isolated from ESP32 transport and cannot create a physical command. A recorded replay match establishes software repeatability for the supplied input and configuration; it does not validate real hardware, stopping behavior or safe speed.
