# Historical slide-text inventory

Read-only OOXML text extraction; no binary modified. None of these decks is
software/electrical authority. All three six-slide variants are covered by the
[current patch sheet](../../../docs/PPT_CLAIM_PATCH_SHEET.md). Source filenames
are artifact identifiers, not required machine paths. No filename/date is used
to overrule source-code evidence. Text in images is outside this extraction.

## TARK_SIH26007_PRE.pptx

SHA-256: `9e04ad76a6fa636ea0039a92c235826f619c21acdb3b30e7da253c0247bbdacd`.

### Slide 1

> Proposed hardware arrangement
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware .  TITLE Title Page
>
> 01
>
> SMART INDIA HACKATHON 2026
>
> PROBLEM STATEMENT ID
>
> SIH26007
>
> THEME
>
> Smart Automation
>
> CATEGORY
>
> Hardware
>
> TEAM NAME
>
> TARK
>
> PROBLEM STATEMENT
>
> PROPOSED SOLUTION
>
> PERCEPTION-VERIFIED SAFETY ASSISTANCE
>
> FOR OPEN-CAST MINE VEHICLES
>
> Multi-sensor perception  +  risk-aware operating envelope  +  independent safety control
>
> TEAM ID
>
> 155480
>
> “Safe and Efficient Operation of Mine Vehicles in Fog and Low-Visibility Conditions
>
>  in Open Cast Iron Ore Mines.”
>
> SMART INDIA
HACKATHON 2026
>
> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 01

### Slide 2

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 02
>
> Proposed Solution
>
> Complementary sensing plus a reliability check before the vehicle is allowed to continue
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Proposed Solution
>
> 02
>
> HOW THE REASONING FLOWS
>
> Low visibility (fog)
>
> ⌄
>
> Visible-light perception becomes less reliable
>
> ⌄
>
> People / vehicles / obstacles become harder to observe
>
> ⌄
>
> System checks sensor health and observability
>
> ⌄
>
> Fuses complementary sensing (radar + thermal + RGB)
>
> ⌄
>
> Tracks hazards and relative motion
>
> ⌄
>
> Calculates TTC and stopping requirement
>
> ⌄
>
> Evaluates Perception-Verified Safe Operating Envelope
>
> NORMAL
>
> ›
>
> WARN
>
> ›
>
> RESTRICT
>
> ›
>
> STOP
>
> CORE IDEA
>
> We are not only detecting obstacles; we are deciding whether the available perception is reliable enough for the vehicle to safely continue.
>
> CORE HARDWARE
>
> HLK-LD2450
>
> 24 GHz tracking radar
>
> MLX90640-D55
>
> 32×24 thermal array
>
> RGB Camera
>
> 1080p USB/UVC
>
> BNO055 + Encoders
>
> Orientation + ego-motion
>
> This is a proposed system-level differentiation, not a claim that radar, thermal sensing or fusion are individually novel.
>
> GNSS (LC29H·AA) supports route/location context only — never a collision-safety input.
>
> SMART INDIA
HACKATHON 2026

### Slide 3

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 03
>
> Technical Approach
>
> Sensing  →  Edge Perception  →  Safety Control  →  Actuation
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Technical Approach
>
> 03
>
> HLK-LD2450
>
> 24 GHz tracking radar
>
> MLX90640-D55
>
> 32×24 thermal array
>
> RGB Camera
>
> 1080p USB/UVC
>
> BNO055 IMU
>
> LC29H(AA)
>
> + wheel encoders
>
> Dual-band GNSS receiver
>
> ▼
>
> RASPBERRY PI 4  —  EDGE PERCEPTION COMPUTE
>
> Timestamping
>
> ›
>
> Sensor health / observability
>
> ›
>
> Detection / target extraction
>
> ›
>
> Track-level EKF
>
> Fixed vs. adaptive covariance
>
> ›
>
> Relative velocity
>
> ›
>
> TTC / stopping requirement
>
> ›
>
> PV-SOE state
>
> NORMAL
>
> ›
>
> WARN
>
> ›
>
> RESTRICT
>
> ›
>
> STOP
>
> ▼  bounded command · heartbeat · timeout · CRC check · watchdog
>
> ESP32-S3
>
> Bounded control · watchdog
>
> Cytron MDD10A
>
> Dual-channel motor driver
>
> 4-wheel vehicle
>
> Differential-driver prototype
>
> INDEPENDENT SAFETY BACKSTOP
>
> Physical E-stop → DC contactor → traction isolated. Independent of Pi / ESP32-S3 software path.
>
> OBSERVATION / HMI PATH
>
> TARK Digital HMI
>
> WebSocket Telemetry
>
> TARK Backend (FastAPI)
>
> Raspberry Pi 4
>
> ⌄
>
> ⌄
>
> ⌄
>
> EKF itself is a standard estimator. Our experimental focus is FIXED covariance vs QUALITY-ADAPTIVE covariance.
>
> Pi = perception + reasoning   |   ESP32-S3 = bounded control + watchdog   |   E-stop = physical isolation
>
> SMART INDIA
>
> HACKATHON 2026
>
> Dashboard · Map · Sensors · Safety · Replay · Logs
>
> MONITORING ONLY · NO BROWSER MOTION AUTHORITY — dashboard path never reaches the motors.

