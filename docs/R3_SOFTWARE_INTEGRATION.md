# R3 software integration — controlled working record

Update, 5 October 2026: this foundation milestone is retained as history.
The subsequent independent R3 reasoning implementation, current results and
remaining limits are recorded in [R3_REASONING_REPORT.md](R3_REASONING_REPORT.md).
Earlier statements that R3 decision reasoning is pending are superseded there.

4 October 2026. Hardware-only R3 E1 is the controlling equipment baseline.
This document is a working implementation record, not a hardware release.

## A. Existing software adversarial audit (before implementation)

| Area | Disposition | Evidence / R3 reason |
|---|---|---|
| FastAPI, same-origin REST/static serving | KEEP EXACTLY | Existing application factory, auth dependencies and deployment workflow work; no replacement server needed. |
| WebSocket / RuntimeOwner | KEEP BUT STRENGTHEN | One lifespan-owned decision loop and detached snapshots already exist. Add a versioned R3 extension; never add another decision loop or socket. |
| Snapshot/domain validation | KEEP BUT STRENGTHEN | Legacy snapshot has coarse source health, not the R3 identity/time/calibration contract. Preserve its fields and add a separately versioned representation. |
| PV-SOE / perception / tracking | KEEP EXACTLY | Current pipeline is a legacy radar research path. TI Doppler cannot silently become full relative velocity or a clear-road claim. New evidence qualification must not change existing decision math. |
| GNSS/location/map | KEEP EXACTLY | Existing parser, callback and normalized location paths remain for legacy hardware. R3 LG290P identity is not established by an NMEA sentence. Synthetic fleet-map participants remain display-only. |
| Recorder/recomputation | KEEP BUT STRENGTHEN | Existing V2 recordings capture ordered radar reports and an initial checkpoint; strict version/config fingerprints support MATCH. Add R3 provenance without relabelling old records. |
| Events/Driver/control room/Owner | KEEP BUT STRENGTHEN | Preserve current visual system and measured-only KPIs. Readiness and structured explanations belong in existing Diagnostics/Safety views. |
| ESP32 Python/C codec | KEEP BUT STRENGTHEN | Actual protocol is V2, with session challenge, canonical flat CBOR, bounded COBS/CRC32C and zero outputs. It currently has no sensor observation message. Extend the existing codec, not a second framing implementation. |
| Firmware entry point | POST-SELECTION / HARDWARE-DEPENDENT | app_main.c deliberately has no guessed USB, entropy or hardware watchdog binding. Preserve that limitation; new host tests do not establish board operation. |
| Legacy BNO055/MLX90640/LD2450 | KEEP EXACTLY (legacy profile) | These are not BNO085/Lepton/IWR6843 drivers. No rename-based migration. |
| Hardware configuration/readiness | ADD | R3 G14–G17 need exact expected source IDs, bounded queues, independent qualification stages, clock/calibration registries and recording identity. |
| Launchers/deployment/security | KEEP EXACTLY | Loopback simulation launcher clears physical paths. Public-demo writes are blocked. New engineering writes must inherit access checks and remain unavailable publicly. |
| Tests | KEEP EXACTLY; ADD | Prior delivery states 143 frontend and 322 backend passed with 31 firmware-host setup errors (WinError 4551). New runs must report blocked tests honestly. |

No hardware access, purchases, physical verification or production deployment is authorized by this pass. Existing dirty R2 website changes are preserved.

## Implementation sequence

1. Versioned evidence, identity and provenance; strict finite/bounded validation.
2. Clock and calibration/configuration registries; fail-closed qualification.
3. Device-specific normalized adapters and synthetic fixtures, no implicit device discovery.
4. Existing protocol observation extension; Node B ordinary-Wi-Fi contract.
5. Recording provenance, experiment records and compatibility explanations.
6. Additive runtime/API/HMI integration and regression tests.

The sections below record Outputs B–Q. This is an integration-foundation release,
not a claim that the full physical R3 system or its perception pipeline is complete.

## B. Controlled R2 → R3 changelog

