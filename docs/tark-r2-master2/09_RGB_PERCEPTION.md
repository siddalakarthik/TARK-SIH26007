# 09 — RGB perception

B0200 IMX291 UVC is frozen. 100° is diagonal FOV; near focus and actual exposure controls require characterization. No camera substitution or physical access.

## Deployment design

One camera owner acquires supported compressed frames with native timestamp information and host reception time. Decode in a bounded worker, validate format/resolution/age and feed inference using latest-frame slots. Preserve original timestamps; dropped frames increment counters. Media/inference failures must not block the decision loop.

Select YOLO11n as the initial *benchmark candidate*, compare YOLO11s and YOLOv8n under the same data/latency budget. Prefer the smaller model unless held-out task gains justify its cost. Initial proposed input is letterboxed 640×640 and TensorRT FP16 batch 1 on Jetson; freeze weights/export/runtime hashes only after accuracy, licensing and concurrent thermal/memory testing. Published GPU benchmarks are not TARK FPS. No code/model download in this task. [Model documentation](https://docs.ultralytics.com/models/yolo11/).

Pretrained person/truck/car classes are starting hypotheses, not validated mining labels. Machinery, unusual obstructions and mine signs require task-labelled training/evaluation; unsupported classes remain UNKNOWN. Sign recognition is contextual and cannot override approved map restrictions. No monocular metric range is asserted.

Pipeline: frame → timing/health → image quality → detector → bounded image-space tracker → class/confidence → geometric/time association. Use Kalman image-box prediction and gated IoU/Hungarian matching as initial image tracker; image IDs are not radar IDs. Store class distribution and model ID, not just a name. Model score is not calibrated collision probability.

## Quality evidence

| Metric | Computation | Limitation |
|---|---|---|
| Contrast | Local intensity standard deviation / bounded percentile spread | Exposure and scene texture confound |
| Edge density | Fraction above calibrated gradient threshold | Plain road can naturally be low-edge |
| Sharpness | Variance of Laplacian, with resolution/exposure version | Blur, motion, compression and fog overlap |
| Clipping | Fraction near min/max luminance | Headlights/sky differ from blockage |
| Saturation/histogram | Channel clipping and distribution changes | Not physical visibility distance |
| Freeze/dropout | Source sequence/time continuity; repeated-content evidence secondary | A static scene is not automatically frozen |

Return quality vector with reason, ROI, calibration and age. Thresholds are learned/selected on held-out reference conditions, not a fabricated fog-meter conversion. Exposure automation changes must be recorded; manual exposure is not assumed available. Enhancement, if later evaluated, is a separate derived stream with original frames retained; it must not create “observed” details.

Test disconnected/frozen camera, dark/glare/blur, small objects, occluded classes and safe/aerosol matched runs. Report precision/recall by class/condition, missed detections, false alarms and end-to-end latency. No semantic detection or clear image proves free space.
