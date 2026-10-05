# Master-2 — complete system architecture

## 1. Functional structure

```text
MAIN VEHICLE A
  IWR1843BOOST ------ geometry/radial motion ----+
  Arducam B0200 ----- visible semantics --------+
  Lepton + PT3 ------ thermal contrast ---------+--> Jetson Orin Nano Super 8 GB
  LG290P rover A ---- position/quality ---------+      single acquisition ownership
  BNO085 SPI -------- inertial evidence -------+      timing/validity/calibration
                                                      perception + localization
  Wheel angle L/R --> ESP32 -- future qualified ------ tracking/uncertainty
                         |    wheel telemetry          route/corridor relevance
                         |                             proposed R2 evidence envelope
                         +<---- bounded request -------+  (current outputs ZERO)
                         |                            |
                 L298N / TT model                    +--> local driver HMI + buzzer status
                 NOT enabled by this design           +--> recorder/replay
                                                      +--> observation API / WebSocket

LOCAL COOPERATIVE NETWORK: TL-WR902AC, no internet dependency
  LG290P base --> laptop correction relay --> rover A and rover B
  LG290P rover B --> Pi 3B+ --> peer state --> vehicle A / control room
  Control-room browser <-- monitoring data; NOT motor authority

INDEPENDENT PHYSICAL PATH
  traction source --> protection --> manual rated disconnect --> model driver power
```

The diagram is functional, not a wire diagram. The wheel telemetry arrow is a proposed R2 interface: the current V2 STATUS schema does not carry magnetic-wheel samples. It must not be presented as already connected.

## 2. Node responsibilities

| Node | Owns | Must not own |
|---|---|---|
| Jetson A | Main sensor acquisition, qualified localization/perception, proposed risk/envelope calculation, recording, local backend/HMI | Independent physical disconnect; unreviewed motor pin writes; remote-command pass-through |
| ESP32 A | Reviewed session/expiry supervision, future qualified wheel sampling, local feedback and warning output | AI/classification, mine routing, browser authority or certified safety-ECU claims |
| Pi B | One rover's receiver/correction link and timestamped physical peer telemetry | Main AI inference; invented second-vehicle wheel speed/heading; traffic-control authority |
| Fixed base/laptop | Reference status, correction distribution, observer/control-room UI, evidence review | Guarantee of absolute survey datum merely from averaging; authority to override local constraints |
| Local AP | Transport, not decision-making | Collision clearance, trusted vehicle identity or clock integrity by itself |
| Display/browser | Present server decisions, health, maps and evidence | Recompute permissible motion, hide stale data, bypass a stop or send motor commands |

## 3. Single runtime owner and two paths

One runtime owns each actual adapter. API requests, WebSocket subscribers and replay do not start extra readers or advance the live decision clock. Acquisition continues independently of observer count. The existing runtime/adapter boundaries should be extended, not copied into a dashboard-specific pipeline.

**Local path:** acquire → validate/freshness → calibrated observations → track/uncertainty → corridor relevance → risk/envelope → bounded request → independent endpoint validation → qualified feedback → evidence log.

**Cooperative path:** correction/peer packets → identity/schema/time/map checks → localization quality or peer hypotheses → route-conflict advisory → local decision constraints. A peer never directly drives a wheel. Losing a peer is not proof a junction is clear.

**Monitoring path:** immutable snapshot projections → existing REST/WebSocket → driver/supervisor/control room. Slow clients can lose intermediate display updates; they cannot stall the local path.

**Replay path:** immutable recording → isolated replay state → recorded/recomputed comparison → replay-only HMI. No physical adapter, live system state or command submission is constructed by replay.

## 4. Runtime design targets

Targets below are scheduling budgets for later profiling, not current performance or new configuration values.

| Work | Initial target / constraint | Overload behavior |
|---|---|---|
| Radar acquisition | Sensor-profile rate; bounded parser/queue | Detect gaps/overflow and invalidate affected evidence, never replay an old scan as new |
| RGB acquisition/inference | Capture near 30 fps where supported; start inference at 10 fps target | Latest-frame processing, explicit drops; reduce semantic capability if frame age exceeds its budget |
| Thermal | Native approximately 8.7 Hz | Track FFC/duplicate frames; do not synthesize extra independent observations |
| IMU | M1 target 100 Hz inertial / 50 Hz orientation | Preserve source sample times, detect overruns; prediction uncertainty increases |
| GNSS | M1 target 5–10 Hz normalized location | Keep fix/quality/correction age; do not fill gaps with hidden simulation |
| Wheel sensing | M1 100 Hz sampling target | Mark wrap ambiguity or missing samples invalid; no invented distance |
| Proposed R2 decision task | 20 Hz design target | A missed timing budget invalidates positive capability; phase-1 output is still zero |
| Peer state | 10 Hz target, bounded packet | Use current packet only; stale-peer awareness degrades |
| HMI | Existing WebSocket stream; up to 4–10 Hz visual refresh as later profiled | Coalesce updates and cap history; no decision recalculation in render |
| Evidence recorder | Ordered metadata plus separately indexed media chunks | Bounded buffers; report loss/full storage; never claim complete recording after drops |

Startup: load immutable versioned configuration → verify identity/capabilities → initialize clocks/calibration references → begin bounded readers → make health available → evaluate decisions. A working adapter is not immediately a qualified evidence source. A fresh session, configuration match and positive validation are all required for any future endpoint request; current phase remains disabled.

Shutdown: inhibit further requests → retire protocol session/flush pending commands → stop/join readers with bounded deadlines → record termination/loss state → flush durable metadata → close transports. Hung teardown is a fault, not a reason to leave motion authority active. Reconnect restarts source identity and warm-up checks; it does not reinstate old evidence.

## 5. Current software versus intended R2

The current production pipeline has radar-driven slot tracks, a provisional nearest-range-minus-uncertainty envelope and a stopping calculation supplied zero vehicle speed. It does **not** implement the R2 EKF, cross-sensor fusion, calibrated free-space observability, autonomous steering or a TTC-driven production policy. R1 tests do not validate these new designs.

The existing firmware service is portable and host-tested; board USB, fresh boot identity, periodic scheduler and physical watchdog bindings remain to be supplied and verified. The reported separate robot's simple serial movement is not assumed to use that reviewed service.

M2 is an evolution plan within the existing repository: keep adapters, runtime, decision ownership, API/observation separation and canonical protocol. Any new data/recording contract needs versioned compatibility tests; do not overload old fields with changed units or meanings.

## 6. Resource and authority budgets

Use bounded acquisition queues, latest-frame inference, capped track/peer counts, bounded replay pages and one writer for ordered evidence metadata. Actual bounds become controlled configuration after profiling; no infinite arrays or unbounded retry loops. Assign priority to acquisition/health and supervision before video encoding, replay computation or dashboard detail.

CPU/GPU/RAM pressure must be observable. Suppress or shed noncritical media work first, while recording that evidence was lost. If the required local decision latency cannot be met, reduce capability or declare the relevant function unavailable. Do not reuse stale decisions as current.

There is no availability claim based on adding hardware counts. One Jetson, a shared USB hub and a common electronics supply create shared-failure points. The independent manual traction interruption does not depend on them, but it also does not guarantee braking after energy removal.