| Change | Why it is necessary | Preserved boundary |
|---|---|---|
| Add `app/r3` evidence, identity, time, calibration and configuration models | R3 distinguishes connection from decision qualification | Legacy domain models and safety math unchanged |
| Add `R3_PI5_ADVISORY` profile, explicit fixture/bundle paths | Separate exact expected equipment from existing small-scale equipment | Default remains `LEGACY_SMALL_SCALE`; no auto-discovery |
| Add type-8 `ENCODER_V1` to the existing V2 codec | Timestamped measurement counts are not disabled motor commands | Same COBS/CRC32C/CBOR implementation and session gate |
| Add R3 readiness to existing snapshots and recordings | Trace evidence without changing the old decision's meaning | Versioned optional extension; one runtime owner and WebSocket |
| Age detached R3 publication at the existing observer boundary | A source deadline may expire between 250 ms ticks | Polling cannot acquire data, tick the system, extend freshness, or mutate recorded evidence |
| Add local experiment metadata and catalog | Associate a test with its bundle and recording | No hardware settings or motion writes |
| Add separate normalized-qualification recomputation | Explain MATCH / MISMATCH / NOT RECOMPUTABLE | Existing decision MATCH remains separate |
| Add Diagnostics readiness and Safety “Why?” | Show stage-specific failures and source provenance | Existing navigation, visual system, map and driver priority retained |

No new package dependencies, paid services, alternate decision engine, motor
controls, cloud dependency, browser geolocation request or hardware probes.
No legacy driver was renamed to a new R3 device. No existing feature was removed.

## C. R3 software architecture and implemented boundary

```text
Existing lifespan-owned TarkSystem / RuntimeOwner
  ├─ Legacy radar pipeline → legacy research decision → zero-output command
  │    (R3 profile refuses command submission entirely)
  └─ R3Runtime
       ├─ explicit normalized fixture worker OR reviewed local adapter callback
       ├─ ObservationAdapter → TARK_EVIDENCE_1 → bounded EvidenceChannel
       ├─ immutable clock / calibration / configuration registries
       ├─ source qualification → TARK_READINESS_1 + scoped TARK_WHY_1
       └─ existing recording store + local experiment metadata
                  ↓
       existing REST / WebSocket → existing HMI
                  ↓
       detached replay → isolated RECOMPUTATION channel
```

This diagram intentionally has **no implemented R3-evidence → legacy-perception
arrow**. TI radial Doppler is not silently treated as a full object velocity;
GNSS peer positions are not inserted as local radar detections. A reviewed R3
perception/tracking bridge remains software work. Until then, the “Why?” object
states `LEGACY_RADAR_RESEARCH_PIPELINE` and does not claim R3 support for a decision.

Real transport factories are dependency-injected, not created by a browser or a
packet. The default R3 runtime constructs no real serial, USB, I²C, SPI or PCIe
driver. `ConfiguredReader` and `DatagramPeerWorker` provide bounded lifecycle
interfaces; only the explicit eight-source synthetic worker is selected at
runtime in this release. Platform binding is still required.

## D. Canonical Evidence Contract

Authority: `backend/app/r3/contracts.py`, schema `TARK_EVIDENCE_1`.
Models forbid unknown fields, require strict types, reject nonfinite values and
bound strings, counts, arrays and inline payloads. JSON round trips are tested.

| Group | Stored meaning |
|---|---|
| Identity | Source/node/class, manufacturer/part, optional revision/serial/asset/firmware, driver, boot and session |
| Time | Native value/units/domain, host epoch, monotonic arrival, separately estimated capture and uncertainty, mapping IDs, optional UTC, publication and age |
| Integrity | Sequence, optional source counter, payload length, transport/check/parse result, drop/duplicate/order counts |
| Measurement | Device-specific payload, units, sensor frame, mode/profile, configuration hash |
| Qualification | Connection, production, freshness, clock, calibration, health, plausibility, reason, uncertainty/origin and allowed purpose |
| Provenance | REAL/SIMULATION/REPLAY, evidence origin, original replay mode, raw reference/hash, transformation lineage, software and configuration bundle |

REAL requires `REAL_CAPTURE`; SIMULATION requires `SIMULATOR` or
`SYNTHETIC_FIXTURE`; REPLAY requires `REPLAY_RECORD` and original provenance.
The live channel rejects REPLAY. Unknown capture time, heading, uncertainty,
coordinates and identity stay null/unavailable. Sender qualification flags never
override local clock, calibration, identity, freshness and configuration gates.

Inline measurement JSON is limited to 65,536 bytes. Media uses references and
hashes; references alone do not imply retained media or recomputable inference.
Published R3 readiness includes per-source expiry information. Observer projection
can only age/degrade a detached view; it cannot promote a source or refresh it.

## E. Pi ↔ ESP32 specification

