# 43 — Software implementation plan

No production code is created now. Use existing repository conventions; all paths below are proposed extensions unless identified existing.

| Actual boundary | Later work | Verification before integration |
|---|---|---|
| backend/app/sensors/ | Add TI processed-profile adapter; retain LD2450 bench path separately | Documented fixtures, malformed framing, valid-empty/missing |
| backend/app/camera.py and hardware/interfaces.py | Adapt existing camera ownership to B0200 formats; normalized contracts versioned | Timestamp/freeze/disconnect and media isolation |
| backend/app/thermal.py | Separate Lepton/PT3 adapter from existing MLX90640 path | Native mode/FFC/units, no fake radiometry |
| backend/app/imu.py | Separate BNO085 SPI/SH-2 acquisition from BNO055 | INT/RST/report validation and timestamp/error tests |
| backend/app/gnss_driver.py, gnss.py, location.py | LG290P profile/correction multiplexing and quality/reference extensions | One receiver owner; no real-mode simulator fallback |
| backend/app/hardware/ | Magnetic wheel response validation and provenance | Wrap/gap/slip fixtures; no ground-speed claim |
| backend/app/services/ | Add bounded R2 tracking/fusion/localization/navigation/fleet/risk modules under existing runtime owner | Pure deterministic algorithms and dependency-state tests |
| backend/app/communication/esp32/ | Preserve V2 host codec; review/version extensions separately | Shared vectors and host↔firmware roundtrip |
| firmware/esp32/main/ | Later reviewed board binding, wheel SPI and fail-disabled output profile | Exact board/pin evidence, host tests then authorized bench |
| backend/app/replay/ and logging/ | Versioned multisensor input/checkpoint/media references | Full-session integrity, isolation and compatibility |
| backend/app/main.py and domain/ | Versioned projections, health and approved operations context | API/WebSocket contracts, one runtime independent of observers |
| frontend/src/ | Existing pages and MapLibre updated to consume calculated outputs | No browser business/authority duplication; one subscription |
| backend/tests/; frontend tests; firmware/esp32/tests/ | Regression and new fixtures in current suites | Deterministic pass/fail, resource and adversarial coverage |
| config/; scripts/; docs/ | Versioned profiles, reviewed deployment and operator guidance | Dry-run/read-only paths, no surprise hardware openers |

Sequence: contract fixtures → acquisition stubs with truthful unavailable state → concrete adapters → timing/calibration → tracking/fusion → motion/localization → graph/navigation → authenticated fleet/conflict → shadow envelope/state → HMI/replay → reviewed endpoint extensions/binding → complete regressions → physical gates.

R1 compatibility remains pinned. No BNO085 is disguised behind a BNO055 device identity, no PT3 behind MLX90640 format, and no IWR1843 behind LD2450 bytes. UI reuse does not mean hardware driver reuse is complete. Do not put a second observation/command pipeline beside the existing owner.

Every change needs a source/mode test, missing/stale/error test, bounded-resource test and replay impact review. A later implementation task, not this architecture package, authorizes code and dependency changes.