### Slide 4

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 04
>
> Feasibility and Viability
>
> Hardware, software, safety and validation, staged toward a future controlled mine pilot
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Feasibility and Viability
>
> 04
>
> HARDWARE
>
> Low-cost radar, thermal array, RGB baseline
>
> Raspberry Pi 4 edge compute
>
> ESP32-S3 bounded controller
>
> Cytron MDD10A dual motor driver
>
> 4-wheel differential-drive platform
>
> BNO055 IMU + GNSS (LC29H·AA)
>
> SOFTWARE
>
> Sensor acquisition & timestamping
>
> Quality / observability layer
>
> Tracking (EKF)
>
> Adaptive uncertainty fusion
>
> TTC + stopping requirement
>
> PV-SOE state machine
>
> Localization · dashboard · FastAPI/WebSocket backend
>
> SAFETY
>
> Independent MCU (ESP32-S3)
>
> Heartbeat watchdog
>
> Bounded commands
>
> Degraded operating modes
>
> Hardware E-stop + traction isolation
>
> DIGITAL DEMONSTRATION + VALIDATION
>
> Simulation 1 — PV-SOE / stopping envelope
>
> Simulation 2 — fixed vs adaptive fusion
>
> Simulation 3 — fault injection / safe-state
>
> Planned: degraded-visibility testing + ground-truth metrics
>
> Deployed — public sim/monitoring demo
>
> Traction: DISABLED_PHASE_1 (safe-state)
>
> DEVELOPMENT ROADMAP
>
> CONCEPT
>
> ›
>
> NUMERICAL
>
> SIMULATION
>
> ›
>
> BENCH SENSOR
>
> INTEGRATION
>
> ›
>
> VEHICLE
>
> PROTOTYPE
>
> ›
>
> DEGRADED-
>
> VISIBILITY TEST
>
> ›
>
> VALIDATION
>
> ›
>
> FUTURE ENGINEERING /
>
> MINE PILOT
>
> Physical prototype, fog chamber and measured performance are future work — not part of this submission.
>
> SMART INDIA
>
> HACKATHON 2026
>
> TARK DIGITAL HMI
>
> LIVE SOFTWARE DEMONSTRATOR
>
> tark-sih26007-demo.onrender.com
>
> ● ● ●
>
> LIVE DASHBOARD SCREENSHOT
>
> To be inserted from the verified deployment before submission
>
> ✓  Real-time telemetry
>
> ✓  Sensor health
>
> ✓  Safety state
>
> ✓  Map / localization
>
> ✓  Radar local view
>
> ✓  Replay / evidence
>
> PUBLIC DEMO · SIMULATION · TRACTION DISABLED
>
> LIVE SOFTWARE DEMO →  tark-sih26007-demo.onrender.com
>
> SOFTWARE BASELINE — frozen 2d319e7
>
> 97 backend tests · 25 frontend tests · TypeScript/build passed · firmware host tests passed

### Slide 5

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 05
>
> Impact and Benefits
>
> What the proposed system is designed to improve
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Impact and Benefits
>
> 05
>
> 01
>
> 04
>
> IMPROVED OPERATOR AWARENESS
>
> FAIL-SAFE BOUNDED CONTROL
>
> Useful hazard information when visible-light perception degrades.
>
> Independent MCU, watchdog, command bounds and a physical E-stop.
>
> 02
>
> 05
>
> COMPLEMENTARY PERCEPTION
>
> LOCALIZATION + CONTEXT
>
> Radar, thermal and RGB provide different information under poor visibility.
>
> GNSS supports route/map context only never collision-safety authority.
>
> 03
>
> 06
>
> RISK-AWARE OPERATING ENVELOPE
>
> COST-CONSCIOUS SCALABILITY
>
> Permitted operation becomes more conservative when perception or stopping margin becomes inadequate.
>
> Low-cost prototype is designed to validate the architecture; higher-grade industrial sensors can be introduced later without changing the core safety-decision concept.
>
> WHAT THIS PROTOTYPE IS NOT
>
> ✕  Not a full-size HEMM controller
>
> ✕  Not autonomous steering
>
> ✕  Not a production mine safety system
>
> ✕  Not mine-certified equipment
>
> ✕  Not a guarantee of collision prevention
>
> The operator remains part of the control loop at all times.
>
> SMART INDIA
HACKATHON 2026
>
> CONCEPTUAL PROTOTYPE — PROPOSED HARDWARE ARRANGEMENT
>
> ≤ ₹60,000
>
> Maximum planning ceiling for the scaled prototype, controlled test setup and contingency — prototype subtotal ₹52,750 + GNSS module ≈₹4,522 + ₹2,250 contingency ≈ ₹59,522.
>
> BNO055
>
> Bounded Controller