See [R3 ESP32 observation protocol](R3_ESP32_OBSERVATION_PROTOCOL.md) for the
message table, canonical fields, framing bounds, state transitions, restart,
expiry, malformed/duplicate handling and shared Python/C vector commands.

Existing VERSION 2 remains authoritative; retired VERSION 1 is rejected.
`ENCODER_V1` type 8 is measurement-only. It cannot acknowledge a motor command,
refresh command liveness, extend expiry or grant actuation. The R3 profile never
submits legacy type-1 commands. GPIO, USB enumeration, boot entropy and hardware
watchdog behavior are not invented by host tests.

## F. Source adapter matrix

| R3 equipment / source | Implemented now | Still required before real use |
|---|---|---|
| IWR6843ISK / radar-a | Typed Cartesian point/radial Doppler model; documented 16-byte Cartesian TLV payload decoder; finite/count/length checks; fixture | Exact selected firmware/profile full stream header/TLV parser, configuration and identity binding |
| Arducam B0200 / rgb-a | Frame metadata/hash/PTS/exposure contract; existing generic UVC boundary preserved; synthetic metadata | Selected mode and asset admission, UVC capture-time semantics and retained frame binding |
| Lepton 3.5 + PureThermal 3 / thermal-a | 160×120 contract, FFC/radiometry state, no invented temperature conversion | Selected firmware UVC pixel/telemetry format, FFC/TLinear metadata and media binding |
| LG290P A/B/base | Existing checksum-validating NMEA parser reused; fix/uncertainty/course model; separate sources | Receiver identity/configuration, correction routing, PPS mapping, lifecycle bindings |
| BNO085 / imu-a | Documented SH-2 acceleration/gyro/quaternion report payload decoding; normalized model | SHTP/vendor HAL/SPI/interrupt/reset integration and actual timestamp source |
| AMT102 pair / encoders-a | Count intervals, error counters, C/Python measurement frame interoperability | Physical counter capture, GPIO release, wheel geometry/scale/slip validation |
| Node B | Authenticated bounded cooperative protocol, explicit session admission, clock/age/uncertainty gates, injected nonblocking socket worker | Provisioned peer/session/keys, selected network binding, measured clocks/link performance |
| Hailo-8 | Versioned inference interface; caller-owned InferVStreams binding with HEF hash and explicit pre/postprocessing; CPU/fixture/unavailable providers | Released model and runtime context, reviewed tensor semantics and target measurements |

All eight profile sources have synthetic normalized fixtures. These are not
physical recordings and do not contain real mine imagery. For reviewed vendor
formats and exact limits, see [vendor evidence](R3_VENDOR_FORMATS.md).

Legacy LD2450, BNO055, MLX90640, old GNSS and camera interfaces remain in the
legacy profile. Their tests do not qualify replacement R3 hardware.

## G. Timing and clock architecture

`ClockRegistry` binds a mapping to source, source boot, host epoch and clock
domain. A mapping records native/host anchors, scale, drift estimate, drift
uncertainty, last synchronization, expiry, evidence reference and status.

```text
capture estimate = host anchor + native delta × ns/tick × (1 + drift ppm / 10^6)
uncertainty bound = offset uncertainty + elapsed since sync × drift uncertainty / 10^6
age bound = publication/view time − capture estimate + capture uncertainty
```

These are bounds under the supplied mapping assumptions, not measured accuracy
claims. Missing/expired mappings yield TIME_UNSYNCED; wrong epochs/boots yield
CLOCK_RESET; impossible timestamps yield TIMESTAMP_INVALID; excessive drift
yields CLOCK_DRIFT_EXCEEDED. A source can be recent but time-unqualified.

Duplicate/out-of-order packets do not refresh evidence. Native counter/clock
reset requires a new admitted lifecycle; wrap is not silently interpreted as
forward time. Registry identities are immutable and bounded. UTC mapping fields
exist, but this release does **not** implement a measured PPS→UTC mapper or claim
that PPS synchronizes camera exposure or radar chirps.

## H. Calibration and configuration

`CalibrationRegistry` stores kind, ID/version, assets, mount revision, method,
date/operator, transform or parameters, units/frame convention, residuals,
validity domain, software and source artifacts. Rigid transforms must be proper
orthonormal homogeneous transforms, not reflections. Missing transforms are
never replaced with identity matrices.

