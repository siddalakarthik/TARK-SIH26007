# Do not connect and hold register

| ID | Item | Status | Required evidence |
| --- | --- | --- | --- |
| H01 | U1 Pin 1 | NO EXTERNAL POWER | Pi Pin 1 must have no external power net. |
| H02 | U2 J1 unallocated | DO NOT CONNECT | J1 positions 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 20; no new GPIO identities assigned. |
| H03 | B1 / BMS | TBD / VERIFY | Battery/BMS variant, terminal identity, current rating and actual protection topology. |
| H04 | F1 / F2 / F3 | TBD / VERIFY | Fuse ratings, holders, interruption ratings and protected load calculations. |
| H05 | PS1 | TBD / VERIFY | PS1-IN-RETURN-HOLD is the isolated IN- stub, source open. OUT- remains N-LOGIC-GND; its physical terminal identity is HOLD. Verify topology, ratings, polarity and regulation. |
| H06 | U1 / U2 power | TBD / VERIFY | Approved 5 V powering method, USB backfeed behavior and current capacity. |
| H07 | ENC-L VCC / signals | TBD / VERIFY | No VCC net; verify output interface, ground reference, polarity and pin numbering. |
| H08 | ENC-R VCC / signals | TBD / VERIFY | No VCC net; verify output interface, ground reference, polarity and pin numbering. |
| H09 | MLX90640 VCC / I2C / GND | TBD / VERIFY | SDA/SCL/GND: HOLD / PHYSICAL PIN VERIFY. VCC/VIN, pullup voltage, address and purchased D55 breakout pins remain unverified. |
| H10 | BNO055 VCC / I2C / GND | TBD / VERIFY | SDA/SCL/GND: HOLD / PHYSICAL PIN VERIFY. VCC/VIN, pullup voltage, address and purchased breakout pins; calibration pending. |
| H11 | K1 coil | TBD / VERIFY | DESIGN HOLD — DO NOT ENERGIZE. Exact coil voltage/current and driver, coil return, suppression polarity/component must be verified from purchased contactor/driver before energization. Coil A/B and MAIN IN/OUT are functional interfaces, not terminal numbers. Coil polarity, duty and markings remain TBD. |
| H12 | CD1 and coil return | TBD / VERIFY | Driver circuit, supply/return topology and coil return termination. No internal design invented. |
| H13 | K1 main contact / U3 T3 | HOLD | T3 must remain disconnected until physical E-stop isolation is verified; NO PHYSICAL TRACTION AUTHORIZATION. |
| H14 | D1/S1 suppression | TBD / VERIFY | Type, value, rating and polarity. Only the parallel connection intent is defined. |
| H15 | K1 auxiliary / SC1 | TBD / VERIFY | NO/NC choice, excitation/reference, power, signal conditioning and GPIO13 levels. |
| H16 | LD2450 interface | TBD / VERIFY | Exact purchased connector orientation and TX/RX electrical compatibility; 256000 8N1 controlled. |
| H17 | CAM1 | TBD / VERIFY | Purchased camera model, USB/UVC cable and connector; no GPIO pins allocated. |
| H18 | USB interfaces | TBD / VERIFY | Port/cable identities and simultaneous power paths; USB assembly internals not assigned. |
| H19 | GNSS1 / ANT1 | TBD / VERIFY | LC29H(AA) USB path, baud, NMEA, antenna connector and compatibility; physical evidence pending. |
| H20 | U2 / U3 | TBD / VERIFY | Purchased board revisions, printed pin/terminal markings and logic levels. |
| H21 | M1 / M2 | TBD / VERIFY | Motor ratings, terminal/polarity identity and mechanical direction; no current or speed assumed. |
| H22 | Harnesses / connectors | TBD / VERIFY | Wire gauge, length, connector variant/pitch, crimps and ratings. |
| H23 | PCB footprints | TBD / VERIFY | Manufacturer footprints and actual connector pinouts unavailable; no fabrication file. |
| H24 | PCB mechanics | TBD / VERIFY | Board dimensions, mounting holes, enclosure and connector locations. |
| H25 | PCB routing classes | TBD / VERIFY | Trace widths, clearances, stackup and allowed currents require physical/electrical data. |
| H26 | Pi to ESP32 transport | TBD / VERIFY | Configured serial software boundary only; no physical GPIO or cable assignment in this package. |
| H27 | U1 unallocated header | DO NOT CONNECT | All 32 header positions without a controlled TARK allocation remain UNALLOCATED / DO NOT CONNECT; full 40-position table on S3. Pin 1 separately remains NO EXTERNAL POWER (H01). |
