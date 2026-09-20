# TARK SIH26007 Public QA Fix Report

Date: 2026-09-20  
Scope: confirmed public-QA presentation defects only. The changes in this
report do not alter safety decisions, sensor contracts, motor authority,
ESP32 protocol, physical-hardware state, or `DISABLED_PHASE_1` traction.

## P1-001 — Map background initially blank

- Status: **FIXED / EXTERNAL REQUEST DIAGNOSTICS RETAINED**
- Exact configured initial request: `https://tiles.openfreemap.org/styles/liberty`.
- Root cause: the repository already used OpenFreeMap's published Liberty style
  URL and its CSP permitted HTTPS styles, tiles, sprites, glyphs and workers.
  The controlled browser could render the same production-built India basemap
  and its OpenFreeMap/OpenMapTiles/OpenStreetMap attribution. A direct request
  from the controlled-browser environment was blocked before networking with
  `ERR_BLOCKED_BY_CLIENT`; consequently it could not reproduce the reported
  public HTTP 404 or identify a different failed public subresource. This is
  an external browser-environment failure, not a malformed URL in TARK.
- Files changed: `frontend/src/mapConfig.ts`, `frontend/src/MapView.tsx`,
  `frontend/src/mapConfig.test.ts`.
- Fix: kept Liberty as the default and added a recovery path only for a failed
  *initial default-style* load. It retries OpenFreeMap's published Fiord style.
  An explicitly configured style is never replaced. The HMI now reports the
  failing resource URL in the map heading if recovery cannot complete.
- Evidence: local production build reached `MAP AVAILABLE`, rendered the India
  basemap, retained the simulation vehicle marker and separate local radar
  overlay, and showed no console errors.

## P1-002 — Mobile responsive layout

- Status: **FIXED**
- Root cause: at narrow breakpoints the header status layout was fragmented;
  the 1040 px rule also hid hardware/traction status text before the mobile
  layout replaced it.
- Files changed: `frontend/src/style.css`.
- Fix: compact responsive status grid at mobile widths, horizontally scrollable
  navigation that does not constrain workspace width, and retained hardware,
  traction and telemetry labels through the 1040 px breakpoint.
- Evidence: visual checks at 320, 375, 430, 768, 1024, 1440 and 1920 px found
  no document-level horizontal overflow and no zero-height map canvas.

## P3-001 — `NOT_CONNECTED` wraps badly

- Status: **FIXED**
- Root cause: generic `overflow-wrap:anywhere` split machine status tokens.
- Files changed: `frontend/src/features/sensors/SensorMatrix.tsx`,
  `frontend/src/features/dashboard/DriverView.tsx`, `frontend/src/style.css`,
  `frontend/src/features/sensors/SensorMatrix.test.tsx`.
- Fix: a narrowly scoped `status-token` class preserves complete status tokens
  without changing ordinary text wrapping.
- Evidence: 375 px visual check shows `NOT_CONNECTED` intact.

## P3-002 — `NORMAL_EVIDENCE` wraps badly

- Status: **FIXED**
- Root cause: the same generic word-breaking rule applied to safety reason
  codes.
- Files changed: `frontend/src/features/dashboard/DriverView.tsx`,
  `frontend/src/features/supervisor/SupervisorView.tsx`, `frontend/src/style.css`.
- Fix: the existing safety-code values use the same narrowly scoped
  no-wrap treatment.
- Evidence: 375 px visual check shows `NORMAL_EVIDENCE` intact.

## P3-003 — RGB camera header/spacer issue

- Status: **FIXED**
- Root cause: the vehicle RGB label and its state were adjacent inline content;
  the unavailable reason could duplicate the state text.
- Files changed: `frontend/src/features/sensors/CameraPanels.tsx`,
  `frontend/src/style.css`, `frontend/src/features/sensors/CameraPanels.test.tsx`.
- Fix: block-level label/state spacing and a distinct truthful unavailable-frame
  message. The camera remains `NOT_CONNECTED`; no live camera claim was added.
- Evidence: component test and 375 px Sensors review pass.

## P3-004 — Last log row clipped

- Status: **FIXED**
- Root cause: the scrollable event list had no bottom breathing room.
- Files changed: `frontend/src/style.css`.
- Fix: added bottom scroll padding and contained overscroll; event data and
  logging are unchanged.
- Evidence: the local event timeline was scrolled to its end at 375 px and its
  final rendered row cleared the panel boundary.

## P4-001 — Public Replay exposes recording creation

- Status: **FIXED**
- Root cause: the shared replay panel always rendered Start/Stop recording
  buttons, even when diagnostics identify a `public_demo` deployment.
- Files changed: `frontend/src/app/OperationsApp.tsx`,
  `frontend/src/features/replay/ReplayPanel.tsx`,
  `frontend/src/features/replay/ReplayPanel.test.tsx`.
- Fix: the public demo presents an evidence-viewer notice and omits both
  recording-creation controls. Local non-public deployments retain their
  existing controls after diagnostics load.
- Evidence: automated public-demo component test confirms neither control is
  rendered; replay playback controls remain available.

## Regression and browser evidence

- Backend: `97 passed`.
- Frontend: `25 passed`.
- Frontend TypeScript: passed.
- Production frontend build: passed (MapLibre lazy-chunk advisory only).
- Firmware Protocol V1 host tests: passed.
- Browser navigation checked: Dashboard → Map → Sensors → Replay → Settings →
  Safety → Logs → Dashboard → Map.
- Browser console: no errors or warnings caused by this fix set.
- Truthfulness retained: simulation labelled, browser location remains distinct
  from vehicle location, radar local X/Y remains distinct from global map
  coordinates, and traction remains `DISABLED_PHASE_1`.
