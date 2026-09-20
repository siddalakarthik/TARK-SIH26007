# Hardware Arrival Checklist

## Universal rule

Keep traction isolated. Use the released schematic, V2 manual and exact purchased documentation to identify every board and connector. Do not infer terminal orientation, voltage, wire size, fuse value or E-stop behavior from software. Record part number, revision, serial number, photo, owner and date before connecting it.

| Component | First software selection | First verification | Do not connect or claim yet |
|---|---|---|---|
| Raspberry Pi 4 | `simulation` until OS, storage and controlled logic rail are verified | boot, hostname, software/configuration hash, local API | traction or unknown sensor VCC |
| ESP32-S3 DevKitC-1 | firmware build only after exact board docs | enumerate verified USB port, flash, boot identity, STATUS and Phase 1 disabled output | MDD10A/motor control, E-stop substitution |
| HLK-LD2450 | raw serial capture first | actual board label, serial device, 256000 8N1 capture, preserve raw bytes | normalized real detections until vendor frame decoder is reviewed |
| MDD10A | `NOT_CONNECTED_PHASE_2` | model/terminal labels match V2 and purchased manual | traction feed/motor output; no PWM claim |
| motors | `NOT_CONNECTED_PHASE_2` | left/right label and terminal documentation | powered movement |
| encoders | `NOT_CONNECTED_PHASE_2` | connector labels and actual output/interface documentation | VCC, because it remains TBD/VERIFY; ground-speed claim |
| USB camera | `NOT_CONNECTED_PHASE_2` | UVC discovery and timestamped test frame | simulated imagery labelled LIVE |
| MLX90640 | `NOT_CONNECTED_PHASE_2` | purchased breakout label, VCC/pull-up/interface documentation | VCC/calibration claim |
| BNO055 | `NOT_CONNECTED_PHASE_2` | purchased breakout label, calibration status and interface documentation | VCC/calibration claim |

For every connection, use the V2 LEGO card sequence: find, identify, orient using board marking/documentation, label, attach one end, inspect, attach second end, meter-check with power off, record. A failed or mismatched item remains HOLD.
