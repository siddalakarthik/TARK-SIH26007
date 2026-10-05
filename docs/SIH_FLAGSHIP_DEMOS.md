# Three TARK R3 flagship SIH demonstrations

5 October 2026 · **SIMULATION / SYNTHETIC EVIDENCE** · advisory only

Exactly three sequences, no hardware access, no random inputs and no prescribed
decisions. Existing ObservationAdapter → EvidenceChannel → qualification → R3
reasoner → advisory/Why → RecordingStore → closed/reopened SQLite → isolated
R3 recomputation. The browser/live bus is not touched by the runner.

From the installed project environment, at repository root:

```text
python -B scripts/run_sih_demos.py --scenario all --output ../work/sih_preselection
```

Or select `degraded-visibility`, `collision-risk`, `blind-curve`. Use a fresh
output directory on each repeat. Each of the three directories holds
`presentation.svg` (judge-facing stage card), `summary.json` (every tick),
`metadata.json` (profiles/configuration/checkpoint/provenance), `records.json`
and the **existing recorder's** `recording.db`. The store generates a session
UUID; replay timings vary. Ordered normalized decisions/evidence are deterministic.

SVG cards show stage endpoints, not all transitional states. Inspect summary
rows for hysteresis, TTC exclusions, uncertainty, source contributions,
excluded evidence, observability, stopping requirement, hazards and Why.
SVGs are static evidence illustrations, not a new dashboard or LIVE feed.
Replay comparisons are qualification + R3 advisory, **not** legacy decisions
or raw-image inference. Raw media inference is NOT RECOMPUTABLE here.

## 1. Degraded visibility / PV-SOE

**TARK-DEMO-01-DEGRADED-VISIBILITY**

**Question:** Must fog always mean STOP?

Healthy configured research coverage → severe RGB fog factor → loss of required
geometry → sustained restored evidence. Stage endpoints:

| Stage | Observed state | Qualified range / advisory cap |
|---|---|---|
| Healthy | NORMAL | 14.790 m / 1.500 m/s |
| RGB fog; radar qualified | RESTRICT | 2.790 m / approximately 1.094 m/s |
| Geometry unavailable | UNKNOWN | unavailable / unavailable (not zero precision) |
| Sustained recovery | NORMAL | 14.790 m / 1.500 m/s |

**Notice / novelty:** RGB support reduces under the explicit environment model;
radar retains its configured contribution. Loss of supporting geometry is not
proof of clearance. The first restored frame stays UNKNOWN/RECOVERY_PENDING;
restoration requires distinct frames and the configured dwell.

**Simulated:** coverage, fog response, clocks/calibrations, wheel response and
vehicle parameters. Thermal contributes only as permitted by the existing
fixture model; no measured thermal fog range is added.

**Not claimed:** fog trials, actual detection range, mine-safe NORMAL, braking.

**Run:** `python scripts/run_sih_demos.py --scenario degraded-visibility`

**Expected:** 45 persisted ticks; qualification MATCH; advisory MATCH.

**30–45-second narration:** “This is synthetic evidence, not a fog trial. First,
TARK has enough configured observation support. As RGB visibility degrades,
qualified radar still contributes, so operating capability reduces rather than
fog automatically forcing STOP. When the required geometry disappears, TARK
reports UNKNOWN: no evidence is not a clear road. Restoring one packet is not
enough. Only sustained, distinct evidence restores the research envelope.
Every decision is recorded and independently recomputed.”

## 2. Moving collision risk / corridor / conditional TTC

**TARK-DEMO-02-COLLISION-RISK**

**Question:** Does TARK reason about a hazard, or merely draw targets?

Healthy baseline → outside target created/confirmed → potential corridor entry
→ relevant target with justified closing motion → unmet stopping requirement.
Stage endpoints are NORMAL → UNKNOWN → RESTRICT → RESTRICT → STOP.
UNKNOWN during the initial lateral approach is deliberate: predicted corridor
entry is uncertain. It is not replaced with a dramatic but unjustified NORMAL.