### Slide 6

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 06
>
> Research, References & Detailed Resources
>
> Standards, peer-reviewed research, current hardware references and detailed project documentation
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Research, References & Resources
>
> 06
>
> TECHNICAL REFERENCES
>
> ISO STANDARD
>
> ISO 21815-1:2022
>
> Earth-moving machinery — Collision warning and avoidance — Part 1: General requirements.
>
> iso.org/standard/77302.html
>
> ISO STANDARD
>
> ISO/TS 21815-2:2021
>
> Earth-moving machinery — Collision warning and avoidance — Part 2: On-board J1939 communication interface.
>
> iso.org/standard/77303.html
>
> PEER-REVIEWED PAPER
>
> Ogunrinde & Bernadin (2023)
>
> Deep Camera–Radar Fusion with an Attention Framework for Autonomous Vehicle Vision in Foggy Weather Conditions. Sensors, 23(14), 6255.
>
> doi.org/10.3390/s23146255
>
> PEER-REVIEWED PAPER
>
> Hrica et al. (2022)
>
> A Rapid Review of Collision Avoidance and Warning Technologies for Mining Haul Trucks. Mining, Metallurgy & Exploration, 39, 1357–1389.
>
> doi.org/10.1007/s42461-022-00633-w
>
> CURRENT HARDWARE REFERENCES
>
> HLK-LD2450
>
> BNO055
>
> 24 GHz tracking radar  ·  official manufacturer reference
>
> 9-DOF IMU  ·  Bosch Sensortec docs
>
> MLX90640-D55
>
> LC29H(AA) GPS HAT
>
> 32×24 thermal array  ·  Melexis datasheet
>
> Dual-band GNSS receiver  ·  Waveshare product page
>
> Raspberry Pi 4 Model B
>
> 4 GB edge compute  ·  raspberrypi.com
>
> ESP32-S3-DevKitC-1
>
> Bounded control MCU  ·  espressif.com docs
>
> Cytron MDD10A
>
> Dual-channel motor driver  ·  cytron official page
>
> DEFERRED HIGH-GRADE OPTION
>
> AWR1843BOOST, FLIR Lepton 3.5, Pi 5, STM32F407, Sabertooth 2×32 — future upgrade path, not part of the ≤ ₹60,000 MVP.
>
> DETAILED PROJECT DOCUMENTATION
>
> OPEN MASTER BUILD PLAN
>
> Master build, budget & validation plan
>
> OPEN COMPLETE PROJECT DOSSIER
>
> TARK GITHUB REPOSITORY
>
> Full engineering blueprint & BOM
>
> Source code and software baseline
>
> OPEN SIMULATION 1
>
> PV-SOE — stopping envelope logic
>
> OPEN SIMULATION 2
>
> Fixed vs adaptive-covariance EKF
>
> OPEN SIMULATION 3
>
> TARK PUBLIC DEMO
>
> Fault-injection / safety-state logic
>
> Simulation / monitoring dashboard — not physical vehicle operation
>
> Manufacturer, standards and paper links were checked directly and are live. Cytron’s page could not be independently fetched (bot-protected) but matches the listed product. The GitHub link above returned unavailable when checked — please verify before sharing.
>
> SMART INDIA
HACKATHON 2026

## TARK_SIH26007_upgraded_deck.pptx

SHA-256: `894cf22c67efc8b622f2179e4a1256e3c0b17329ff9c79b091c9524f4ae9829a`.

### Slide 1

> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Title Page
>
> 01
>
> SMART INDIA HACKATHON 2026
>
> IDEA SUBMISSION  ·  HARDWARE
>
> PROBLEM STATEMENT ID
>
> SIH26007
>
> THEME
>
> Smart Automation
>
> CATEGORY
>
> Hardware
>
> TEAM NAME
>
> TARK
>
> PROBLEM STATEMENT
>
> “Safe and Efficient Operation of Mine Vehicles in Fog and Low-Visibility Conditions in Open Cast Iron Ore Mines.”
>
> PROPOSED SOLUTION
>
> PERCEPTION-VERIFIED SAFETY ASSISTANCE
>
> FOR OPEN-CAST MINE VEHICLES
>
> Multi-sensor perception  +  risk-aware operating envelope  +  independent safety control
>
> CONCEPTUAL PROTOTYPE
>
> Proposed hardware arrangement
>
> RADAR + THERMAL + RGB
>
> 4-WHEEL DIFFERENTIAL DRIVE
>
> Open-cast iron ore mine — haul road in fog (conceptual)
>
> SMART INDIA
HACKATHON 2026

