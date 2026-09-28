# Canonical node table

Membership is functional connection intent, not a resolved physical CAD terminal or hardware compatibility proof. RESOLVED means only a controlled physical identifier; purchased hardware verification still applies. HOLD members are excluded from resolved counts. PS1 OUT- remains a functional source on N-LOGIC-GND, but its physical terminal identity is HOLD.

| ID | Net | Resolved count | Resolved identifiers | HOLD count | HOLD / PHYSICAL PIN VERIFY |
| --- | --- | --- | --- | --- | --- |
| N001 | N-BAT+ | 0 |  | 2 | B1.positive (vendor terminal TBD); BMS.battery positive input (TBD) |
| N002 | N-BMS+ | 0 |  | 2 | BMS.protected positive output (TBD); F1.IN (terminal TBD) |
| N003 | N-PROTECTED12+ | 0 |  | 4 | F1.OUT (terminal TBD); F2.IN (terminal TBD); F3.IN (terminal TBD); K1.MAIN IN (terminal TBD) |
| N004 | N-TRACTION12+ | 1 | U3.T3 POWER+ | 1 | K1.MAIN OUT (terminal TBD) |
| N005 | N-TRACTION- | 1 | U3.T4 POWER- | 2 | B1.negative (vendor terminal TBD); BMS.negative reference (TBD) |
| N006 | N-LOGIC12+ | 0 |  | 2 | F2.OUT (terminal TBD); PS1.IN+ |
| N007 | N-LOGIC5+ | 3 | LD2450.Pin 1 VCC; U1.Pin 2 5V; U2.J1-21 5V | 1 | PS1.OUT+ |
| N008 | N-LOGIC-GND | 5 | LD2450.Pin 2 GND; U1.Pin 20 GND; U1.Pin 6 GND; U2.J1-22 GND; U3.P1 GND | 5 | BNO055.GND (pin TBD); ENC-L.GND (pin TBD); ENC-R.GND (pin TBD); MLX90640.GND (pin TBD); PS1.OUT- |
| N009 | N-ESTOP-FUSED+ | 0 |  | 2 | ES1.NC IN (terminal TBD); F3.OUT (terminal TBD) |
| N010 | N-ESTOP-SWITCHED+ | 0 |  | 2 | CD1.control/supply IN (TBD); ES1.NC OUT (terminal TBD) |
| N011 | K1-COIL+ | 0 |  | 3 | CD1.coil OUT (terminal TBD); D1/S1.coil-side terminal (TBD); K1.COIL A (terminal TBD) |
| N012 | K1-COIL- | 0 |  | 2 | D1/S1.return-side terminal (TBD); K1.COIL B (terminal TBD) |
| N013 | K1-AUX-RAW | 0 |  | 2 | K1.AUX signal terminal (TBD); SC1.IN (terminal TBD) |
| N014 | ESTOP-AUX-STATUS | 1 | U2.J1-19 GPIO13 | 1 | SC1.OUT (terminal TBD) |
| N015 | I2C-SDA | 1 | U1.Pin 3 GPIO2 SDA | 2 | BNO055.SDA (pin TBD); MLX90640.SDA (pin TBD) |
| N016 | I2C-SCL | 1 | U1.Pin 5 GPIO3 SCL | 2 | BNO055.SCL (pin TBD); MLX90640.SCL (pin TBD) |
| N017 | RADAR-TX | 2 | LD2450.Pin 3 TX; U1.Pin 10 GPIO15 RX | 0 |  |
| N018 | RADAR-RX | 2 | LD2450.Pin 4 RX; U1.Pin 8 GPIO14 TX | 0 |  |
| N019 | ESP-PWM1 | 2 | U2.J1-15 GPIO9; U3.P4 PWM1 | 0 |  |
| N020 | ESP-DIR1 | 2 | U2.J1-16 GPIO10; U3.P5 DIR1 | 0 |  |
| N021 | ESP-PWM2 | 2 | U2.J1-17 GPIO11; U3.P2 PWM2 | 0 |  |
| N022 | ESP-DIR2 | 2 | U2.J1-18 GPIO12; U3.P3 DIR2 | 0 |  |
| N023 | ENC-L-A | 1 | U2.J1-4 GPIO4 | 1 | ENC-L.A (pin TBD) |
| N024 | ENC-L-B | 1 | U2.J1-5 GPIO5 | 1 | ENC-L.B (pin TBD) |
| N025 | ENC-R-A | 1 | U2.J1-6 GPIO6 | 1 | ENC-R.A (pin TBD) |
| N026 | ENC-R-B | 1 | U2.J1-7 GPIO7 | 1 | ENC-R.B (pin TBD) |
| N027 | M1A | 1 | U3.T2 M1A | 1 | M1.M1A (terminal TBD) |
| N028 | M1B | 1 | U3.T1 M1B | 1 | M1.M1B (terminal TBD) |
| N029 | M2A | 1 | U3.T5 M2A | 1 | M2.M2A (terminal TBD) |
| N030 | M2B | 1 | U3.T6 M2B | 1 | M2.M2B (terminal TBD) |
| N031 | PS1-IN-RETURN-HOLD | 0 |  | 1 | PS1.IN- |
