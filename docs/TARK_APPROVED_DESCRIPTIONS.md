# Approved TARK descriptions

Authority: [claim/evidence matrix](TARK_CLAIM_EVIDENCE_MATRIX.md).
Word counts use whitespace-separated tokens, excluding headings.

## 25 words

TARK explores perception-aware mine-vehicle safety assistance through tested software, bounded communication and a monitoring dashboard, with traction disabled and physical validation reserved for later phases.

## Short description (60–100 words)

TARK addresses the low-visibility mine-vehicle problem through a perception-aware
operating-envelope concept called PV-SOE. Its Phase-1 software connects radar
observations, freshness checks, provisional stopping logic, bounded Protocol V2
communication and a monitoring dashboard with recording and replay. Deterministic
production-path evidence demonstrates runtime ownership, stale-data handling,
communication supervision and zero-command invariants under controlled software
conditions. GNSS and additional sensor interfaces provide observational context.
Traction remains disabled; measured vehicle, braking and degraded-visibility
validation form the next engineering phase.

## Extended description (150–200 words)

TARK is a research demonstrator for safety assistance to open-cast mine vehicles
in fog and low visibility. Its central idea, the Perception-Verified Safe
Operating Envelope, links the evidence available from perception to the operating
conditions that can be justified. The current production implementation is a
provisional radar-based software model, not a calibrated vehicle safety envelope.

The Raspberry Pi application brings together normalized observations, sensor
freshness, slot-based tracking, parameterized stopping requirements, bounded
commands, persistence and replay. Protocol V2 provides explicit sessions,
receiver-local command expiry and strict response validation across the Python
client and board-neutral ESP32 firmware. A shared monitoring application displays
state, reasons, sensor health, local radar coordinates, map context and recorded
evidence without acquiring motion authority.

Controlled production-path scenarios demonstrate deterministic replay, observer
independence, stale-data handling and zero-command invariants. Separate numerical
studies explore stopping envelopes and adaptive-covariance estimation; these are
not production multisensor fusion. Phase-1 traction remains disabled. Purchased
component verification, electrical HOLD closure, board binding and measured
vehicle, braking and degraded-visibility tests are the next controlled phase,
not claimed results of this software release.
