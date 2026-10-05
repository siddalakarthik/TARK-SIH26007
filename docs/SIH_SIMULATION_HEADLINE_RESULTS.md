# SIH SIMULATION HEADLINE RESULTS

Analytical/sensitivity research only. Assumed inputs are not measured NMDC values. Physical validation pending; production R1 remains unchanged and traction remains DISABLED_PHASE_1.

| Finding | Value | Conditions | Meaning | Does not prove |
| --- | --- | --- | --- | --- |
| 4 m visual reference | 2.12204 km/h | {"parameter_set": "reference", "trustworthy_perception_range_m": 4} | Small visual range severely constrains this model | A calibrated driver speed recommendation |
| 5 m visual reference | 3.87372 km/h | {"parameter_set": "reference", "trustworthy_perception_range_m": 5} | Model upper speed bound at 5 m | Radar range in fog |
| 18 km/h perception requirement | 18.8333 m | {"parameter_set": "reference", "speed_mps": 5, "trustworthy_perception_range_m": 40} | Required distance under declared reference parameters | Current hardware can perceive that far reliably |
| 36 km/h perception requirement | 51.3333 m | {"parameter_set": "reference", "speed_mps": 10, "trustworthy_perception_range_m": 40} | Quadratic braking cost matters | Full-scale truck validation |
| Stationary target clearance | 4.16667 m | {"parameter_set": "reference", "initial_separation_m": 40, "trustworthy_perception_range_m": 20, "speed_mps": 5, "encounter_type": "stationary"} | Point clearance after delayed detection and braking | Collision avoidance in arbitrary roads |
| 40 m concept cycle | 1 baseline-cycle units | {"parameter_set": "reference", "range_case_m": 40, "dwell_index": 0.25, "policy": "perception_concept"} | No added fog travel delay in this assumed case | A measured haul-cycle saving |
| 4 m visual throughput | 0.308192 baseline-throughput units | {"parameter_set": "reference", "range_case_m": 40, "dwell_index": 0.25, "policy": "visual_reference"} | Normalized travel restriction cost | Actual ore evacuation or MTPA impact |
| Uncertainty negative-margin share | 0.385725 fraction of engineering samples | {"samples": 40000} | Fraction of assumed candidate points failing the model constraint | Accident probability or reliability |

All rows: ASSUMED_SENSITIVITY; source row IDs and unrounded values are in `../studies/sih26007_simulation/results/final_simulation_summary.json`. Reference assumptions: delay 1.5 s, deceleration 1.5 m/s², fixed margin 2 m, perception reserve 1 m. Numbers are checked independently from the CSV.