Kinds include radar/RGB/thermal/IMU/GNSS A/GNSS B to body, encoder geometry,
RGB intrinsics and thermal alignment. Replacement assets, mount changes or a
failed fixture check invalidate the version. Each dependent purpose remains
unqualified until an appropriate valid record matches the asset and mount.

`ConfigurationBundle` identifies hardware/driver profiles, sensor modes, radar,
camera/thermal/GNSS/network selections, calibrations and mounts, model, PV-SOE
parameter identity, cart parameters and software fingerprint. Content is hashed;
an existing ID cannot silently change content. Default bundle is explicitly
uncommissioned. `TARK_R3_BUNDLE_PATH` loads a reviewed bundle and calibrations,
bounded to 256 KiB, with profile/software mismatch rejection. It does not turn
hardware access on. Browser editing of this bundle is not provided.

## I. Recorder, replay and provenance

Existing SQLite recording/session/checkpoint/replay logic is preserved. R3
recording metadata adds profile/hash, full configuration/hash, software
fingerprint, current experiment and explicit claim scope. Each recorded tick
stores admitted sessions, normalized observations, clock/calibration/configuration
records, readiness and existing legacy decision inputs/outputs. Capture of R3
record and readiness uses one lock so a callback cannot split their provenance.

R3 recomputation constructs a separate channel without live callbacks or device
references and evaluates at the recorded tick time. It checks software/profile/
configuration compatibility and compares defined qualification fields. Results:

- MATCH: normalized observations reproduce recorded qualification in this scope.
- MISMATCH: a compared qualification field differs; first divergence is retained.
- NOT RECOMPUTABLE: missing/corrupt/incompatible evidence, unavailable software,
  configuration difference or no evidence ticks; a reason is returned.

Legacy decision recomputation is a separate result. Raw camera/thermal/model
inference reconstruction remains NOT RECOMPUTABLE without retained media and a
released model pipeline. This is not concealed by a normalized-evidence MATCH.
Old recordings without R3 metadata still retain their legacy replay behavior.

Existing recorder error/corruption/restart tests remain applicable. SQLite
software tests do not prove power-loss durability on the target storage device;
G17 needs measured throughput, capacity, safe failure and recovery tests. No
deletion or overwrite of existing user recordings was performed.

## J. Node B ordinary-Wi-Fi cooperative protocol

Authority: `app/r3/cooperative.py`. `PeerMessage` version 1 includes node/boot/
session, sequence, native source and publication timestamps, domain/mapping ID,
uncertainty, normalized fix, health/faults, configuration, provenance and correction
state. Envelope contains the exact payload JSON string and HMAC-SHA256 over its
UTF-8 bytes. Datagram maximum: 8,192 bytes; shared key minimum: 32 bytes. No key
is stored in this repository.

Receiver requires an explicitly admitted boot/session, expected node/config/mode
and independently qualified time mapping. New packet-supplied sessions are not
automatically trusted. Duplicates/old sequence cannot refresh; gaps increment
drops. Unknown position uncertainty, excessive uncertainty, stale receipt/source,
bad health/fix, correction loss when required and failed clocks remove qualification.
Position uncertainty thresholds are explicit configuration, not generic safety
constants. Default zero allowance disables position qualification.

The injected socket worker is nonblocking, accepts the selected peer address,
processes at most 32 datagrams per pump, retries failures and closes cleanly.
Packets also serve as liveness evidence; silence expires. This is not DSRC,
C-V2X, industrial V2X certification or hidden-object detection. A known equipped
peer can supply cooperative context; an unequipped hidden target cannot.

Blind-curve fixture tests cover latency, loss, stale source, restart/session,
correction loss and uncertainty growth. They do not establish a radio link,
surveyed road conflict geometry or validated collision avoidance.

## K. Controlled HMI changes

- Persistent legacy mode plus separate R3 mode; mixed sources remain MIXED.
- Diagnostics: one card per source with expected/detected/identity/driver/
  production/freshness/plausibility/time/calibration/qualification stages.
- Rate, age bound, actual transport sequence drops, rejected observations and
  reason are shown. Bounded history eviction is not mislabeled packet loss.
- Safety: structured “Why?” scope, backend reason and configuration; no generated
  AI safety explanation and no browser safety calculation.
- Diagnostics: local experiment form, active experiment, finish and read-only
  recent catalog. Public-demo writes remain disabled.
- Replay: separate legacy decision, R3 qualification and raw inference outcomes.
- Source timeline is bounded to 100 retained events and visibly shows at most 20.

