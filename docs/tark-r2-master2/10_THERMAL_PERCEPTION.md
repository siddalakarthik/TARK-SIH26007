# 10 — Thermal perception

Complete path: Lepton 3.5 500-0771-01 → PURETHERMAL-3 → USB acquisition → timestamp/FFC validity → regions/tracks → cross-sensor association. Core alone is not a complete host camera. [Bridge documentation](https://groupgets.com/products/purethermal-3), [frozen specifications](../tark-r2-master/03_EXACT_COMPONENT_FREEZE.md).

Preserve native 160×120/8.7 Hz behavior. Do not interpolate a display stream and report it as new measurements. One owner selects the documented firmware/UVC mode and records pixel format, scale and radiometric/AGC state. Validate dimensions, complete frame, sequence, finite conversion, age and FFC/shutter state. A held frame during FFC must be labelled unavailable for new measurements.

Thermal imagery shows spatial radiation contrast. Radiometric temperature requires a documented mode, units, calibration, emissivity/reflected-temperature treatment and environmental assumptions. Pseudo-color is a display transformation, not temperature or distance. If metadata cannot support calibrated temperature, show relative intensity/contrast only. No thermal range is synthesized.

Initial region method: remove characterized bad pixels; estimate local background with robust median; threshold positive/negative contrast using calibrated noise; connected-component regions with pixel-area bounds; track centroids/boxes with bounded association. O(pixels) filtering/labeling plus bounded tracking. Keep both warmer and cooler anomalies; warm does not mean person. Ambient changes, hot machinery, reflections, equal-temperature targets and FFC can invalidate the method.

Output ThermalRegion: region ID, box/centroid in optical pixels, contrast metric and units, optional supported temperature statistics, frame timestamp, FFC state, quality, uncertainty and calibration ID. A thermal-only region can trigger “unclassified thermal contrast,” not a named object at invented distance. Matched radar supplies a *separately attributed* distance; ambiguity remains explicit.

Validate target pixels/contrast over distances, emissivity/background variation, FFC interruption/recovery, USB corruption/stale frames and remounts. Retain raw values and display transfer settings for replay. No ordinary glass/acrylic optical window is presumed LWIR-transparent. No mine-weather or absolute-temperature accuracy claim follows from a working USB image.
