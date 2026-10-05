# Independent exported-artifact audit

This checker reads saved artifacts and separately specified approved mappings. It does not import the drawing generator. It is a second-method automated review by the same authoring agent, not a second engineer certification.

| Check | Result | Evidence |
| --- | --- | --- |
| Export IDs unique | PASS | 49 scheduled physical connections, no duplicate ID. |
| Approved shared node | PASS | C01/C02 approved F1 common node only. |
| Downstream traction node | PASS | No upstream member. |
| Post-protection logic node | PASS | Only after F2. |
| F3 dedicated net | PASS | ES1 output is a separate net, N-ESTOP-SWITCHED+. |
| Separate returns | PASS | No invented common return or converter internal bridge. |
| Pi golden allocation | PASS | All 8 specified physical pins. |
| Pi complete official header | PASS | S7 official Pi 4 datasheet release 1.1, Figure 3 p9 visually checked; 40/40 functions. |
| Pi unused external positions | PASS | 32 new documentation rows; zero added conductors. |
| Logic ground resolved identities | PASS | Exactly the five controlled physical identifiers; no hardware compatibility claim. |
| Logic ground physical holds | PASS | Four specified sensor/encoder grounds plus functional converter source. None counted as a resolved physical CAD terminal. |
| Physical resolution count reconciliation | PASS | Functional members and resolved identifiers are distinct for all 31 nets. |
| ESP32 full golden allocation | PASS | All 22 positions, ordered, including 11 unallocated. |
| MDD10A golden allocation | PASS | Five logic pins plus six power/motor terminals. |
| LD2450 golden allocation | PASS | Four pins; electrical compatibility remains H16. |
| I2C SDA | PASS | One shared bus node, two sensor endpoints. |
| I2C SDA physical identities | PASS | Functional shared node retained; physical module pins TBD / VERIFY. |
| I2C SCL | PASS | One shared bus node, two sensor endpoints. |
| I2C SCL physical identities | PASS | Functional shared node retained; physical module pins TBD / VERIFY. |
| UART crossover | PASS | TX to RX in both directions. |
| PWM1 endpoints | PASS | Source-approved mapping. |
| DIR1 endpoints | PASS | Source-approved mapping. |
| PWM2 endpoints | PASS | Source-approved mapping. |
| DIR2 endpoints | PASS | Source-approved mapping. |
| Encoder LA | PASS | VCC, interface, polarity, connector numbering remain HOLD. |
| Encoder LB | PASS | VCC, interface, polarity, connector numbering remain HOLD. |
| Encoder RA | PASS | VCC, interface, polarity, connector numbering remain HOLD. |
| Encoder RB | PASS | VCC, interface, polarity, connector numbering remain HOLD. |
| Coil suppression | PASS | Two separate terminals; return termination not invented. |
| GPIO13 diagnostic only | PASS | Not in primary safety-current chain. |
| Unknown supplies open | PASS | No fabricated voltage/net assignment. |
| Phase 1 restriction | PASS | Documented output restriction unchanged, no hardware access. |
| CSV exact export | PASS | 49 physical rows plus one explicitly documentation-only open return. |
| XLSX exact schedule | PASS | All 49 rows and the first 13 exact controlled fields. Notes are uniform caveats. |
| XLSX full pin table | PASS | All 93 pin/functional port rows match JSON, including full Pi header. |
| XLSX holds | PASS | 27 records; original 26 dispositions unchanged, H27 documents unused Pi positions. |
| XLSX endpoint resolution | PASS | Explicit source/destination physical identity status. |
| XLSX net resolution register | PASS | Separate counts and member lists; isolated input HOLD retained. |
| Frozen topology preserved | PASS | All 49 conductor/cable identities, endpoints, nets and components unchanged from original Rev 1.0 ZIP. |
| Only approved open-net rename | PASS | All 31 node memberships identical; only singleton PS1 IN- net name changed. |
| Original HOLD dispositions retained | PASS | No original HOLD converted into a released connection. |
| Unrelated PCB workbook preserved | PASS | Untouched PCB tab values, cell styles, tables and panes retained on workbook import/export. |
| PDF five A1 pages | PASS | 841 x 594 mm, landscape, vector text/lines. |
| Each physical ID visible once | PASS | Full ID labels appear once in detailed sheets; overview has range references. |
| Visible SVG bidirectional paths | PASS | 49/49 actual line endpoints and visible labels matched, not metadata-only. |
| Master net references resolve | PASS | All exact master net references resolve on detailed sheets. |
| Safety legends on every page | PASS | No as-built or hardware verification assertion. |
| Independent mechanical linkage | PASS | Actuator to contact function only; separate y from coil/return, no junction dot. |
| Software arrows have no wire IDs | PASS | HMI/GNSS/software arrows are not copper nets. |
| Required trace 01 | PASS | F1 OUT <-> K1 MAIN IN; W-PWR-003 |
| Required trace 02 | PASS | F1 OUT <-> F2 IN; W-PWR-004 |
| Required trace 03 | PASS | F2 OUT <-> PS1 IN+; W-LOGIC-001 |
| Required trace 04 | PASS | K1 MAIN OUT <-> U3 T3; W-PWR-006 |
| Required trace 05 | PASS | U3 T1 <-> Left M1B; W-M1-B |
| Required trace 06 | PASS | U3 T2 <-> Left M1A; W-M1-A |
| Required trace 07 | PASS | U3 T5 <-> Right M2A; W-M2-A |
| Required trace 08 | PASS | U3 T6 <-> Right M2B; W-M2-B |
| Required trace 09 | PASS | J1-15 <-> MDD P4; W-PWM1 |
| Required trace 10 | PASS | J1-16 <-> MDD P5; W-DIR1 |
| Required trace 11 | PASS | J1-17 <-> MDD P2; W-PWM2 |
| Required trace 12 | PASS | J1-18 <-> MDD P3; W-DIR2 |
| Required trace 13 | PASS | Pi Pin 10 <-> LD2450 TX; W-RAD-001 |
| Required trace 14 | PASS | Pi Pin 8 <-> LD2450 RX; W-RAD-002 |
| Required trace 15 | PASS | Pi Pin 3 <-> I2C-SDA, both sensor branches; W-I2C-SDA-01, W-I2C-SDA-02 |
| Required trace 16 | PASS | Pi Pin 5 <-> I2C-SCL, both sensor branches; W-I2C-SCL-01, W-I2C-SCL-02 |
| Required trace 17 | PASS | Pi Pin 2 <-> N-LOGIC5+; W-LOGIC-002 |
| Required trace 18 | PASS | ESP32 J1-21 <-> N-LOGIC5+; W-LOGIC-003 |
| Required trace 19 | PASS | Physical ES1 <-> CD1 <-> K1 coil control path; W-ESTOP-001, W-ESTOP-002, W-ESTOP-003 |
| Required trace 20 | PASS | K1 AUX <-> SC1 <-> GPIO13 diagnostic path; W-K1-AUX-RAW, W-K1-AUX |
| K1 functional-interface warning | PASS | Explicit purchased-datasheet and pre-energization gate beside the coil. |
