# TARK maturity matrix

Release: **TARK PHASE-1 SOFTWARE EVIDENCE RELEASE R1**.
“yes” means the stated scoped property, not the entire subsystem. No percentage
or numerical maturity score. Physical validation is pending even where software
tests pass. Research studies are separate from production implementation.

| Subsystem | DESIGNED | IMPLEMENTED | DEMONSTRATED | SOFTWARE-VERIFIED | PHYSICAL-VALIDATION-PENDING | HOLD / VERIFY | Evidence source | Current limitation |
|---|---|---|---|---|---|---|---|---|
| LD2450 parser/adapter | yes | yes | fixture | bounded decoder tests | yes | purchased format/identity | C01–02 | no physical capture |
| Radar tracking | yes | slot updates | fixture | specified update/freshness cases | yes | physical target association | C03–04 | not persistent-object EKF |
| Health/freshness | yes | yes | production-path fixture | yes | timing on hardware | clock source | C05–07 | AGING can retain NORMAL |
| Runtime/observers | yes | single owner | REST/WS fixtures | yes | host deployment load | one-worker rule | C08–09 | not distributed runtime |
| PV-SOE/stopping | provisional | provisional | fixture | implemented formula/branches | yes | calibrated envelope/parameters | C10–12 | assumed speed zero |
| TTC | helper | helper only | unit scope | helper cases only | future policy review | no production integration | C13–14 | NOT COMPUTED in HMI |
| WARN | vocabulary | no policy branch | no production policy | not claimed | policy review | thresholds undefined | C15 | no executable semantics |
| RGB | interface | lifecycle/library | mocked | yes | yes | device/optics | C16 | no real frames |
| Thermal | interface | lifecycle/library | mocked | validation/lifecycle | yes | breakout/calibration | C17 | no measured temperatures |
| IMU | interface | lifecycle/library | mocked | validation/lifecycle | yes | identity/mounting | C18 | not fused into decision |
| Multisensor fusion | concept | no production fusion | separate study only | not production | yes | integration/model review | C19 | observations separate |
| EKF/adaptive covariance | research | separate study | archived simulation | not R1 production coverage | yes | synthetic quality | C20–21 | condition-dependent results |
| GNSS/location | yes | yes | mocked/simulated | software contracts | yes | receiver/antenna | C22 | no RTK/accuracy claim |
| Map/browser location | yes | yes | software tests | lifecycle/separation | physical GNSS pending | provider availability | C23–24 | advisory only |
| Event/record persistence | yes | yes | software sessions | tested cases | operational soak pending | retention limits | C25–26 | not signed provenance |
| Replay | yes | format 2 | 20 saved scenarios | compared fields | not physical evidence | legacy sessions | C27 | MATCH scoped |
| Protocol V2 / Pi client | yes | yes | Python/C interop | 36 shared vectors + regressions | yes | physical link | C28–29 | not authentication |
| Firmware parser/service | yes | portable C | fresh host tests | yes | board pending | board binding | C30–32 | not ESP-IDF flash |
| Hardware watchdog | architecture | portable supervision only | host timer behavior | not hardware behavior | yes | SDK/scheduler/reset | C33 | actual binding absent |
| Encoder | contract | counts/fault interface | fixtures | yes | yes | voltage/pulses/polarity | C34–35 | wheel response only |
| MDD10A | interface | disabled/simulator | host tests | zero boundary | yes | board/load/wiring | C36–37 | no PWM claim |
| E-stop/K1 | electrical intent | design only | drawing audits | not physical | yes | H11–H15 | C38–41 | no energization |
| Phase-1 traction | disabled policy | zero | full suite/scenarios | yes | future control phase | no traction approval | C42 | no vehicle motion |
| Vehicle/braking/fog | concept/plan | not built here | no physical evidence | not applicable | yes | measured validation | C43–45 | no physical result |
| Dashboard/demo | yes | yes | tests/historical captures | local HMI tests | no vehicle linked | external revision unknown | C46–47 | R1 not deployed |
| Simulation/evidence | yes | yes | 150 repetitions | 70 harness tests | not hardware evidence | modeled scope | C48–49 | not universal proof |
| Electrical/BOM/PCB | controlled design | logical definitions | export audits | no native CAD ERC | yes | 27 HOLDs | C56–57 | no fabrication release |
| Certification/autonomy | not current scope | not claimed | none | none | outside R1 | separate programme | C50–51 | no mine readiness |

Claim IDs link conceptually to the [full claim matrix](TARK_CLAIM_EVIDENCE_MATRIX.md),
which supplies exact source paths, evidence types, permissible wording and limits.
