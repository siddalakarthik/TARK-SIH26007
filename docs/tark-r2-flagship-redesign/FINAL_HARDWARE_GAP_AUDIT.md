# Final flagship hardware feature-gap audit

Revision F0-A1 · 2 October 2026 · Audit of the six-document F0 clean-sheet flagship package

## Verdict and freeze meaning

**FLAGSHIP HARDWARE: FREEZE APPROVED — NO UPGRADE REQUIRED**

This freezes the **capability selection and F01–F27 BOM scope** for the already-defined bounded research demonstration. It is not a fabrication, purchasing, energization, software-completion or physical-verification approval. The original [G01–G14 gates](05_VALIDATION_SCALABILITY_AND_GATES.md) remain in force. The F0 statement that fabrication freeze has not passed remains true. Unselected protective-device details, cart drawings and node-B power-bank identity must still be resolved within their existing allocations.

No new sensor, compute platform, actuator, network technology or storage purchase is justified by the requested software features. None is removed. No old hobby-robot hardware is introduced. Existing software and motor authority are unchanged; `DISABLED_PHASE_1` remains untouched. The new cart itself has no powered drivetrain.

## A. HARDWARE ALREADY SUFFICIENT

The [feature matrix](FLAGSHIP_FEATURE_TO_HARDWARE_MATRIX.md) traces every requested A–J feature group to its physical evidence and identifies conditional/unavailable quantities.

| Capability | Existing physical source | Qualification needed, not a new purchase |
|---|---|---|
| Position, guidance and mine-map context | LG290P A/base, BNO085, two AMT102-V paths, Pi/HMI | Road survey/graph, datum, lever arms, motion calibration and bounded uncertainty |
| Two-participant fleet and cooperative conflicts | Separate A/B rovers, shared base, MCU B, AP/laptop | Bidirectional corrections, identity, common reference, source ages and coverage |
| Local perception | IWR6843ISK, B0200/Hailo, Lepton/PT3 | Radar profile/decoder, supported model, calibrated spatial/time alignment |
| Qualitative visibility evidence | RGB plus existing charts and controlled-obscuration access | Reproducible optical evidence labels, not meteorological metres |
| Shadow operating envelope | Radar plus GNSS/IMU/wheel evidence | Geometry-aware relative motion and justified model parameters; not actual brake authority |
| Recording, replay, diagnostics and control room | Endurance SD, Pi, AP and lab laptop access | Rate/retention benchmark, provenance, versioned records and bounded queues |

Sufficiency is an engineering assessment of the hardware paths, not a test result. The new radar, RTK, Hailo and metrology paths still require the later integration listed in G14. No claim is made that the existing application already supports the newly selected hardware.

## B. SMALL HARDWARE ADDITIONS REQUIRED

**None.** The only item classified REQUIRED NOW in the candidate table is a wheel-speed source, and it is already supplied by F11–F13. Do not order an additional encoder.

The delta ledger [FINAL_MICRO_UPGRADE_BOM.csv](FINAL_MICRO_UPGRADE_BOM.csv) contains one zero-quantity decision record, not a purchasable part: `NO ADDITIONAL FLAGSHIP HARDWARE REQUIRED`.

## C. INDUSTRIAL-ONLY HARDWARE

Industrial-only entries below are outside the student purchase scope. They identify measurements/infrastructure to evaluate against a real site's operational domain; they are not a claim that all such technologies must coexist on every dumper.

Vehicle qualification may require rear/side coverage, approved vehicle-bus input, vehicle-specific steering geometry, a cab-readable display/alarm system, stronger positioning/heading assurance and a surveyed communications network. None of those needs is established merely by the low-speed forward-facing cart experiment. Do not claim the cart has 360-degree sensing, mine-wide radio coverage, stationary GNSS body heading or OEM brake data.

## D. HARDWARE IDEAS REJECTED

Exactly one category is assigned to each of the 30 requested candidates. NOT REQUIRED means no demonstrated need in the current scope, not that the technology can never have value. REQUIRED NOW may be already satisfied.

