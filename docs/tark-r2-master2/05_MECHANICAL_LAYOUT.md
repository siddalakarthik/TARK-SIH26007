# 05 — Mechanical layout

Body B: x forward, y left, z up. Origin: midpoint of measured wheel-contact rectangle projected to ground. Measure chassis L/W, wheel radius/width, track b, axle spacing, clearance, hub/shaft diameters, axial/radial room, fastener pattern, plate thickness and load deflection. Use calipers/rule/square with recorded uncertainty, never generic TT dimensions.

| Item | Height/forward/lateral strategy | Yaw/pitch/roll | Service/connector clearance | Risks |
|---|---|---|---|---|
| Radar | z_R above measured chassis occlusion; x_R front; y_R near center | Forward, calibrated tilt/roll | Plug, bend radius, removal access | No metal across antenna; cover characterization |
| RGB | Close to radar/thermal plane; measured offset | Forward/calibrated | Lens access/USB relief | Near-focus blind zone, glare |
| Thermal | Near RGB with measured baseline | Calibrated transform | Core service/cable access | No assumed LWIR-transparent ordinary glass/acrylic |
| GNSS antenna | High practical open view, rigid | Supplier installation | RF bend/connector access | EMI/multipath, ground-plane requirement unknown |
| IMU | Rigid central body, away from motor fields | Recorded body alignment | SPI/INT/RST access | Vibration/magnetic contamination |
| Jetson/hub/SSD | Low and central | Cooling orientation | Fan intake/exhaust/service | Heat/liquid ingress |
| Electronics pack | Low, secured, separate heat | Manufacturer constraints | Isolation/inspection | Mass/retention |
| ESP/driver | Short control/reference route, driver heat separated | Terminals readable | Cutoff accessible | High-current interference |
| Display | Operator-facing, limited mast height | Readable tilt | HDMI/USB relief | CG/glare |
| Wheel carriers | One wheel per side, on-axis | Per selected assembly | Rotating clearance/guard | PHYSICAL GEOMETRY DEPENDENT |

All coordinates/angles are variables for the measured drawing, not released dimensions. Cable clearance C >= plug length + minimum bend radius + tool allowance. Harness length = measured routed path plus documented service loop. Separate motor/switching wiring from SPI/RF; no pinch or wheel snag.

CG = sum(m_i r_i)/sum(m_i). Weigh complete payload; qualify chassis stiffness before mounting. Static lateral tip illustration a_y < g(b/2−abs(y_CG))/h_CG excludes bumps/compliance, so it is not an operating limit. Angular mount error delta_theta causes approximately R delta_theta lateral projection error. Allocate this error before selecting bracket material/thickness.

Rigid aluminum/appropriate structural brackets are a fabrication direction within R03, not a new selected chassis. If payload fails, report a CR before any platform replacement. A stationary sensor fixture plus separate model may support limited tests, but must never be presented as one integrated moving system. Recalibrate after remount; use [06](06_SENSOR_GEOMETRY_AND_CALIBRATION.md) and [44](44_HARDWARE_COMMISSIONING_GATES.md).
