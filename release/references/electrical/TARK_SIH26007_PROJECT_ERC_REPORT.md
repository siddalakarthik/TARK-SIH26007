# Project electrical connectivity rules

These are reproducible graph/schema checks, not KiCad/native CAD ERC. No pin-type, voltage-limit or device-internal model is available. Native CAD ERC was not run because KiCad is not installed; that gate remains NOT RUN.

| Rule | Result | Evidence |
| --- | --- | --- |
| Unique connection IDs | PASS | Every conductor/cable schedule row occurs once. |
| One net per terminal | PASS | Separate series-device terminals remain distinct. |
| K1 isolates traction nets | PASS | N-TRACTION12+ is downstream only. |
| Post-F2 logic name | PASS | F2 output is logic supply; F1 output is N-PROTECTED12+. |
| F1 common protected node | PASS | Exact approved node membership. |
| No return bridge | PASS | No common terminal or new wire bridges these domains. |
| DC-DC IN-/OUT- separate | PASS | IN- source explicitly unassigned. |
| Suppression across both coil terminals | PASS | No diode polarity/value invented. |
| GPIO13 diagnostic only | PASS | GPIO13 absent from coil and traction nets. |
| Pi Pin 1 unconnected | PASS | NO EXTERNAL POWER retained. |
| All 22 J1 rows | PASS | Unallocated identities not invented. |
| All 40 Pi header positions | PASS | Official S7 physical header; existing 8 controlled rows unchanged. |
| Unallocated Pi positions unconnected | PASS | 32 unallocated positions remain DO NOT CONNECT. |
| Resolved versus HOLD terminal counts | PASS | Logic GND: five controlled physical identifiers; four sensor/encoder and PS1 OUT- physical interfaces held. |
| Unallocated J1 unconnected | PASS | Positions 1,2,3,8,9,10,11,12,13,14,20 DNC. |
| No unknown VCC assignment | PASS | Unknown sensor/encoder supplies stay open. |
| Two shared I2C nodes | PASS | Each node has Pi plus two sensor terminals. |
| No unauthorized component | PASS | New document IDs only identify existing components. |
| Drawing vs netlist physical rows | PASS | Every connection rendered once in detailed lanes. Master and overview repeat references only. |
| Five sheets and numbering | PASS | Exactly five A1 landscape sheets. |
| Geometric text/wire collision audit | PASS | 0 findings; detailed in QA evidence. |

## Findings classification

REAL ERROR: 0 project-check failures.

TBD: 27 controlled hold records; electrical ratings, part terminals and compatibility are unresolved.

EXPECTED / DOCUMENTED: open PS1 IN-; coil return unresolved; sensor and encoder VCC open; unallocated J1 positions unconnected; PCB not fabricated.

FALSE POSITIVE: none claimed.