### Slide 2

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 02
>
> Proposed Solution
>
> Complementary sensing plus a reliability check before the vehicle is allowed to continue
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Proposed Solution
>
> 02
>
> HOW THE REASONING FLOWS
>
> Low visibility (fog)
>
> ⌄
>
> Visible-light perception becomes less reliable
>
> ⌄
>
> People / vehicles / obstacles become harder to observe
>
> ⌄
>
> System checks sensor health and observability
>
> ⌄
>
> Fuses complementary sensing (radar + thermal + RGB)
>
> ⌄
>
> Tracks hazards and relative motion
>
> ⌄
>
> Calculates TTC and stopping requirement
>
> ⌄
>
> Evaluates Perception-Verified Safe Operating Envelope
>
> NORMAL
>
> ›
>
> WARN
>
> ›
>
> RESTRICT
>
> ›
>
> STOP
>
> CORE IDEA
>
> We are not only detecting obstacles; we are deciding whether the available perception is reliable enough for the vehicle to safely continue.
>
> CORE HARDWARE
>
> HLK-LD2450
>
> 24 GHz tracking radar
>
> MLX90640-D55
>
> 32×24 thermal array
>
> RGB Camera
>
> 1080p USB/UVC
>
> BNO055 + Encoders
>
> Orientation + ego-motion
>
> This is a proposed system-level differentiation, not a claim that radar, thermal sensing or fusion are individually novel.
>
> GNSS (LC29H·AA) supports route/location context only — never a collision-safety input.
>
> SMART INDIA
HACKATHON 2026

### Slide 3

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 03
>
> Technical Approach
>
> Sensing  →  Edge Perception  →  Safety Control  →  Actuation
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Technical Approach
>
> 03
>
> HLK-LD2450
>
> 24 GHz tracking radar
>
> MLX90640-D55
>
> 32×24 thermal array
>
> RGB Camera
>
> 1080p USB/UVC
>
> BNO055 IMU
>
> LC29H(AA)
>
> + wheel encoders
>
> Dual-band GNSS receiver
>
> ▼
>
> RASPBERRY PI 4  —  EDGE PERCEPTION COMPUTE
>
> Timestamping
>
> ›
>
> Sensor health / observability
>
> ›
>
> Detection / target extraction
>
> ›
>
> Track-level EKF
>
> Fixed vs. adaptive covariance
>
> ›
>
> Relative velocity
>
> ›
>
> TTC / stopping requirement
>
> ›
>
> PV-SOE state
>
> NORMAL
>
> ›
>
> WARN
>
> ›
>
> RESTRICT
>
> ›
>
> STOP
>
> ▼  bounded command · heartbeat · timeout · CRC check · watchdog
>
> ESP32-S3
>
> Bounded control · watchdog
>
> Cytron MDD10A
>
> Dual-channel motor driver
>
> 4-wheel vehicle
>
> Differential-driver prototype
>
> INDEPENDENT SAFETY BACKSTOP
>
> Physical E-stop → DC contactor → traction isolated. Independent of Pi / ESP32-S3 software path.
>
> OBSERVATION / HMI PATH
>
> TARK Digital HMI
>
> WebSocket Telemetry
>
> TARK Backend (FastAPI)
>
> Raspberry Pi 4
>
> ⌄
>
> ⌄
>
> ⌄
>
> EKF itself is a standard estimator. Our experimental focus is FIXED covariance vs QUALITY-ADAPTIVE covariance.
>
> Pi = perception + reasoning   |   ESP32-S3 = bounded control + watchdog   |   E-stop = physical isolation
>
> SMART INDIA
>
> HACKATHON 2026
>
> Dashboard · Map · Sensors · Safety · Replay · Logs
>
> MONITORING ONLY · NO BROWSER MOTION AUTHORITY — dashboard path never reaches the motors.

