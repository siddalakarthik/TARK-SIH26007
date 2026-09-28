# UI Guide

Current [R1 scope](PROJECT_STATUS.md): measured speed is `UNAVAILABLE`, TTC is
`NOT COMPUTED`, and permitted speed is a separately labelled zero command.
NORMAL describes available modeled evidence, not certified safety. Source,
traction-disabled and parameterized labels remain visible. The current wire
contract is [Protocol V2](ESP32_PROTOCOL_V2.md); no UI code changed in Prompt 4.

The React application uses one shell with DRIVER, SUPERVISOR and OWNER/FLEET view selection. It provides Dashboard, Map, Sensors, Safety, Logs, Replay, Diagnostics and Settings views. Dashboard displays state, reason, current/permitted speed, PV-SOE, radar tracks, health and events. Sensors shows source mode/status/reason. Safety exposes only backend-calculated PV-SOE values and marks parameterized values. Replay is observation-only. Settings shows diagnostics without safety-parameter editing. The browser is monitoring-only and has no command route to traction, PV-SOE, or ESP32 validation.

The MapLibre component is lazy-loaded. Its style priority is `VITE_MAP_STYLE_URL`, legacy `VITE_MAPTILER_STYLE_URL`, then the no-key OpenFreeMap Liberty style. `TARK_DEFAULT_MAP_CENTER=longitude,latitude` and `TARK_DEFAULT_MAP_ZOOM` are display-only configuration. Without an approved centre, the UI opens in an India overview—context for this Indian project, not a mine or vehicle location. `LOCATE ME` requests browser permission only after an explicit action and labels the result **DEVICE LOCATION**, never vehicle/radar location; location remains local to the browser. Follow-device watches are cleared when the Map view closes. Radar data appears only in a separate local X/Y metre scope and is not transformed into geographic coordinates. Routing remains `NOT CONNECTED` unless a real provider is separately configured and verified. Map rendering is advisory and never feeds local decision logic. The Settings page is read-only and exposes system, map, display, connection, simulation and about information without safety-parameter or motor controls.
