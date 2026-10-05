# 26 — Dataset strategy

Pretraining learns initial representations. Benchmarking compares methods on a defined held-out dataset. Prototype validation measures the actual TARK hardware/configuration. These are different evidence levels; none of the public datasets below is Bailadila validation.

| Dataset / primary reference | Appropriate use | Not transferable automatically |
|---|---|---|
| [RADIal](https://github.com/valeoai/RADIal) | Radar/camera research methodology and cross-modal tasks | Raw high-definition radar format/calibration != IWR1843 processed UART |
| [CARRADA](https://github.com/valeoai/carrada_dataset) | Radar-camera association/annotation method studies | Its radar tensors/sensor setup are not plug-in TARK frames |
| [nuScenes paper](https://arxiv.org/abs/1903.11027) | Multisensor tracking, coordinate/time conventions | Urban multi-camera/radar/LiDAR setup is not a front-only mine system |
| [FLIR ADAS](https://oem.flir.com/en-gb/solutions/automotive/adas-dataset-form/) | Thermal/visible detector research | Camera resolution/optics/registration != Lepton 160×120; temperatures not assumed |
| [BDD100K](https://github.com/bdd100k/bdd100k) | Road-scene visual pretraining/benchmark | Mining machinery, terrain and monsoon coverage not established |
| [Foggy Cityscapes / Foggy Driving](https://people.ee.ethz.ch/~csakarid/SFSU_synthetic/) | Synthetic versus real fog-domain generalization studies | Synthetic optical fog does not validate radar/thermal or local aerosol physics |

Some project pages were inaccessible in direct retrieval; use linked author/manufacturer repositories/publications, and verify exact download version/license/terms before use. No dataset was downloaded or trained in this task. Record license, attribution, class mapping, consent/privacy limits, split and checksum. Model/data licenses require release review, not an assumed commercial permission.

## Custom TARK_DATASET layout

```text
TARK_DATASET/
  run_<id>/
    manifest.json
    calibration/
    radar/
    rgb/
    thermal/
    gnss/
    imu/
    wheels/
    fleet/
    decisions/
    endpoint/
    reference_truth/
    environment/
    annotations/
```

This is a proposed organization, not files created now. Manifest records source modes, physical identities, map/datum, clocks, software/model/configuration hashes, conditions, target arrangement, independent reference uncertainty, sequence coverage and exclusions. Store original raw/normalized evidence and derived annotations separately; no silent relabelling of generated frames as real imagery.

Split by RUN, site/trajectory and relevant acquisition day/conditions; prevent adjacent frames and repeated object placements leaking across training/evaluation. Group synthetic variants with their original clear scene. Reserve locked held-out runs before tuning; report per-condition results including failure cases. Annotate object class/geometry only where visible/reference-supported; unresolved labels remain uncertain, not invented.

Use independent measured ground truth, not TARK's own outputs as truth. Label reviewer agreement/disagreement and time-alignment uncertainty. Compare fixed versus uncertainty-aware methods on the same runs and disclose abstentions/availability, not only accuracy on easy accepted frames.