No duplicate MapLibre or WebSocket instance was added. Existing source
disconnect/stale handling clears the workspace rather than retaining apparently
current values. Cached REST/WebSocket views age R3 deadlines without changing
the decision loop. The HMI is sampled telemetry, not an independent continuous
safety monitor. Driver view remains action-first; engineering cards stay in
Diagnostics. See the verification report for viewport and console checks.

## L. Experiment manager

Local SQLite registry: one active experiment, up to 1,000 retained experiments;
browser catalog shows the newest ten. Metadata includes title/scenario/operator/
date, hardware/software/config/calibration identities, expected sources,
visibility condition and notes. Server validates current identity and prevents
changing experiments during an active recording.

Workflow: Diagnostics → create experiment → Replay → start/stop recording →
load/verify → Diagnostics → finish → load catalog. Recording attaches
automatically. One recording per experiment prevents silent replacement.
Restart changes unfinished ACTIVE entries to INTERRUPTED. Completion summarizes
recorded duration, source presence, warning/fault tick counts, mode transitions,
drop-counter increases, recording validity and R3 replay result. A fault-tick
count is not a count of independent incidents or real accidents.

## M. Test / fixture plan and reproducibility

New tests: `test_r3_evidence.py`, `test_r3_protocol.py`, `test_r3_runtime.py` and
frontend `R3Evidence.test.tsx`. Coverage includes strict schemas, finite values,
identity/provenance contradictions, modes, clocks, resets/drift/expiry, missing
calibration, concurrent bounded retention, vendor payloads, rejected peer data,
configuration mismatches, replay corruption/isolation, experiment association,
public-write denial, unavailable inference and a mocked SDK call.

Shared vector JSON and generated C header drive the actual production C and
Python codecs. No skip converts execution denial into success. Final counts,
exact commands and the earlier Windows policy failure are in
[R3 verification](R3_VERIFICATION_REPORT.md).

The acceptance probe is intentionally limited:

```text
python scripts/r3_acceptance_probe.py --url http://127.0.0.1:8000 --samples 20
```

It measures bounded HTTP requests and reports source/inference diagnostics;
it does not open hardware. Running on this Windows PC is PC evidence only.
Full Pi CPU/RAM/temperature/throttle/recorder-throughput instrumentation remains
work; null diagnostics are not measurements. Do not describe this script as a
complete Pi acceptance test.

## N. Pre-selection implementation status

| Capability | Status / scope |
|---|---|
| Evidence/provenance/time/calibration/configuration contracts | IMPLEMENTED / FIXTURE-VERIFIED |
| Eight normalized source interfaces and synthetic worker | IMPLEMENTED / FIXTURE-VERIFIED |
| Reviewed TI Cartesian and SH-2 report payload subset | IMPLEMENTED / FIXTURE-VERIFIED; not complete wire drivers |
| ESP32 observation frame encoding and Python/C compatibility | IMPLEMENTED / host-tested; physical binding pending |
| Normalized recording/recomputation and experiments | IMPLEMENTED / FIXTURE-VERIFIED |
| Node B validation/injected datagram worker | IMPLEMENTED / FIXTURE-VERIFIED; not runtime-provisioned fleet communication |
| Hailo provider and explicit model boundary | IMPLEMENTED / mocked SDK verified; no model/hardware performance claim |
| HMI integration and legacy compatibility | IMPLEMENTED / software/browser tested |
| R3 qualified evidence into R3 perception/advisory | NOT IMPLEMENTED; legacy decision scope deliberately retained |
| Complete real transport bindings, raw-media inference replay, PPS producer | INCOMPLETE integration, not claimed hardware-only |

## O. Post-selection and commissioning backlog

1. Freeze delivered firmware/mode identities and authoritative format documents;
   record exact hashes, asset IDs and selected profiles. Do not select arbitrary ports.
2. Implement/review complete TI stream framing, SH-2/SHTP HAL, PureThermal metadata,
   LG290P setup/correction/PPS, UVC media retention and Hailo context/model bindings.
   These include software tasks; absence of equipment is not an excuse to call
   every binding complete.
3. Bind admitted workers into the R3 lifecycle using reviewed configuration;
   test absent device, reconnect, malformed stream, stop and restart with mocks
   before opening actual hardware under separate commissioning authorization.
4. Define and test the R3 perception bridge: approved coordinate conventions,
   transforms, uncertainty and time gates, radial versus full velocity semantics,
   local versus cooperative evidence. Do not change legacy math by relabeling inputs.
