# Batch A exclusions

Revision A0, 1 October 2026. These exclusions define the assessed student scope; they do not authorize the unclosed included design. Nothing is discarded physically by this document.

| Hardware / role | Decision | Reason |
|---|---|---|
| LiDAR | EXCLUDED | Not needed to establish the selected complementary radar/RGB/thermal research channels; adds integration and cost without closing a mandatory gap |
| Second premium radar | EXCLUDED | One characterized primary radar is the scope; duplicated hardware does not imply coverage or redundancy |
| Second premium thermal camera | EXCLUDED | One complete thermal acquisition path suffices for the current experiment |
| Premium planetary/synchronous motors | EXCLUDED | No demonstrated requirement to replace the existing four TT motors; current rating evidence must be obtained first |
| Decorative replacement metal chassis | EXCLUDED | Reuse must be evaluated before replacing structure for appearance; mounting/guard reserve remains |
| Autonomous steering actuator | EXCLUDED | Not required for the controlled student assistance demonstrator |
| Heavy-vehicle brake actuator | EXCLUDED | No OEM approval, HEMM interface design or safe authority for such a system |
| C-V2X development kit | EXCLUDED | Local two-node telemetry does not require cellular V2X hardware |
| LoRa radio | EXCLUDED | Local Wi-Fi is the selected communication technology; no separate low-bandwidth range requirement established |
| 4G/LTE modem and subscription | EXCLUDED | The local demo must run without WAN; no assumed external NTRIP dependency |
| Additional supervisory MCU | EXCLUDED | Existing ESP32 role retained; no second endpoint owner justified |
| Second Jetson | EXCLUDED | Pi handles node-B relay, existing PC handles base/control room |
| Custom PCB at this stage | EXCLUDED | Interfaces, power and purchased variants are not frozen |
| Burnt LM2596 | EXCLUDED permanently | User reports damage; never reuse, test as a working converter, or include in spare inventory |
| Existing red switch as rated traction cutoff | EXCLUDED from cutoff chain | No verified DC rating/action type; kept in owned inventory only |
| Existing JQC-3FC/T73 relay as rated traction cutoff | EXCLUDED from cutoff chain | Unverified manufacturer/pinout/contact rating; not a complete coil-driver/cutoff assembly |
| AWR1843BOOST substitution | EXCLUDED | IWR1843BOOST is the assessed exact primary radar; no silent automotive/industrial variant switch |
| DCA1000/raw ADC capture hardware | EXCLUDED | Selected architecture uses documented processed USB-UART outputs, not raw ADC collection |
| Separate XDS debugger/carrier for IWR1843BOOST | EXCLUDED | Onboard debug/USB-UART serves the selected use; additional boards would be unnecessary cost |
| LC29H(AA) as an RTK receiver | EXCLUDED from RTK design | Variant name is not evidence of RTK rover/base capability |
| MLX90640 thermal alternative | EXCLUDED from this assessed flagship BOM | Current thermal choice is Lepton assembly; any budget-driven resolution reduction requires explicit requirement/decision revision |
| Pi 3B+ as main simultaneous perception computer | EXCLUDED from main-compute role | No demonstrated concurrent inference/recording capacity for the intended workload; retained as node-B controller |
| Existing webcam as exact flagship RGB model | EXCLUDED from primary-perception role | Identity/optics unverified; retained as bench asset A24 |
| LD2450 as second active flagship safety radar | EXCLUDED from active primary path | Retained as bench comparison A17 without claiming industrial equivalence |
| 32 GB owned card as Jetson main recorder | EXCLUDED from that role | Allocated to Pi node B; cannot be in two computers or stand in for unbudgeted recording capacity |
| SLA battery as assumed onboard compute supply | EXCLUDED from that role | Capacity, payload and energy conversion are not established; retained bench asset A22 |
| Replacement MDD10A inferred from older documents | EXCLUDED from this current design | The actual reported robot uses L298N; no automatic restoration of obsolete topology |

An exclusion of an unverified component from a safety role does not mean that role is satisfied. GAP-CUTOFF remains open.