| Candidate | Classification | Decision and reason |
|---|---|---|
| Second radar | NOT REQUIRED | Existing forward radar covers the research measurement role; another radar does not supply cooperative hidden-peer identity or remove profile/calibration work. |
| Rear radar | INDUSTRIAL ONLY | Reversing/rear collision coverage belongs to a later vehicle-specific domain; no rear-clearance claim in this forward experiment. |
| Side radar | INDUSTRIAL ONLY | Side blind spots/swept-path coverage require later vehicle hazard analysis, not another front-demo sensor. |
| LiDAR | NOT REQUIRED | No unmet depth/mapping requirement for the measured course; it cannot be assumed immune to optical obscuration. |
| Ultrasonic | NOT REQUIRED | No close-range automatic maneuvering function; independent supervision protects the manual cart. |
| Stereo/depth camera | NOT REQUIRED | Radar supplies measured geometry; stereo is not required for RGB semantics or a measured road graph. |
| UWB | NOT REQUIRED | The defined course is open-sky GNSS, not guaranteed indoor/pit localization; no new anchor infrastructure is justified. |
| Additional IMU | NOT REQUIRED | A already has BNO085; B is explicitly a location-only peer with unknown stationary heading. |
| Compass | NOT REQUIRED | BNO085 already has a magnetic sensing path; another compass does not establish reliable geographic heading near steel. |
| Barometer | NOT REQUIRED | Surveyed test-course geometry provides needed context; pressure is not reliable road identity or visibility evidence. |
| Rain sensor | NOT REQUIRED | Dry controlled experiments; no automatic rainfall control requirement or monsoon qualification claim. |
| Humidity sensor | NOT REQUIRED | Relative humidity is not meteorological visibility and does not unlock a requested prototype function. |
| Fog sensor | NOT REQUIRED | An unspecified fog detector is not a calibrated visibility reference. Use qualified optical evidence labels. |
| Visibility meter | INDUSTRIAL ONLY | Consider a traceable reference for later quantitative meteorological studies/site monitoring; not needed for the current qualitative claim. |
| Wheel-speed source | REQUIRED NOW | Already satisfied by two AMT102-V paths, MCU and buffers in F11–F13; zero new quantity. |
| Steering-angle sensor | INDUSTRIAL ONLY | Real vehicle kinematics/swept paths may need approved steering data. Manual cart motion is measured by wheels/IMU, with no autonomous steering. |
| CAN/J1939 | INDUSTRIAL ONLY | No real HEMM bus in this cart; purchasing an interface adds no vehicle measurement. |
| Haptic alert | NOT REQUIRED | Text/symbol display plus existing buzzer meets demo alert modalities; haptic human-factors validation is not a missing measurement. |
| Brighter HMI | INDUSTRIAL ONLY | Cab sunlight/night/glare qualification is later; current display is limited to validated daylight/shade conditions. |
| Speaker | NOT REQUIRED | F19 buzzer supplies audible attention; speech generation is not a stated hardware requirement. |
| Physical warning beacon | INDUSTRIAL ONLY | Site pedestrian/vehicle warning rules may require a qualified beacon; no safety reliance on the demo alarm. |
| USB SSD | NOT REQUIRED | Bounded session estimates fit the current SD allocation; no measured throughput/retention failure justifies it. |
| Ethernet switch | NOT REQUIRED | Current topology uses A on AP Ethernet and laptop/B on Wi-Fi; no additional wired port demand. |
| Second AP | INDUSTRIAL ONLY | Mine coverage/roaming requires an RF survey; no second AP is justified for the small validated course. |
| LoRa | NOT REQUIRED | Existing LAN serves prototype telemetry/corrections; another radio adds a path without resolving a demonstrated coverage requirement. |
| LTE/5G | INDUSTRIAL ONLY | A future mine network option after survey; no internet dependency is needed for this demonstration. |
| C-V2X | INDUSTRIAL ONLY | Evaluate for a compatible industrial ecosystem and authorization; current cooperation is local V2I over Wi-Fi. |
| Better GNSS antenna | NOT REQUIRED | Three antennas are already included; verify their specifications/installation under G07 before claiming performance, not speculative replacement. |
| GNSS heading dual-antenna system | INDUSTRIAL ONLY | True body heading at rest can justify a validated baseline system in an expanded domain; moving-course/unknown-heading semantics suffice here. |
| Larger power source | NOT REQUIRED | Existing 256 Wh design has an illustrative 90-minute target margin; confirm measured load/runtime, do not purchase unused capacity. |

## E. SOFTWARE/CALIBRATION SOLUTIONS INSTEAD OF NEW HARDWARE

These are requirements for later integration/validation, not software implemented by this audit.