5. Provision Node B keys/peer/session and clock mappings; test replay resistance,
   sequence loss, source expiry and network outages on the actual local network.
6. Implement target resource collectors and full recorder/media load/recovery
   benchmarks; perform model evaluation separately from latency profiling.
7. Obtain physical calibration records, wheel geometry, asset/mount identity,
   measured clock uncertainty, radio coverage, power/storage behavior and display
   ergonomics. These verification steps genuinely require the selected equipment.
8. Add real-capture fixtures alongside—not instead of—the synthetic regression set.
   Keep real commissioning reports separate from software test reports.

## P. Release gates, fault mapping and claims

G14 adapter integration, G15 time mapping, G16 untethered network and G17 recording
throughput/recovery have software foundations. **None is hardware PASSED.** The
UI marks hardware tests pending. Overall R3 operational release remains OPEN.

| Observable fault | Current software response / remaining evidence |
|---|---|
| Frozen source counter / duplicate packet | Reject refresh; eventually stale/unqualified. Constant physical scene alone is not diagnosed as a frozen sensor. |
| USB/source disconnect | Worker stop/failure and missing production; exact real transport callback remains binding work. |
| Clock reset/drift/expiry | Explicit time state; no cross-source qualification. |
| Missing/replaced calibration | Asset/mount/version mismatch removes dependent qualification. |
| GNSS no fix / unknown uncertainty | No qualified location; no made-up metre accuracy. Jump detection needs reviewed plausibility parameters/temporal integration. |
| Correction loss | Peer can require APPLIED corrections; receiver correction telemetry binding pending. |
| GNSS antenna failure | Only report explicit receiver diagnostics; no inference from poor fix alone. |
| IMU reset / encoder loss | Session/time/fault/count fields exist; physical diagnostic generation and interpretation still required. |
| Node B/network/AP dropout | Receipt/source expiry; no replacement fake position; AP failure cause is not inferred from silence. |
| Storage full/corruption/write failure | Existing recorder failure/recovery boundary; real storage power-loss/throughput tests pending. |
| Hailo unavailable | Explicit unavailable provider, no fabricated detections. |
| Pi temperature/throttle/undervoltage | Not yet collected by R3; unavailable, not healthy. |
| Display disconnected | No physical display diagnostic claim; browser link loss is different. |

Security: read-only endpoints inherit existing access checks; experiment writes
reuse recording-write authorization and are forbidden in public-demo environment.
No observation-injection, motor, port-selection or calibration-grant endpoint is
exposed. Keep development mode on loopback; do not expose unauthenticated local
engineering writes to a LAN/public host. HMAC authenticates a configured peer,
not its GNSS truth. Key distribution/rotation is a commissioning responsibility.

Allowed claim: **“R3 software evidence integration foundation implemented and
tested with synthetic fixtures; physical integration and validation pending.”**
Disallowed: physically integrated, synchronized, real-time, mine-certified,
reliable AI collision avoidance, or operational gains inferred from fixture MATCH.

## Q. Adversarial SIH/NMDC judge review

**Does a green connection mean safe to move?** No. Readiness has separate stages;
even qualified evidence is purpose-limited. The browser has no motion authority.

**Where is the proof that R3 sensors drove the safety decision?** There is none
in this pass. The existing decision explicitly retains its legacy research scope.
R3 observations are qualified/recorded but not covertly substituted into it.

**Is the hidden vehicle detected through fog/rock?** No. An equipped peer may
send cooperative position over ordinary Wi-Fi. Neither packets nor synthetic
map participants establish local sensing of an unequipped hidden object.

**Does RTK FIXED imply exact position or heading?** No. Fix state, uncertainty,
correction state and course are different. Stationary course is not body heading.

**Does replay MATCH prove field safety?** No. It proves a defined computation is
reproducible from the retained evidence/configuration. Missing raw media/model
cannot be hidden behind a normalized replay result.

**Is 26 TOPS sufficient performance evidence?** No. Selected-model latency,
drop/queue behavior, system load and temperature require target measurements.

**Can hardware be plugged in with no further software work?** Not yet. The
interfaces and gates reduce redesign risk, but selected wire/platform bindings,
R3 semantic integration and target instrumentation still require implementation.

**What is defensible today?** A working existing HMI with tested provenance,
qualification, protocol extension, experiments and normalized replay; a clear
list of unimplemented bindings; no invented physical-validation claims.