### Slide 4

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 04
>
> Feasibility and Viability
>
> Hardware, software, safety and validation, staged toward a future controlled mine pilot
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Feasibility and Viability
>
> 04
>
> HARDWARE
>
> Low-cost radar, thermal array, RGB baseline
>
> Raspberry Pi 4 edge compute
>
> ESP32-S3 bounded controller
>
> Cytron MDD10A dual motor driver
>
> 4-wheel differential-drive platform
>
> BNO055 IMU + GNSS (LC29H·AA)
>
> SOFTWARE
>
> Sensor acquisition & timestamping
>
> Quality / observability layer
>
> Tracking (EKF)
>
> Adaptive uncertainty fusion
>
> TTC + stopping requirement
>
> PV-SOE state machine
>
> Localization · dashboard · FastAPI/WebSocket backend
>
> SAFETY
>
> Independent MCU (ESP32-S3)
>
> Heartbeat watchdog
>
> Bounded commands
>
> Degraded operating modes
>
> Hardware E-stop + traction isolation
>
> DIGITAL DEMONSTRATION + VALIDATION
>
> Simulation 1 — PV-SOE / stopping envelope
>
> Simulation 2 — fixed vs adaptive fusion
>
> Simulation 3 — fault injection / safe-state
>
> Planned: degraded-visibility testing + ground-truth metrics
>
> Deployed — public sim/monitoring demo
>
> Traction: DISABLED_PHASE_1 (safe-state)
>
> DEVELOPMENT ROADMAP
>
> CONCEPT
>
> ›
>
> NUMERICAL
>
> SIMULATION
>
> ›
>
> BENCH SENSOR
>
> INTEGRATION
>
> ›
>
> VEHICLE
>
> PROTOTYPE
>
> ›
>
> DEGRADED-
>
> VISIBILITY TEST
>
> ›
>
> VALIDATION
>
> ›
>
> FUTURE ENGINEERING /
>
> MINE PILOT
>
> Physical prototype, fog chamber and measured performance are future work — not part of this submission.
>
> SMART INDIA
>
> HACKATHON 2026
>
> TARK DIGITAL HMI
>
> LIVE SOFTWARE DEMONSTRATOR
>
> tark-sih26007-demo.onrender.com
>
> ● ● ●
>
> LIVE DASHBOARD SCREENSHOT
>
> To be inserted from the verified deployment before submission
>
> ✓  Real-time telemetry
>
> ✓  Sensor health
>
> ✓  Safety state
>
> ✓  Map / localization
>
> ✓  Radar local view
>
> ✓  Replay / evidence
>
> MONITORING ONLY · NO BROWSER MOTION AUTHORITY
>
> PUBLIC DEMO · SIMULATION · TRACTION DISABLED
>
> LIVE SOFTWARE DEMO →  tark-sih26007-demo.onrender.com
>
> SOFTWARE BASELINE — frozen 2d319e7
>
> 97 backend tests · 25 frontend tests · TypeScript/build passed · firmware host tests passed

### Slide 5

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 05
>
> Impact and Benefits
>
> What the proposed system is designed to improve
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Impact and Benefits
>
> 05
>
> 01
>
> 04
>
> IMPROVED OPERATOR AWARENESS
>
> FAIL-SAFE BOUNDED CONTROL
>
> Useful hazard information when visible-light perception degrades.
>
> Independent MCU, watchdog, command bounds and a physical E-stop.
>
> 02
>
> 05
>
> COMPLEMENTARY PERCEPTION
>
> LOCALIZATION + CONTEXT
>
> Radar, thermal and RGB provide different information under poor visibility.
>
> GNSS supports route/map context only — never collision-safety authority.
>
> 03
>
> 06
>
> RISK-AWARE OPERATING ENVELOPE
>
> COST-CONSCIOUS SCALABILITY
>
> Permitted operation becomes more conservative when perception or stopping margin becomes inadequate.
>
> Low-cost prototype is designed to validate the architecture; higher-grade industrial sensors can be introduced later without changing the core safety-decision concept.
>
> WHAT THIS PROTOTYPE IS NOT
>
> ✕  Not a full-size HEMM controller
>
> ✕  Not autonomous steering
>
> ✕  Not a production mine safety system
>
> ✕  Not mine-certified equipment
>
> ✕  Not a guarantee of collision prevention
>
> The operator remains part of the control loop at all times.
>
> SMART INDIA
HACKATHON 2026
>
> CONCEPTUAL PROTOTYPE — PROPOSED HARDWARE ARRANGEMENT
>
> ≤ ₹60,000
>
> Maximum planning ceiling for the scaled prototype, controlled test setup and contingency — prototype subtotal ₹52,750 + GNSS module ≈₹4,522 + ₹2,250 contingency ≈ ₹59,522.
>
> BNO055
>
> Bounded Controller

