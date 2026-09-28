# TARK SIH26007 Master Project Index

This index supports the Master Project Dossier V1.0. It does not replace the controlled source hierarchy.

## Primary controlled sources

| Path | Role |
| --- | --- |
| `outputs/FINAL_ENGINEERING_PRESENTATION.pdf` | Latest controlled electrical presentation and pin terminal net reference |
| `outputs/FINAL_ENGINEERING_PRESENTATION.svg` | Vector electrical presentation source |
| `outputs/TARK_SIH26007_LEGO_STYLE_BUILD_AND_COMMISSIONING_MANUAL_V2.docx` | Physical build and commissioning sequence |
| `outputs/TARK_SIH26007_COMPLETE_BUILD_AND_INTEGRATION_MANUAL_V1.docx` | Earlier detailed build and integration reference |
| `outputs/TARK_SIH26007_MASTER_SOFTWARE_ARCHITECTURE/` | Architecture and contract package |
| `tark/` | Frozen TARK software repository |

## Software release and operation records

| Path | Role |
| --- | --- |
| `tark/docs/SOFTWARE_FREEZE_BASELINE.md` | Freeze commit, tag and release evidence |
| `tark/docs/FINAL_SOFTWARE_COMMUNICATION_CLOSURE_REPORT.md` | Protocol, LD2450, encoder and host-test closure |
| `tark/docs/ESP32_PROTOCOL_V1.md` | Sole Protocol V1 contract |
| `tark/docs/PROTOCOL_IMPLEMENTATION.md` | Protocol implementation notes |
| `tark/docs/RUN.md` | Local startup workflow |
| `tark/docs/DEPLOYMENT.md` | Deployment operating record |
| `tark/docs/PUBLIC_DEPLOYMENT.md` | Public deployment configuration record |
| `tark/docs/PUBLIC_QA_FIX_REPORT.md` | Scoped public HMI QA fixes |
| `tark/docs/UI_GUIDE.md` | Dashboard and HMI guide |
| `tark/docs/SIMULATION.md` | Simulation operation and source truthfulness |
| `tark/docs/REPLAY_GUIDE.md` | Replay operation |
| `tark/docs/TEST_REPORT.md` | Test record |
| `tark/docs/FAULT_MATRIX.md` | Fault behavior |
| `tark/config/phase1.json` | Frozen Phase 1 parameters and disabled hard cap |

## Hardware and interface references

| Path | Role |
| --- | --- |
| `tark/docs/HARDWARE_ARRIVAL_CHECKLIST.md` | Controlled hardware arrival procedure |
| `tark/docs/GNSS_INTEGRATION.md` | LC29H AA software boundary and safety isolation |
| `tark/docs/CAMERA_INTEGRATION.md` | UVC camera interface |
| `tark/docs/IMU_INTEGRATION.md` | BNO055 interface |
| `tark/docs/THERMAL_INTEGRATION.md` | MLX90640 interface |
| `tark/docs/I2C_SENSOR_HARDWARE_BRINGUP.md` | I2C hardware bring-up guardrails |
| `tark/docs/ESP32_MOTOR_ENCODER_INTEGRATION.md` | ESP32 motor and encoder interface boundary |
| `tark/firmware/esp32/KNOWN_LIMITATIONS.md` | Firmware hardware-binding limitations |

## Repository implementation areas

| Path | Role |
| --- | --- |
| `tark/backend/` | FastAPI backend and TARK decision services |
| `tark/frontend/` | React TypeScript HMI |
| `tark/firmware/esp32/` | ESP32 Protocol V1 and host-test source |
| `tark/tests/` | Backend test suite where present |
| `tark/simulation/` | Simulation components where present |
| `tark/scripts/` | Startup, build, test and deployment helpers |

## Release identity

- Frozen commit: `2d319e7`
- Previous QA commit: `962365e`
- Frozen tag: `tark-software-freeze-2026-09-20`
- Current dossier: `outputs/TARK_SIH26007_MASTER_PROJECT_DOSSIER_V1_0.docx`
- Current dossier PDF: `outputs/TARK_SIH26007_MASTER_PROJECT_DOSSIER_V1_0.pdf`
