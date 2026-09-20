# Test Report

Last final-master audit run: 2026-09-15.

| Check | Result | Status |
|---|---|---|
| Backend configuration, safety pipeline, API, WebSocket, map safety and deployment tests | 30 passed | VERIFIED |
| Frontend contract, map/device-location/camera readiness and HMI interaction tests | 17 passed | VERIFIED |
| Frontend production build | Vite build passed | VERIFIED |
| ESP32 C source compilation, protocol supervisor and safe hardware-boundary tests | GCC `-Wall -Wextra -Werror -fsyntax-only` passed | VERIFIED |
| ESP32 host executable behavior | CRC-32C, sequence/expiry/heartbeat, safe MDD10A zero-output, simulated encoder freshness and watchdog-boundary checks passed | VERIFIED |
| Local HMI same-origin telemetry | Browser loaded and connected at `http://localhost:8000` | VERIFIED |
| Two-tab local HMI | Two tabs independently connected; traction stayed disabled | VERIFIED |
| Responsive HMI | 320–1920 px CSS viewport checks; no document overflow after mobile event-row fix | VERIFIED |
| Browser console | No error/warning messages observed in local HMI | VERIFIED |
| Static production-source transport audit | No hard-coded production localhost/URL-token transport dependency | VERIFIED |
| Frontend bundle credential audit | No `TARK_ACCESS_TOKEN` or test token in compiled frontend assets | VERIFIED |
| Docker build/runtime | Docker CLI not installed on this workstation | NOT VERIFIED |
| Render Blueprint static validation | Docker runtime, `plan: free`, `/ready`, public-demo profile | VERIFIED |
| Render/public HTTPS/WSS | No hosting account/hostname available | NOT VERIFIED |
| Physical mobile/external network | No external device/network test available | NOT VERIFIED |

The final-polish backend run completed with **30 passed** and three non-failing warnings: two upstream TestClient deprecation warnings and one sandbox-denied pytest-cache write. The frontend completed with **17 passed** and a production build. They are not TARK test failures. The MapLibre lazy-loaded bundle remains approximately 808 kB before gzip; it is loaded only when the Map view opens. This is documented as a non-blocking performance observation, not a Raspberry Pi measurement. OpenFreeMap Liberty India-overview checks passed at 320, 360, 390, 412, 768, 1024, 1280, 1440 and 1920 px with no document-level horizontal overflow. No geographic vehicle data is fabricated and radar remains in a separate local-coordinate scope.

Simulation-only truth remains intact: no test run validates real LD2450 parsing, ESP32 USB operation, physical actuator response, encoder response, motor operation, physical E-stop, timing, stopping distance, or mine safety behavior.