### Slide 6

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 06
>
> Research, References & Detailed Resources
>
> Standards, peer-reviewed research, current hardware references and detailed project documentation
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Research, References & Resources
>
> 06
>
> TECHNICAL REFERENCES
>
> ISO STANDARD
>
> ISO 21815-1:2022
>
> Earth-moving machinery — Collision warning and avoidance — Part 1: General requirements.
>
> iso.org/standard/77302.html
>
> ISO STANDARD
>
> ISO/TS 21815-2:2021
>
> Earth-moving machinery — Collision warning and avoidance — Part 2: On-board J1939 communication interface.
>
> iso.org/standard/77303.html
>
> PEER-REVIEWED PAPER
>
> Ogunrinde & Bernadin (2023)
>
> Deep Camera–Radar Fusion with an Attention Framework for Autonomous Vehicle Vision in Foggy Weather Conditions. Sensors, 23(14), 6255.
>
> doi.org/10.3390/s23146255
>
> PEER-REVIEWED PAPER
>
> Hrica et al. (2022)
>
> A Rapid Review of Collision Avoidance and Warning Technologies for Mining Haul Trucks. Mining, Metallurgy & Exploration, 39, 1357–1389.
>
> doi.org/10.1007/s42461-022-00633-w
>
> CURRENT HARDWARE REFERENCES
>
> HLK-LD2450
>
> BNO055
>
> 24 GHz tracking radar  ·  official manufacturer reference
>
> 9-DOF IMU  ·  Bosch Sensortec docs
>
> MLX90640-D55
>
> LC29H(AA) GPS HAT
>
> 32×24 thermal array  ·  Melexis datasheet
>
> Dual-band GNSS receiver  ·  Waveshare product page
>
> Raspberry Pi 4 Model B
>
> 4 GB edge compute  ·  raspberrypi.com
>
> ESP32-S3-DevKitC-1
>
> Bounded control MCU  ·  espressif.com docs
>
> Cytron MDD10A
>
> Dual-channel motor driver  ·  cytron official page
>
> DEFERRED HIGH-GRADE OPTION
>
> AWR1843BOOST, FLIR Lepton 3.5, Pi 5, STM32F407, Sabertooth 2×32 — future upgrade path, not part of the ≤ ₹60,000 MVP.
>
> DETAILED PROJECT DOCUMENTATION
>
> OPEN MASTER BUILD PLAN
>
> Master build, budget & validation plan
>
> OPEN COMPLETE PROJECT DOSSIER
>
> TARK GITHUB REPOSITORY
>
> Full engineering blueprint & BOM
>
> Source code and software baseline
>
> OPEN SIMULATION 1
>
> PV-SOE — stopping envelope logic
>
> OPEN SIMULATION 2
>
> Fixed vs adaptive-covariance EKF
>
> OPEN SIMULATION 3
>
> TARK PUBLIC DEMO
>
> Fault-injection / safety-state logic
>
> Simulation / monitoring dashboard — not physical vehicle operation
>
> Manufacturer, standards and paper links were checked directly and are live. Cytron’s page could not be independently fetched (bot-protected) but matches the listed product. The GitHub link above returned unavailable when checked — please verify before sharing.
>
> SMART INDIA
HACKATHON 2026

## TARK_SIH26007_Submission_Final.pptx

SHA-256: `ca218f385bc24eb853ddddc358f9080d01295826792735dacb19e1d4a107a9c6`.

### Slide 1

> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Title Page
>
> 01
>
> SMART INDIA HACKATHON 2026
>
> IDEA SUBMISSION  ·  HARDWARE
>
> PROBLEM STATEMENT ID
>
> SIH26007
>
> THEME
>
> Smart Automation
>
> CATEGORY
>
> Hardware
>
> TEAM NAME
>
> TARK
>
> PROBLEM STATEMENT
>
> “Safe and Efficient Operation of Mine Vehicles in Fog and Low-Visibility Conditions in Open Cast Iron Ore Mines.”
>
> PROPOSED SOLUTION
>
> PERCEPTION-VERIFIED SAFETY ASSISTANCE
>
> FOR OPEN-CAST MINE VEHICLES
>
> Multi-sensor perception  +  risk-aware operating envelope  +  independent safety control
>
> CONCEPTUAL PROTOTYPE
>
> Proposed hardware arrangement
>
> RADAR + THERMAL + RGB
>
> 4-WHEEL DIFFERENTIAL DRIVE
>
> Open-cast iron ore mine — haul road in fog (conceptual)
>
> SMART INDIA
HACKATHON 2026

### Slide 2

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 02
>
> Proposed Solution
>
> Complementary sensing plus a reliability check before the vehicle is allowed to continue
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Proposed Solution
>
> 02
>
> HOW THE REASONING FLOWS
>
> Low visibility (fog)
>
> ⌄
>
> Visible-light perception becomes less reliable
>
> ⌄
>
> People / vehicles / obstacles become harder to observe
>
> ⌄
>
> System checks sensor health and observability
>
> ⌄
>
> Fuses complementary sensing (radar + thermal + RGB)
>
> ⌄
>
> Tracks hazards and relative motion
>
> ⌄
>
> Calculates TTC and stopping requirement
>
> ⌄
>
> Evaluates Perception-Verified Safe Operating Envelope
>
> NORMAL
>
> ›
>
> WARN
>
> ›
>
> RESTRICT
>
> ›
>
> STOP
>
> CORE IDEA
>
> We are not only detecting obstacles; we are deciding whether the available perception is reliable enough for the vehicle to safely continue.
>
> CORE HARDWARE
>
> HLK-LD2450
>
> 24 GHz tracking radar
>
> MLX90640
>
> 32×24 thermal array
>
> RGB Camera
>
> 1080p USB/UVC
>
> BNO055 + Encoders
>
> Orientation + ego-motion
>
> This is a proposed system-level differentiation, not a claim that radar, thermal sensing or fusion are individually novel.
>
> GNSS (LC29H·AA) supports route/location context only — never a collision-safety input.
>
> SMART INDIA
HACKATHON 2026