**Notice / novelty:** one retained track; body x-forward/y-left coordinates;
position/time/velocity bounds; conditional TTC unavailable until justified.
TTC is derived from successive positions under the fixed-body-axes research
model. Radar radial velocity is independently zero in this fixture: it is never
substituted for the target vector. Later TTC is finite with a bounded interval;
the advisory cap contracts. STOP appears when lower-bound hazard distance is
below the parameterized stopping requirement, approximately 1.395 m.
Why names the track, supporting evidence and stopping-limit reason.

**Simulated:** Cartesian target trajectory, calibration/time/uncertainty,
fixed body axes, wheel response and stopping parameters. Object class is not
invented; this is a geometrically relevant target.

**Not claimed:** measured braking, Doppler-vector inference, ground-truth speed,
certified collision avoidance or moving real motors.

**Run:** `python scripts/run_sih_demos.py --scenario collision-risk`

**Expected:** 42 persisted ticks; qualification MATCH; advisory MATCH.

**30–45-second narration:** “This simulated target starts outside the corridor.
TARK creates and confirms its track, and explicitly holds UNKNOWN when possible
entry remains uncertain. Once geometry and motion evidence justify it, the
target becomes corridor-relevant. Closing motion comes from two positions,
not Doppler treated as a velocity vector. TTC is shown only when its conditions
hold. As usable distance shrinks, the operating envelope reduces; eventually
the research stopping requirement is not met. Why identifies the exact target
and evidence. No physical brake is actuated.”

## 3. Blind-curve cooperative awareness

**TARK-DEMO-03-BLIND-CURVE**

**Question:** What does an equipped peer contribute beyond local line of sight?

No relevant conflict → fresh qualified B position overlaps the declared
synthetic conflict zone → B packets stop and the evidence expires.
Endpoints: NORMAL → RESTRICT/COOPERATIVE_CONFLICT → UNKNOWN/RECOVERY_PENDING.

**Notice / novelty:** no B radar point or RGB/thermal detection is generated.
Cooperative context is separate from local tracks. Identity, session, sequence,
capture/arrival time, uncertainty, RTK/correction state, health and provenance
remain in recorded evidence. Once stale, B disappears from active qualified
context. Its last position is retained as historical recording evidence, not a
ghost vehicle. Communication loss does not silently release to NORMAL.

**Simulated:** own/peer positioning, correction quality, clocks, separate node
identity and conflict-zone overlap. This is not a measured RF/V2V link or map.

**Not claimed:** detection through rock, detection of unequipped vehicles,
surveyed mine geometry, real RTK accuracy or physical authentication validation.

**Run:** `python scripts/run_sih_demos.py --scenario blind-curve`

**Expected:** 30 persisted ticks; qualification MATCH; advisory MATCH; no active
peer after expiry; no local B detections.

**30–45-second narration:** “Vehicle B is outside A's local line of sight in
this synthetic scenario. We do not invent a radar or camera detection for it.
Instead, a separate equipped peer supplies qualified position evidence.
When that report overlaps the configured conflict region, TARK restricts the
research envelope and explains the cooperative conflict. Now the peer link
stops. Its stale position is removed from active support, but disappearance
does not mean the conflict is safe: capability remains UNKNOWN. This is
cooperative awareness—not seeing through rock.”

## Existing browser presentation and tests

The existing Safety/Driver/Diagnostics/Replay screens remain unchanged.
They display runtime telemetry, **not** these CLI sequences unless an explicit
existing observation feed is connected. Do not imply that the ordinary
uncommissioned dashboard fixture reproduces the positive-envelope cards.
CLI and SVG stage cards are the reproducible presentation for this freeze.

Focused tests: `python -B -m pytest backend/tests/test_sih_demos.py -q -p no:cacheprovider`.
For current full verification and physical limitations, see
[the freeze handoff](TARK_R3_PRESELECTION_FREEZE.md) and
[R3 reasoning report](R3_REASONING_REPORT.md).
