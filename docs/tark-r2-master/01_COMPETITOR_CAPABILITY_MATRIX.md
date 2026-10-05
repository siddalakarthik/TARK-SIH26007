# TARK R2 — competitor capability matrix

Revision M1 • 1 October 2026 • Technical research, not a team ranking.

## Evidence boundary

All ten requested YouTube URLs were attempted in this research pass. Direct retrieval failed through cache, redirect or access errors. **UNVERIFIED / VIDEO CONTENT NOT ACCESSIBLE** applies to the video content in every row. No footage was watched or timestamped in this pass, and no transcript was recovered.

The workspace's `outputs/TARK_R2_ENGINEERING_DECISION_PACKAGE_2026-10-01.md`, section N, preserves an earlier public-title/description review. The tables below explicitly reuse that secondary research record. They are not independent confirmation of any team's implementation. D-R = claim recorded from a public description in that earlier review; U = unknown. U never means absent. A title saying “prototype” does not demonstrate operation. Ten links represent nine proposal groups because TRINETRAM has two links. The earlier Electron link is outside this prompt's ten-link set.

## Video register

| ID | Prior-review name / source | Evidence retained | Distinguishing claim in the retained description |
|---|---|---|---|
| C01 | [MineSafe](https://youtu.be/GOyQf_GNT7Q) | D-R description; video inaccessible | Moving/braking model, ultrasonic/fog sensing, driver LCD/LED |
| C02 | [DRISHTI](https://youtu.be/qRZ9sj2lmfI) | D-R description; video inaccessible | AI/proximity alerts, GPS/V2V and risk-zone dashboard |
| C03 | [Vinay Sing presentation](https://youtu.be/t0B33FaZF88) | Empty description in prior review; video inaccessible | U |
| C04 | [PROXIMINE / SafePit](https://youtu.be/Ie0EXrxgxiQ) | D-R description; video inaccessible | Ultrasonic array, ESP-NOW, threshold warnings/stop, OLED/siren |
| C05 | [MINE VISION](https://youtu.be/9WJu2w7ZcDo) | D-R description; video inaccessible | Unspecified multimodal edge sensing, hazard coordinates, mesh, HUD/corridor |
| C06 | [SD creation](https://youtu.be/Hh2bfiNWxJk) | Empty description in prior review; video inaccessible | U |
| C07 | [Infranova / FogGuard](https://youtu.be/caDGaYjh_Bs) | D-R description; video inaccessible | Radar/LiDAR/camera/environment sensing, several links, control-room events |
| C08 | [FogX / SmartMine FogGuard](https://youtu.be/6SeRVo6gauU) | D-R description; video inaccessible | Radar/LiDAR/thermal/ultrasonic/visibility sensing and cooperative awareness |
| C09 | [TRINETRAM prototype](https://youtu.be/VJ8klSXAqU0) | Prototype in title only; video inaccessible | U |
| C10 | [TRINETRAM explanation](https://youtu.be/loNIiMsc1co) | Empty description in prior review; video inaccessible | U |

## Sensing / compute claims

| ID | Radar | LiDAR | RGB / camera | Thermal | Ultrasonic | Other sensing | Compute | AI/CV |
|---|---|---|---|---|---|---|---|---|
| C01 | U | U | U | U | D-R | D-R fog sensing, method U | U | U |
| C02 | U | U | U exact modality | U | U | D-R proximity, modality U | U | D-R AI detection |
| C03 | U | U | U | U | U | U | U | U |
| C04 | U | U | U | U | D-R array | U | U exact MCU | U |
| C05 | U | U | U | U | U | D-R multimodal, unspecified | D-R edge concept; board U | U specific algorithm |
| C06 | U | U | U | U | U | U | U | U |
| C07 | D-R | D-R | D-R camera; RGB implementation U | U | U | D-R BME280 | U | U specific algorithm |
| C08 | D-R | D-R | U | D-R | D-R | D-R visibility sensing, method U | U | U specific algorithm |
| C09 | U | U | U | U | U | U | U | U |
| C10 | U | U | U | U | U | U | U | U |

## Location / communication / operational claims

| ID | GPS/GNSS | RTK | V2V/V2I | Navigation | TTC / collision logic | Stop/cutoff |
|---|---|---|---|---|---|---|
| C01 | U | U | U | U | U formula; proximity concept | D-R braking model |
| C02 | D-R GPS | U | D-R V2V | U turn-by-turn | D-R risk zones; TTC U | U |
| C03 | U | U | U | U | U | U |
| C04 | U; no GNSS in described design, not proof of absence | U | D-R ESP-NOW | U | D-R distance thresholds; TTC U | D-R threshold stop |
| C05 | D-R hazard-coordinate concept; receiver U | U | D-R mesh | D-R corridor; route guidance U | D-R speed/proximity thresholds; TTC U | D-R motor cutoff |
| C06 | U | U | U | U | U | U |
| C07 | D-R GNSS | U | D-R LoRa/Wi-Fi/4G; exact peer roles U | U turn-by-turn | D-R risk assessment; TTC U | U demonstrated cutoff |
| C08 | D-R GPS | U | D-R V2V/V2I | U turn-by-turn | D-R collision-risk classification; TTC U | U demonstrated cutoff |
| C09 | U | U | U | U | U | U |
| C10 | U | U | U | U | U | U |

## HMI / integration claims

| ID | Dashboard/HMI | Fleet map | Digital twin | Physical prototype | Cloud/control room | Evidence replay |
|---|---|---|---|---|---|---|
| C01 | D-R LCD/LED | U | U | D-R motion/braking | U | U |
| C02 | D-R dashboard/risk zones | U detailed map | U | D-R | U hosting | U |
| C03 | U | U | U | U | U | U |
| C04 | D-R OLED/siren | U | U | D-R | U | U |
| C05 | D-R HUD/corridor | U | U | U | U | U |
| C06 | U | U | U | U | U | U |
| C07 | D-R dashboard/events | U detailed fleet view | U | D-R hardware/demo sequence | D-R control room; cloud U | Logs D-R; replay U |
| C08 | U detailed HMI | U | U | U | U detailed platform | U |
| C09 | U | U | U | Title only, U operation | U | U |
| C10 | U | U | U | U | U | U |

## Design consequences

The retained descriptions already overlap radar, cameras, thermal, GPS, cooperative links, warnings, dashboards and cutoff. These are therefore **not defensible standalone novelty claims for TARK**, even though implementation depth cannot be compared here.

TARK's proposed contribution is testable system behavior: source/freshness/calibration provenance, preserved sensor disagreement, evidence-bounded authority, uncertainty-aware conflict intervals, local operation through network loss, and decision replay. This is a design differentiation, **not a proven exclusive feature among these teams**. No claim that competitors lack it is justified by U cells.

Before making comparative performance claims, obtain accessible source footage/transcripts, timestamp observations, distinguish animation from acquired data, and compare target/environment/latency/failure conditions. This evidence limitation does not prevent the present hardware architecture decision.