### Slide 3

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 03
>
> Technical Approach
>
> Sensing  →  Edge Perception  →  Safety Control  →  Actuation
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Technical Approach
>
> 03
>
> HLK-LD2450
>
> 24 GHz tracking radar
>
> MLX90640
>
> 32×24 thermal array
>
> RGB Camera
>
> 1080p USB/UVC
>
> BNO055 IMU
>
> LC29H(AA)
>
> + wheel encoders
>
> Dual-band GNSS receiver
>
> ▼
>
> RASPBERRY PI 4  —  EDGE PERCEPTION COMPUTE
>
> Timestamping
>
> ›
>
> Sensor health / observability
>
> ›
>
> Detection / target extraction
>
> ›
>
> Track-level EKF
>
> Fixed vs. adaptive covariance
>
> ›
>
> Relative velocity
>
> ›
>
> TTC / stopping requirement
>
> ›
>
> PV-SOE state
>
> NORMAL
>
> ›
>
> WARN
>
> ›
>
> RESTRICT
>
> ›
>
> STOP
>
> ▼  bounded command · heartbeat · timeout · CRC check · watchdog
>
> ESP32-S3
>
> Bounded control · watchdog
>
> Cytron MDD10A
>
> Dual-channel motor driver
>
> 4-wheel vehicle
>
> Differential-driver prototype
>
> INDEPENDENT SAFETY BACKSTOP
>
> Physical E-stop → DC contactor → traction isolated. Independent of Pi / ESP32-S3 software path.
>
> ALGORITHM CHAIN
>
> Sensor quality / observability
>
> ⌄
>
> Measurement uncertainty
>
> ⌄
>
> Adaptive fusion
>
> ⌄
>
> Target state
>
> ⌄
>
> Relative velocity
>
> ⌄
>
> TTC
>
> ⌄
>
> Stopping requirement
>
> ⌄
>
> PV-SOE state
>
> EKF itself is a standard estimator. Our experimental focus is FIXED covariance vs QUALITY-ADAPTIVE covariance.
>
> Pi = perception + reasoning   |   ESP32-S3 = bounded control + watchdog   |   E-stop = physical isolation
>
> SMART INDIA
>
> HACKATHON 2026

### Slide 4

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 04
>
> Feasibility and Viability
>
> Hardware, software, safety and validation, staged toward a future controlled mine pilot
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Feasibility and Viability
>
> 04
>
> HARDWARE
>
> Low-cost radar, thermal array, RGB baseline
>
> Raspberry Pi 4 edge compute
>
> ESP32-S3 bounded controller
>
> Cytron MDD10A dual motor driver
>
> 4-wheel differential-drive platform
>
> BNO055 IMU + GNSS (LC29H·AA)
>
> SOFTWARE
>
> Sensor acquisition & timestamping
>
> Quality / observability layer
>
> Tracking (EKF)
>
> Adaptive uncertainty fusion
>
> TTC + stopping requirement
>
> PV-SOE state machine
>
> Localization · dashboard · FastAPI/WebSocket backend
>
> SAFETY
>
> Independent MCU (ESP32-S3)
>
> Heartbeat watchdog
>
> Bounded commands
>
> Degraded operating modes
>
> Hardware E-stop + traction isolation
>
> VALIDATION / SIMULATION
>
> Simulation 1 — PV-SOE / stopping envelope
>
> Simulation 2 — fixed vs adaptive fusion
>
> Simulation 3 — fault injection / safe-state
>
> Controlled degraded-visibility testing
>
> Ground truth + measured metrics later
>
> Deployed — public sim/monitoring demo
>
> Traction: DISABLED_PHASE_1 (safe-state)
>
> DEVELOPMENT ROADMAP
>
> CONCEPT
>
> ›
>
> NUMERICAL
>
> SIMULATION
>
> ›
>
> BENCH SENSOR
>
> INTEGRATION
>
> ›
>
> VEHICLE
>
> PROTOTYPE
>
> ›
>
> DEGRADED-
>
> VISIBILITY TEST
>
> ›
>
> VALIDATION
>
> ›
>
> FUTURE ENGINEERING /
>
> MINE PILOT
>
> Physical prototype, fog chamber and measured performance are future work — not part of this submission.
>
> VALIDATION EVIDENCE — SIMULATION 2
>
> Numerical simulation -
>
> Synthetic degradation levels-not measured hardware data
>
> Quality-adaptive covariance keeps track-position error lower than a fixed-covariance filter as sensor quality degrades (C0=clear … C4=failure). Synthetic degradation levels — not measured hardware data.
>
> SMART INDIA
>
> HACKATHON 2026