1. **Position and map:** version the surveyed road graph, coordinate reference, base coordinates, antenna lever arms and map-match uncertainty. Retain multiple candidate roads when ambiguous; withhold specific turn instructions rather than invent certainty.
2. **Heading:** distinguish body heading, GNSS course over ground and assigned route intent. Initialize A's body frame and measure IMU/wheel drift. B publishes credible moving course only; an unknown heading is an acceptable truthful state, not a hidden sensor.
3. **Timing:** store sample time, host receipt, clock mapping, sequence/session and age. Measure latency/clock uncertainty. GNSS UTC does not synchronize all camera exposures or radar chirps. Bound stale-data displacement, for example speed bound × age, and invalidate beyond the accepted bound.
4. **Hazards:** use radar geometry plus valid time-aligned pose/extrinsics for a global obstacle location. Otherwise record an observer-location report or uncertain region. Record source, confirmation, timestamp, expiry and revocation. Closures/destinations are authorized intent records, not sensed facts.
5. **Trust:** separate connected, fresh and valid. Do not label an absent/failed source healthy; retain calibration state, residuals, dropped frames and uncertainty. Temperature/image quality does not certify detection completeness.
6. **Replay:** retain original observations and original outputs, alongside calibration, firmware/profile/model/configuration identifiers. Keep recomputation separate. Record stream gaps, storage truncation and clock uncertainty rather than silently interpolating evidence.
7. **Compute:** benchmark the existing Pi/Hailo acquisition, inference, recorder and HMI together. Model compatibility and latency are G06/G14 gates, not solved by buying more sensors.
8. **Navigation loss:** bounded dead reckoning on A can maintain an estimate only within measured drift limits. B has no corresponding wheel/IMU fallback. Neither gets indefinite localization continuity by software assertion; issue degraded/unavailable navigation when evidence expires.

## F. CAN/J1939 decision

