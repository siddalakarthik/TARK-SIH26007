# Protocol implementation

The current, explicitly approved **V2** contract is in
[Protocol V2](ESP32_PROTOCOL_V2.md). V1 frames are
rejected. There is one Python codec/client and one firmware codec/service;
shared vectors cover both. Envelope framing remains COBS + CRC32C + canonical
CBOR. Sessions, strict response correlation, finite numeric compatibility and
bounded receiver-local lifetime replace the earlier incomplete V1 semantics.

The Pi transport has bounded TX/RX state, partial-write handling, per-command
deadlines and reconnect-generation flushing. Communication health depends on
validated current-session exchanges, not a worker thread. The default endpoint
is explicitly SIMULATION. Firmware response source REAL denotes the endpoint
contract, not proven physical operation. Applied outputs remain permanently zero.

The board-neutral C service supports receive, disconnect and independent
periodic supervision/status hooks. Physical USB choice, fresh boot-identity
binding, scheduler integration, firmware flashing and physical watchdog behavior
remain pending reviewed board documentation/bring-up. No clock synchronization
is assumed. CRC/session handling is not cryptographic peer authentication.

See [Prompt-2 correction evidence](PROTOCOL_FIRMWARE_REPLAY_CORRECTION_REPORT.md)
for test gates and the exact hardware/software distinction.