### Slide 5

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 05
>
> Impact and Benefits
>
> What the proposed system is designed to improve
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Impact and Benefits
>
> 05
>
> 01
>
> 04
>
> IMPROVED OPERATOR AWARENESS
>
> FAIL-SAFE BOUNDED CONTROL
>
> Useful hazard information when visible-light perception degrades.
>
> Independent MCU, watchdog, command bounds and a physical E-stop.
>
> 02
>
> 05
>
> COMPLEMENTARY PERCEPTION
>
> LOCALIZATION + CONTEXT
>
> Radar, thermal and RGB provide different information under poor visibility.
>
> GNSS supports route/map context only — never collision-safety authority.
>
> 03
>
> 06
>
> RISK-AWARE OPERATING ENVELOPE
>
> COST-CONSCIOUS SCALABILITY
>
> Permitted operation becomes more conservative when perception or stopping margin becomes inadequate.
>
> Low-cost prototype validates the architecture; higher-grade industrial sensors can be introduced later without changing the safety-decision concept.
>
> WHAT THIS PROTOTYPE IS NOT
>
> ✕  Not a full-size HEMM controller
>
> ✕  Not autonomous steering
>
> ✕  Not a production mine safety system
>
> ✕  Not mine-certified equipment
>
> ✕  Not a guarantee of collision prevention
>
> The operator remains part of the control loop at all times.
>
> SMART INDIA
HACKATHON 2026
>
> CONCEPTUAL PROTOTYPE — PROPOSED HARDWARE ARRANGEMENT
>
> ≤ ₹60,000
>
> Maximum planning ceiling for the scaled prototype, controlled test setup and contingency — prototype subtotal ₹52,750 + GNSS module ≈₹4,522 + ₹2,250 contingency ≈ ₹59,522.
>
> BNO055

### Slide 6

> TARK  ·  SIH26007
>
> SMART INDIA HACKATHON 2026
>
> 06
>
> Research, References & Detailed Resources
>
> Standards, peer-reviewed research, current hardware references and detailed project documentation
>
> SIH 2026  ·  PS ID SIH26007  ·  Smart Automation  ·  Hardware  ·  Research, References & Resources
>
> 06
>
> TECHNICAL REFERENCES
>
> ISO STANDARD
>
> ISO 21815-1:2022
>
> Earth-moving machinery — Collision warning and avoidance — Part 1: General requirements.
>
> iso.org/standard/77302.html
>
> ISO STANDARD
>
> ISO/TS 21815-2:2021
>
> Earth-moving machinery — Collision warning and avoidance — Part 2: On-board J1939 communication interface.
>
> iso.org/standard/77303.html
>
> PEER-REVIEWED PAPER
>
> Ogunrinde & Bernadin (2023)
>
> Deep Camera–Radar Fusion with an Attention Framework for Autonomous Vehicle Vision in Foggy Weather Conditions. Sensors, 23(14), 6255.
>
> doi.org/10.3390/s23146255
>
> PEER-REVIEWED PAPER
>
> Hrica et al. (2022)
>
> A Rapid Review of Collision Avoidance and Warning Technologies for Mining Haul Trucks. Mining, Metallurgy & Exploration, 39, 1357–1389.
>
> doi.org/10.1007/s42461-022-00633-w
>
> CURRENT HARDWARE REFERENCES
>
> HLK-LD2450
>
> BNO055
>
> 24 GHz tracking radar module  ·  current India listing
>
> 9-DOF IMU  ·  Bosch Sensortec docs
>
> MLX90640-BAB
>
> LC29H(AA) GPS HAT
>
> 32×24 thermal array  ·  Melexis datasheet
>
> Dual-band GNSS receiver  ·  Waveshare product page
>
> Raspberry Pi 4 Model B
>
> 4 GB edge compute  ·  raspberrypi.com
>
> ESP32-S3-DevKitC-1-N8
>
> Bounded control MCU  ·  espressif.com docs
>
> Cytron MDD10A
>
> Dual-channel motor driver  ·  cytron official page
>
> DEFERRED HIGH-GRADE OPTION
>
> AWR1843BOOST, FLIR Lepton 3.5, Pi 5, STM32F407, Sabertooth 2×32 — future upgrade path, not part of the ≤ ₹60,000 MVP.
>
> DETAILED PROJECT DOCUMENTATION
>
> OPEN MASTER BUILD PLAN
>
> Master build, budget & validation plan
>
> OPEN COMPLETE PROJECT DOSSIER
>
> Full engineering blueprint & BOM
>
> OPEN SIMULATION 1
>
> PV-SOE — stopping envelope logic
>
> OPEN SIMULATION 2
>
> Fixed vs adaptive-covariance EKF
>
> OPEN SIMULATION 3
>
> TARK PUBLIC DEMO
>
> Fault-injection / safety-state logic
>
> Simulation / monitoring dashboard — not physical vehicle operation
>
> All links above were checked and are live. TARK GitHub repository: private during SIH review, available to reviewers on request.
>
> SMART INDIA
HACKATHON 2026