**Choose option 1: no purchase.** A CAN interface without a real permitted vehicle bus adds a transport demonstration, not gear, engine, brake or authentic vehicle-speed evidence. Linux exposes J1939 through its CAN networking stack; protocol fixture work can be labelled synthetic without pretending it is HEMM acquisition. [Linux J1939 documentation](https://docs.kernel.org/networking/j1939.html)

Industrial connection remains a separate OEM/site review: actual interface/pinout, bus parameters, electrical isolation/protection, supported PGNs/semantics, source freshness and permitted read-only access. Do not imply that all J1939 vehicles expose the same braking data, that a connector alone grants access, or that vehicle data authorizes actuation. No exact industrial interface is selected because no real target bus has been specified.

## G. Visibility-hardware decision

**Choose option 1: no new visibility device.** Use `TARK VISIBILITY EVIDENCE INDEX` or calibrated qualitative states GOOD / DEGRADED / SEVERE / UNKNOWN. GOOD means the tested optical-evidence band, never safe-to-drive or a guarantee of clear space. This is separate from any existing safety-state enum.

Meteorological optical range is a defined optical quantity linked to extinction/transmission and a contrast threshold; an arbitrary image score, humidity value or radar range is not that measurement. [Vaisala MOR definition](https://docs.vaisala.com/r/M210667EN-G/en-US/GUID-A9B97051-B87E-4065-AAA6-F7450B732AAF/GUID-844CDE21-5C8F-4D41-849B-BAF15AA50901)

Within existing F25/F26 allowances, record a contrast/recognition target at known stations, clear reference frames, camera exposure/gain/settings, illumination conditions and repeated obscuration trials. Define the classes before evaluating held-out recordings. Reject lens contamination, glare, automatic exposure changes or out-of-calibration illumination as atmosphere measurements; report uncertain cause/UNKNOWN when not distinguishable. Save the reference condition and model/calibration version.

Report statements such as “target recognition degraded at this measured station under this test condition,” not “mine visibility is 3 metres.” A local observation must not become a mine-wide weather assertion.

If a future experiment requires visibility in metres, use an independently calibrated transmissometer or suitable calibrated scatter instrument/reference with uncertainty and spatial representativeness established. A simple lux/transmission rig can measure a defined path ratio under controlled geometry, but does not automatically establish meteorological visibility. Such a new quantitative requirement changes the study scope; it is not needed to close this qualitative demonstrator.

## H. Storage decision and arithmetic

**Choose option 1: retain F15, 128 GB MAX ENDURANCE microSD.** Keep the planned 40 GB OS/models, 20 GB free/maintenance margin and 60 GB dataset quota, subject to checking actual usable capacity and installed footprint. All sizes below are decimal and exclude file/database overhead.

| Stream | Assumed rate | Calculated GB/hour |
|---|---:|---:|
| Compressed RGB example | 8 Mb/s | 3.600000 |
| Raw 16-bit thermal example | 160 × 120 × 2 bytes × 8.7 frames/s | 1.202688 |
| Processed radar and other telemetry allowance | 0.5 MB/s | 1.800000 |
| Total example | Approximately 1.834 MB/s | 6.602688 |

Formula: compressed video GB/h = Mb/s × 0.45. Thermal GB/h = width × height × bytes/pixel × frames/s × 3600 / 10^9.

The 60 GB quota supports approximately **9.09 h** in this example; 90 minutes uses **9.90 GB** before overhead. A higher 30 Mb/s RGB scenario totals **16.50 GB/h**, approximately **3.64 h** or **24.75 GB per 90 minutes** before overhead. These are assumptions, not measured camera settings or retention guarantees. Uncompressed 1080p video, duplicate encodings, raw ADC radar and indefinite archives are not this retention plan.

SanDisk specifies endurance-oriented recording and U3/V30 for this product family; those ratings do not establish mixed database/video latency, power-loss integrity or an arbitrary TARK workload lifetime. Test simultaneous recording and disk-full behavior on the delivered card. [SanDisk specifications and qualification notes](https://www.sandisk.com/en-in/products/memory-cards/microsd-cards/sandisk-max-endurance-uhs-i-microsd?sku=SDSQQVR-128G-GN6IA)

Use bounded incident buffers, explicit retention/locked-record policy, reserve-space alarms, clean shutdown and verified offload to the existing lab machine. Never overwrite locked incident evidence silently; report recording unavailable if capacity cannot safely be reclaimed. Prefer supported compressed camera output while recording its actual settings and measuring host decode load.

The selected AI HAT+ occupies the Pi PCIe port; do not add an incompatible NVMe HAT. A USB SSD would also require port/bandwidth/power validation. [Raspberry Pi AI HAT documentation](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html)

No SSD cost is added. Reopen storage only upon a recorded failure of the accepted workload/retention test, not simply to improve the parts list. Storage is not independently validated by these calculations.

## I. GNSS, fleet scaling and blind-curve conclusion

The topology supports the **concept** of N equipped vehicles: each has a rover, unique identity/session, local computation and network connection. Vehicle A uses Pi plus metrology MCU; the reduced-function B node uses its MCU for location forwarding, not full perception. Additional full vehicles need their own qualified local sensor/compute/HMI kits. The two real rovers and one shared base are enough to demonstrate independent peer updates and cooperative evidence; N-vehicle implementation and capacity must be tested later with clearly labelled synthetic load.

Correction infrastructure stays shared. Each rover must receive appropriate corrections as well as send its fixes. One local base/AP is not a promise of whole-mine coverage, and there is no one-base-per-vehicle requirement. Relative base consistency alone does not prove absolute map accuracy.

Quectel's LG290P protocol documents course-over-ground and speed observations. Treat those as motion observations, not automatic stationary body heading. [Quectel GNSS protocol specification, manufacturer-hosted copy](https://forums.quectel.com/uploads/short-url/6xmu7ol2mqq8NBBAKdxvPWVudu7.pdf)

For B, accept motion direction only when successive displacement exceeds its position/time uncertainty and has adequate signal quality. For A, align IMU/wheel/GNSS evidence and retain disagreement. Do not set a numerical heading threshold without calibration. A route assignment is intent, not an observed orientation. At rest or ambiguous movement, keep heading unknown and retain the occupied position/footprint with uncertainty.

For the blind-curve demonstration, use a common measured course, fresh A/B evidence, bounded clock/network age, candidate routes and **occupancy intervals** at the conflict region. ETA is an uncertain estimate, not an exact arrival promise. A stopped participant already in the region remains a conflict candidate. A stale peer never becomes an all-clear. Cooperative information does not detect unequipped vehicles behind a hill, nor guarantee radio coverage through the hill.

**No extra radar, UWB or dual-antenna heading purchase is required for this bounded conflict demonstration.** Always-known stationary body orientation and continuous GNSS-denied operation are not supplied by this baseline and must not be advertised.

## J. Safe-operating-envelope conclusion

Motion evidence exists through wheel response, IMU and GNSS. Radar supplies range and radial motion; RGB supplies semantics and thermal supplies corroboration. Those are sufficient inputs for a research shadow envelope with explicit uncertainty and model parameters.

The illustration `d_required = v × total_delay + v² / (2 × deceleration) + margin` still requires valid positive deceleration and justified load/grade/delay assumptions. No added sensor can substitute for actual HEMM braking characterization. Corridor motion/TTC must be derived using valid geometry, not equated to every radar Doppler observation. Unknown model/evidence means PARAMETERIZED / NOT VALIDATED or unavailable, not a safe speed guarantee.

The cart's mechanical brakes and supervisors protect the experiment independently. TI EVM use restrictions remain applicable. This audit does not approve functional-safety evaluation, automatic braking, powered traction or mine operation.

## K. Per-vehicle, shared and prototype-only allocation

This table classifies function at deployment, not whether the development-board SKU is industrially suitable. It refines mixed experimental rows without changing their quantities or prices.

| Category | Hardware/functions in current allocation | N-vehicle treatment |
|---|---|---|
| PER-VEHICLE | F01–F03 compute/inference/cooling function; F05–F08 sensing; two rover portions of F09; F10 motion; qualified equivalents of F11–F13 metrology; F14/F19 HMI/alert; F15 recording; local portions of F18 | One appropriate kit per fully equipped vehicle; actual cart wheel/MCU carrier implementation may be replaced by qualified vehicle inputs. B is only a location node. |
| SHARED MINE INFRASTRUCTURE | Base portion of F09; F17 network role; base mount portion F24; calibration/reference access F25; control-room/relay/archive role F27; shared cables F18 | Size by coverage, capacity and availability, not by multiplying every line by N. Road/map database is a software/infrastructure asset. |
| PROTOTYPE-ONLY | F04 bench supply, F16 desktop hub realization, F20 power station, F21 manual cart, F22 peer bank, F23 lab distribution, B carrier portion F24, F26 artificial aerosol; development/debug fixtures in F12/F13 | Do not replicate this experimental apparatus per dumper. Industrial supply, packaging and interconnects require separate qualification. |

F26 was grouped as shared experimental access in the original BOM. Its experimental role is **PROTOTYPE-ONLY** for fleet scaling: an aerosol generator is not mine operating infrastructure. The lab laptop is an access allowance, not a newly purchased industrial server. Its archived-data capacity must be checked rather than assumed from a model name.

Industrial planning remains: N × qualified local kit + shared corrections/network/control room + survey/calibration + installation/training/lifecycle support. INR 246,950 is not a per-dumper rollout price.

## L. Budget and unchanged selections

| Cost item | INR |
|---|---:|
| Existing F01–F27 allocation | 231950 |
| Added hardware | 0 |
| Removed hardware | 0 |
| Unspent price/integration reserve | 15000 |
| Final planning allocation | 246950 |
| Hard ceiling | 250000 |
| Unallocated headroom outside reserve | 3050 |

No savings, current checkout prices, shipping costs or supplier availability are invented. Reserve remains unspent. Exact quotes, regional parts, custom fabrication/protection details and lab access remain purchase-release gates; no delivery questions or supplier contacts were made.

## M. Closeout and retained gates

Selection changes: **zero**. Purchases: **zero**. Hardware access: **none**. Software/firmware edits: **none**. Existing F0 documents: preserved. The three new audit files supplement them, with no claim that G01–G14 have passed.

Before fabrication/use, close the already-recorded gates for exact revisions/pinouts, new cart mechanics/brakes, guarded power/protection, radar firmware/profile/RF authorization, Hailo workload, GNSS corrections/antenna/UART details, metrology carrier, USB/display arrangement, node-B power, lab access, calibration and software integration. These are essential work within the selected architecture, not invitations to add premium hardware.

**Final status: capability/BOM selection frozen with no upgrade; fabrication and commissioning remain gated.** Do not reopen hardware selection without a documented failed requirement, a changed operational domain or verified component incompatibility. No hardware or software test was performed by this documentary audit.

## N. Document checks completed

- 30 feature-matrix rows cover all ten requested groups A–J; each row has the nine required columns.
- All 30 candidate additions have exactly one classification: 1 REQUIRED NOW (already present), 11 INDUSTRIAL ONLY and 18 NOT REQUIRED.
- All 27 original BOM cost rows reconcile quantity × unit cost. Base INR 231,950 plus INR 15,000 reserve totals INR 246,950, leaving INR 3,050 outside reserve.
- Storage examples independently recalculated; they remain assumptions rather than benchmark results.
- The CSV has the nine requested fields and one zero-addition record. Export/import round-trip comparison passed; rendered preview inspected for clipping.
- Relative links in the two new reports resolve. SHA-256 comparison confirms all six original F0 documents unchanged.
- Tracked and staged Git diffs remained empty. Only the three requested new deliverables were added inside the flagship package; the authoring/check script and preview are outside the application tree.
- No application regression suite, physical test, device access, purchase, commit or push was performed. Document checks do not verify the unbuilt system.
