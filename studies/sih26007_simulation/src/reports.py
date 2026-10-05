"""Reports extract numbers from published CSV tables, not generator state."""
import json
from .experiments import read_csv,write_csv

NAMES=['TARK_SIH26007_SIMULATION_REPORT','SIH_SIMULATION_HEADLINE_RESULTS','SIH_SIMULATION_PPT_RESULT_CARD','SIH_REQUIREMENT_TO_RESULT_MATRIX','SIH_SIMULATION_FEASIBILITY_REPORT','SIH_OPERATIONAL_IMPACT_SIMULATION','SIH_SIMULATION_JUDGE_QA','PPT_SIMULATION_PATCH_SHEET']
DOCS=['docs/'+n+'.md' for n in NAMES]
BOUNDARY='Analytical/sensitivity research only. Assumed inputs are not measured NMDC values. Physical validation pending; production R1 remains unchanged and traction remains DISABLED_PHASE_1.'


def mdtable(headers,values):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(str(v) for v in row)+' |\n' for row in values)


def generate(root,repo,d,t,verification):
    tables={p.stem:read_csv(p) for p in sorted((root/'tables').glob('*.csv'))}
    def select(name,**conditions):
        return [r for r in tables[name] if all(str(r[k])==str(v) or _numeric_equal(r[k],v) for k,v in conditions.items())]
    def one(name,**c):
        a=select(name,**c)
        if len(a)!=1:raise ValueError(f'headline selector not unique: {name} {c}: {len(a)}')
        return a[0]
    def f(v):return f'{float(v):.6g}'
    def report(name,text):
        (repo/'docs'/f'{name}.md').write_text('# '+name.replace('_',' ')+'\n\n'+BOUNDARY+'\n\n'+text.rstrip()+'\n',encoding='utf-8',newline='\n')
    headlines=[]
    def headline(name,table,key,unit,conditions,meaning,not_meaning,figure):
        r=one(table,**conditions)
        headlines.append(dict(name=name,value=float(r[key]),units=unit,conditions=conditions,provenance='ASSUMED_SENSITIVITY',
             result_class=r['result_class'],meaning=meaning,does_not_prove=not_meaning,source_table=f'tables/{table}.csv',scenario_id=r['scenario_id'],field=key,figure=figure))
    headline('4 m visual reference','sim01_safe_speed_vs_range','speed_kmph','km/h',{'parameter_set':'reference','trustworthy_perception_range_m':4},'Small visual range severely constrains this model','A calibrated driver speed recommendation','sim01_visual_reference')
    headline('5 m visual reference','sim01_safe_speed_vs_range','speed_kmph','km/h',{'parameter_set':'reference','trustworthy_perception_range_m':5},'Model upper speed bound at 5 m','Radar range in fog','sim01_visual_reference')
    headline('18 km/h perception requirement','sim09_fullscale_requirements','required_perception_range_m','m',{'parameter_set':'reference','speed_mps':5,'trustworthy_perception_range_m':40},'Required distance under declared reference parameters','Current hardware can perceive that far reliably','sim09_required_perception_range')
    headline('36 km/h perception requirement','sim09_fullscale_requirements','required_perception_range_m','m',{'parameter_set':'reference','speed_mps':10,'trustworthy_perception_range_m':40},'Quadratic braking cost matters','Full-scale truck validation','sim09_required_perception_range')
    headline('Stationary target clearance','sim03_encounters','minimum_clearance_m','m',{'parameter_set':'reference','initial_separation_m':40,'trustworthy_perception_range_m':20,'speed_mps':5,'encounter_type':'stationary'},'Point clearance after delayed detection and braking','Collision avoidance in arbitrary roads','sim03_clearance_map')
    headline('40 m concept cycle','sim08_operational_continuity','normalized_cycle_time','baseline-cycle units',{'parameter_set':'reference','range_case_m':40,'dwell_index':.25,'policy':'perception_concept'},'No added fog travel delay in this assumed case','A measured haul-cycle saving','sim08_cycle_time_comparison')
    headline('4 m visual throughput','sim08_operational_continuity','normalized_productivity','baseline-throughput units',{'parameter_set':'reference','range_case_m':40,'dwell_index':.25,'policy':'visual_reference'},'Normalized travel restriction cost','Actual ore evacuation or MTPA impact','sim08_productivity_retention')
    headline('Uncertainty negative-margin share','sim07_uncertainty_samples_summary','negative_margin_fraction','fraction of engineering samples',{'samples':max(d['uncertainty']['counts'])},'Fraction of assumed candidate points failing the model constraint','Accident probability or reliability','sim07_margin_distribution')
    headline_rows=[[h['name'],f(h['value'])+' '+h['units'],json.dumps(h['conditions']),h['meaning'],h['does_not_prove']] for h in headlines]
    headline_text=mdtable(['Finding','Value','Conditions','Meaning','Does not prove'],headline_rows)
    report('SIH_SIMULATION_HEADLINE_RESULTS',headline_text+'\nAll rows: ASSUMED_SENSITIVITY; source row IDs and unrounded values are in `../studies/sih26007_simulation/results/final_simulation_summary.json`. Reference assumptions: delay 1.5 s, deceleration 1.5 m/s², fixed margin 2 m, perception reserve 1 m. Numbers are checked independently from the CSV.\n')
    visual=select('sim01_safe_speed_vs_range')
    visual=[r for r in visual if r['visibility_m']]
    visual_text=mdtable(['Parameter set','Visual reference (m)','Model cap (m/s)','Model cap (km/h)','Margin at cap (m)'],[[r['parameter_set'],r['visibility_m'],f(r['speed_mps']),f(r['speed_kmph']),f(r['safety_margin_m'])] for r in visual])
    full=select('sim09_fullscale_requirements',trustworthy_perception_range_m=40)
    full_text=mdtable(['Set','Candidate speed (km/h)','Required range (m)','Max delay at 40 m (s)','Min deceleration at 40 m (m/s²)'],[[r['parameter_set'],f(r['speed_kmph']),f(r['required_perception_range_m']),f(r['max_response_delay_s']) if r['max_response_delay_s'] else 'INFEASIBLE',f(r['min_effective_deceleration_mps2']) if r['min_effective_deceleration_mps2'] else 'INFEASIBLE'] for r in full])
    encounters=select('sim03_encounters',parameter_set='reference',initial_separation_m=40,trustworthy_perception_range_m=20,speed_mps=5)
    encounter_text=mdtable(['Encounter','Initial closing rate (m/s)','TTC research metric (s)','Minimum clearance (m)','Finite-horizon margin (m)','Modeled overlap'],[[r['encounter_type'],f(r['initial_closing_rate_mps']),f(r['ttc_analysis_s']),f(r['minimum_clearance_m']),f(r['safety_margin_m']),r['model_collision']] for r in encounters])
    encounter_text+='\nReference case: own 5 m/s, initial separation 40 m, detection range 20 m; target speed stationary 0, lead 2.5, oncoming -5 m/s. Target never brakes. Horizon: own stop plus 5 s. Negative clearance denotes mathematical overlap, not post-impact physics. Oncoming vehicles continuing indefinitely eventually hit a stopped ego vehicle; finite-horizon clearance cannot establish permanent avoidance. Vehicle geometry is reduced to front-to-front clear gap, with no width, steering, grade, lateral trajectories or brake buildup.\n'
    cycle=select('sim08_operational_continuity',range_case_m=40,dwell_index=.25)
    cycle_text=mdtable(['Set','Policy','Cycle-time index','Throughput index','Halt fraction'],[[r['parameter_set'],r['policy'],f(r['normalized_cycle_time']),f(r['normalized_productivity']),f(r['halt_fraction'])] for r in cycle])
    cycle_text+='\nOne clear-condition cycle = 1: fixed activities 0.4, nonfog travel 0.3, fog travel 0.3. Desired speed 5 m/s; constrained fog travel scales by desired/allowed speed. A halt adds a dwell index (0, 0.25 or 1) and then resumes at the cap for a separately assumed 40 m recovery envelope. Halt duration is not inferred from fog or sensors. The zero-dwell case is an instantaneous-recovery sensitivity bound, not a realistic guaranteed recovery. Nonfog travel is held constant and is not a vehicle-dynamics calculation. Throughput is 1/cycle, without tonnage or fleet scaling. At short range there may be no improvement; across dwell assumptions halting can outperform prolonged slow travel. Thus superiority is conditional, not universal.\n'
    uncertainty=tables['sim07_uncertainty_samples_summary'];last=uncertainty[-1]
    uncertainty_text=mdtable(['Samples','Minimum (m)','5th (m)','Median (m)','95th (m)','Maximum (m)','Negative fraction'],[[r['samples'],*[f(r[k]) for k in ['minimum_m','p05_m','median_m','p95_m','maximum_m','negative_margin_fraction']]] for r in uncertainty])
    rank=sorted(tables['sim07_sensitivity'],key=lambda r:abs(float(r['pearson_correlation'])),reverse=True)
    uncertainty_text+='\nSeed 26007; independent uniforms: delay 0.5–2.5 s, deceleration 0.5–3 m/s², reserve 0.5–5 m, trustworthy range 3–100 m, candidate speed 0–15 m/s; fixed margin 2 m. These distributions are study choices, not fitted mine distributions. Percentiles use linear interpolation. The final 20,000→40,000 prefix comparison passed the predeclared 0.02 fraction and 3 m percentile stability thresholds. This is a limited numerical stability diagnostic, not statistical confidence or distributional convergence proof. Largest absolute marginal Pearson correlation: '+rank[0]['parameter']+' ('+f(rank[0]['pearson_correlation'])+'); dependent on the chosen bounds and not a universal importance ranking. Negative-margin fraction is NOT an accident probability.\n'
    integrated=tables['sim10_integrated'];duration=sum(float(r['epoch_duration_s']) for r in integrated)
    available=sum(float(r['epoch_duration_s']) for r in integrated if r['operation_available']=='True')/duration
    restricted=sum(float(r['epoch_duration_s']) for r in integrated if r['restricted']=='True')/duration
    halted=sum(float(r['epoch_duration_s']) for r in integrated if r['halted']=='True')/duration
    visualprogress=sum(float(r['epoch_duration_s'])*min(t['desired_speed_mps'],float(r['visual_reference_cap_mps'])) for r in integrated)/(duration*t['desired_speed_mps'])
    conceptprogress=sum(float(r['epoch_duration_s'])*float(r['speed_mps']) for r in integrated)/(duration*t['desired_speed_mps'])
    continuity=dict(duration_s=duration,model_available_fraction=available,restricted_fraction=restricted,halted_fraction=halted,normalized_cap_time_integral=conceptprogress,visual_cap_time_integral=visualprogress,
                    meaning='Condition-epoch capability integral, NOT traveled distance or a dynamic haul cycle; transitions require separate physical feasibility validation')
    (root/'results/integrated_continuity.json').write_text(json.dumps(continuity,indent=2)+'\n',encoding='utf-8',newline='\n')
    integrated_text=mdtable(['Epoch (s)','Condition','Visual (m)','Effective range (m)','Cap (km/h)','State','Link'],[[r['epoch_start_s'],r['event'],r['visibility_m'],r['trustworthy_perception_range_m'],f(r['speed_kmph']),r['analytical_state'],r['link_available']] for r in integrated])
    integrated_text+=f'\nEqual-duration condition assessment: available {available:.6g}, restricted {restricted:.6g}, halted {halted:.6g}; normalized cap-time integral {conceptprogress:.6g} versus visual reference {visualprogress:.6g}. This is a continuity indicator, not actual distance or a physical speed trajectory. Cap changes are not instantaneous braking commands. Receiver expiry/session behavior comes from separate verified SIM-06 R1 traces, not from these synthetic booleans.\n'
    fault=tables['sim06_fault_story'];fault_text=f'{len(fault)} recorded steps across nine verified R1 scenarios EV-03,05,07,10,11,13,14,15,20. All projected live speed/left/right commands are zero; traction is DISABLED_PHASE_1. Freshness, communications, session, receiver reason and state are copied from the existing evidence. The analytical cap column is a separate research overlay, not production output. It is zero throughout these selected recorded conditions, so these traces demonstrate no positive-speed research benefit. Controlled logical time is not measured Pi/ESP32 latency. See `tables/sim06_fault_story.csv` and the R1 evidence manifest for original provenance.\n'
    fault_metrics=[]
    for sid in dict.fromkeys(r['source_scenario'] for r in fault):
        rs=[r for r in fault if r['source_scenario']==sid]
        expiry=next((r for r in rs if r['receiver_reason']=='COMMAND_EXPIRED'),None)
        fault_metrics.append(dict(source_scenario=sid,first_sampled_expiry_s=expiry['controlled_time_s'] if expiry else '',
             maximum_research_cap_mps=max(float(r['analytical_cap_mps']) for r in rs),
             maximum_live_command=max(abs(float(r[k])) for r in rs for k in ['live_permitted_speed_mps','live_left_command','live_right_command']),
             recovery_actions='; '.join(r['action'] for r in rs if r['action'] in ['RESTART_RECEIVER','RESTART_SENDER','TRANSPORT_RECONNECT','RESTORE_COMMUNICATION']),
             interpretation='First observed expiry sample, NOT physical latency; blank means no expiry sample in selected trace'))
    write_csv(root/'results/fault_metrics.csv',fault_metrics)
    fault_text+=mdtable(['Trace','First sampled expiry (controlled s)','Max research cap (m/s)','Live command maximum','Recovery actions'],[[r['source_scenario'],r['first_sampled_expiry_s'] or 'not observed',r['maximum_research_cap_mps'],r['maximum_live_command'],r['recovery_actions'] or 'none'] for r in fault_metrics])
    fault_text+='\nExpiry threshold remains the existing Protocol V2 rule; sparse observation at 0.7 s is not a measured 0.7 s response guarantee. FIG-08 uses ordered steps with controlled-time labels so simultaneous events do not hide restart/recovery transitions.\n'
    mapping={1:['09'],2:['04','05','10'],3:['01'],4:['01','02','07','09'],5:['03','10'],6:['01','04','08'],7:['08'],8:['08'],9:['04','08','10'],10:['05','06','07'],11:['02','07'],12:['03','10'],13:['06','10'],14:['09']}
    requirement_names=['Open-cast setting','Monsoon/fog','3–5 m visibility','HEMM safe movement','Collision risk','Slow/stop operation','Haul-cycle delay','Productivity impact','Continuity','Reliability','Safe and efficient movement','Operator guidance','Real-time monitoring','Scalability']
    table_by_sim={f'{i:02d}':next(k for k in tables if k.startswith(f'sim{i:02d}_')) for i in range(1,11)}
    matrix=mdtable(['Requirement','Official condition/outcome','Studies','Evidence tables','Status / limitation'],[[f'REQ-SIH-{i:02d}',requirement_names[i-1],', '.join('SIM-'+s for s in sims),'; '.join(table_by_sim[s]+'.csv' for s in sims),'Scoped analytical support; physical outcome NOT VERIFIED'] for i,sims in mapping.items()])
    report('SIH_REQUIREMENT_TO_RESULT_MATRIX',matrix+'\nAll source locations are in `../studies/sih26007_simulation/SIH_REQUIREMENTS_TRACEABILITY.md`. Coverage is not equivalent to field satisfaction.\n')
    feasibility=full_text+'\nRequirements are grade-neutral sensitivity results. Effective deceleration, response, margin and uncertainty must be measured for vehicle load, road surface, slope, tire/brake state and deployment conditions. No friction coefficient, truck mass, mine geometry or regulatory stopping limit is invented. The simplified point model cannot establish full-scale compliance. LD2450 raw acquisition/decoder provenance limitations and all electrical HOLDs remain those of R1. No claimed radar immunity, thermal detection curve, IMU accuracy, GNSS availability or EKF fusion capability is added. A scaled prototype cannot validate HEMM sensing/braking distances.\n'
    report('SIH_SIMULATION_FEASIBILITY_REPORT',feasibility)
    report('SIH_OPERATIONAL_IMPACT_SIMULATION',cycle_text+'\n## Integrated condition-epoch continuity\n\n'+integrated_text)
    questions=[
      ('Is any simulator mandated?','No specific tool/method was mandated in the official 2026 PS, guidelines and template reviewed; Digital Twin is optional.'),
      ('Where does 3–5 m come from?','Official PS background describes visual visibility. Four metres is a derived midpoint, not a separately measured condition.'),
      ('Does 3 m visibility mean 3 m radar range?','No. Visual and trustworthy perception ranges are independent study variables.'),
      ('Are these NMDC braking values?','No. All vehicle response, deceleration and reserve sets are assumed sensitivity inputs.'),
      ('Is the cap a safe driving instruction?','No. It is a bound within an unvalidated constant-deceleration model.'),
      ('What is live motor output?','Exactly zero in the R1 evidence. DISABLED_PHASE_1 remains unchanged.'),
      ('Is TTC controlling the live vehicle?','No. Encounter TTC here is a research relative-motion metric, not new production behavior.'),
      ('Does the system avoid oncoming impact?','Not guaranteed. The target never brakes; continuing oncoming motion eventually reaches a stopped ego.'),
      ('What does negative clearance mean?','A predicted model overlap before the finite horizon; no post-impact physical model is implemented.'),
      ('Are slopes included?','No unsupported grade/friction inputs are introduced. Validate effective deceleration over actual conditions.'),
      ('Is uncertainty failure share accident probability?','No. It is the negative-margin fraction over arbitrary independent engineering input distributions.'),
      ('How was sample count chosen?','Prespecified prefix sizes through 40,000 and stated fraction/percentile stability tolerances; not tuned to attractive results.'),
      ('How are headline numbers checked?','Independent bisection, exported-row arithmetic, percentile interpolation and cycle recomputation; corruption must be rejected.'),
      ('Can we claim production gains?','Only normalized cycle/throughput indices under declared shares, speeds and dwell assumptions; no tonnage/MTPA forecast.'),
      ('Can halt-and-recover be better?','Yes. Assumed dwell and recovery capability determine the result. No universal superiority claim is justified.'),
      ('What is the Pareto interpretation?','At fixed resource assumptions, increasing speed consumes margin; optimize only inside nonnegative model margin.'),
      ('Has sensor fusion been integrated?','No new fusion/EKF is implemented or credited. Archived fusion research is not a production capability.'),
      ('Is this a mine digital twin?','No. It is a reproducible longitudinal and operational sensitivity study, without calibrated mine geometry or plant dynamics.'),
      ('What remains for hardware?','Identity, wiring/voltage/HOLD resolution, sensor calibration, range/freshness, loaded stopping and delay measurement, physical watchdog/E-stop and supervised trials.'),
      ('Can this be reproduced without equipment?','Yes. Run the isolated study command and verifier, then R1 regression commands. No COM/USB/I2C access is required.')]
    report('SIH_SIMULATION_JUDGE_QA','\n\n'.join(f'## {i}. {q}\n\n{a}' for i,(q,a) in enumerate(questions,1)))
    report('SIH_SIMULATION_PPT_RESULT_CARD','## Evidence card — research only\n\n'+mdtable(['Finding','Value','Assumptions'],[[h['name'],f(h['value'])+' '+h['units'],'Reference set unless uncertainty row; see headline report'] for h in headlines[:6]])+'\nUse FIG-01/FIG-03 for method, FIG-11 for feasibility, FIG-09/FIG-10 for impact. Do not present the modeled speed as the live motor command. No hardware or mine-safety certification is claimed.\n')
    report('PPT_SIMULATION_PATCH_SHEET',mdtable(['Existing slide','Add / replace within current six-slide limit','Suggested caption','Do not claim'],[
      ['3 Technical approach','FIG-03 plus stopping equation; replace redundant decorative graphic','Analytical operating envelope; reference assumed parameters','Validated safe speed or production TTC control'],
      ['4 Feasibility/viability','FIG-11 plus 18/36 km/h requirement rows','Full-scale sensing requirement, not achieved prototype range','Mine-ready hardware or measured latency'],
      ['5 Impact/benefits','FIG-09 or FIG-10 plus normalized cycle table','Conditional normalized continuity benefit; no tonnage forecast','MTPA gains or universal throughput improvement']])+'\nNo PPT/PDF deck was edited. Preserve official six-slide maximum including title and existing electrical/physical-validation limitations. Keep data captions legible; do not stack the full figure collection in the submission.\n')
    selected_rows=tables['sim02_operating_envelope'];negative=sum(float(r['safety_margin_m'])<0 for r in selected_rows)
    summary={'official_requirements_count':14,'simulations_completed':[f'SIM-{i:02d}' for i in range(1,11)],
       'scenario_count':sum(len(v) for k,v in tables.items() if k not in ['sim07_samples','sim07_sensitivity','sim07_uncertainty_samples_summary','safety_efficiency_trade_space']),
       'scenario_count_definition':'Deterministic exported assessment rows, including repeated conditions across different questions and copied R1 steps; excludes uncertainty and derived Pareto/summary tables',
       'deterministic_runs':1,'uncertainty_samples':max(d['uncertainty']['counts']),'visibility_cases':[3,4,5],
       'headline_results':headlines,'most_sensitive_parameter':rank[0],'fullscale_required_range_results':full,
       'normalized_productivity_results':cycle,'safety_constraint_violations_detected':negative,
       'violation_definition':'Negative margins among unconstrained SIM-02 candidate grid; expected infeasible candidates, not unsafe commands',
       'model_failures':0,'physical_validation':False,'hardware_access':False,'production_code_modified':False,
       'numerical_verification':verification,'integrated_continuity':continuity}
    (root/'results/final_simulation_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    model='D_stop = v·t + v²/(2a) + m; R_required = D_stop + u; margin = R_trustworthy − R_required. Units: metres, seconds, m/s, m/s²; multiply m/s by 3.6 for km/h. Positive-root inverse gives maximum speed; if R ≤ m+u there is no positive admissible speed. Zero cap below reserves is NOT proof of feasibility. Age is added to response time in this research overlay; stale/missing/out-of-order evidence grants no positive capability. This overlay does not replace R1 production freshness, state transitions or hard cap.'
    params=mdtable(['Set','Delay s','Deceleration m/s²','Margin m','Reserve m'],[[k,*v.values()] for k,v in d['sets'].items()])
    limitations='Constant effective deceleration and response, longitudinal point-gap geometry, no grade, brake buildup, tire/road model, sensing physics, lateral path planning, driver response distribution, measured sensor reliability, fleet dispatch or validated mine production inputs. Condition timelines are not dynamic vehicle trajectories. Operator/control-room outcomes are supported by explanations, not human-factors trials. Monte Carlo bounds are not empirical distributions. A finite-horizon oncoming result is not permanent collision avoidance. Hashes are content fingerprints, not digital signatures.'
    lineage='The production R1 pipeline uses stopping-distance algebra, tracked envelope/uncertainty and explicit maturity gates, with hard_cap_mps = 0. This independent study reuses the dimensional stopping principle but inverts it for research and adds encounter/normalized-cycle calculations. Study reference parameters are NOT production configuration. SIM-06 copies existing verified R1 traces; all other nonzero speed values are analytical, never commands. Archived simulations 1/2/3 were examined for lineage only; their outputs are not reused as verified numbers. No archived EKF result is credited to production.'
    inventory=json.loads((root/'results/figure_inventory.json').read_text())
    figure_text='\n'.join(f'- `{x["figure"]}.png` / `.svg` ← `{x["source_table"]}`' for x in inventory)
    sections=[('Executive summary',headline_text),('Exact SIH26007 requirement extraction',matrix),('Whether SIH mandates a specific simulator','No specific method/tool mandated by the reviewed official sources. See source-locked traceability document.'),('Simulation selection rationale','See `SIMULATION_SELECTION_MATRIX.md`: ten bounded engineering questions; no unrelated simulator added.'),('Source authority','Three archived official 2026 sources with URLs, dates and SHA-256 in sources/source_inventory.json. PS supplies visual 3–5 m, not physical sensor/braking performance. Exclude secondary AI-generated reports as numerical authority.'),('Parameter provenance',params+'\nAll numeric controls are inventoried in inputs/parameter_registry.csv. The visual endpoints are OFFICIAL_SIH, 4 m DERIVED, freshness CURRENT_TARK_CONFIG, other physical values ASSUMED_SENSITIVITY.'),('Mathematical model',model),('Model assumptions',limitations),('SIM-01 results',visual_text),('SIM-02 results',f'{len(selected_rows)} grid candidates; {negative} have negative model margin and are infeasible at their candidate speed. Cap is computed separately; no negative-margin optimization is permitted. See FIG-03 and full CSV.'),('SIM-03 results',encounter_text),('SIM-04 results','Five independent condition epochs: visual range can fall while separately assumed trustworthy range remains unchanged; range loss and evidence loss reduce cap. See sim04_fog_transition.csv. No fog-to-radar transfer law is inferred.'),('SIM-05 results','Valid target, valid empty, missing and out-of-order evidence are separated. Empty space is not certified observable distance. Age consumes response budget and stale evidence halts analytical capability. Range contraction/uncertainty increase cannot increase cap. See sim05_perception_degradation.csv.'),('SIM-06 results',fault_text),('SIM-07 results',uncertainty_text),('SIM-08 results',cycle_text),('SIM-09 results',feasibility),('SIM-10 results',integrated_text),('Safety–efficiency trade space','Within each fixed sensing/parameter case the positive-speed/remaining-margin curve is non-dominated: speed consumes margin. Different sensing resources are not free Pareto improvements. Optimization maximizes speed subject to nonnegative margin and declared bounds; never exchange negative margin for productivity.'),('Robustness / sensitivity',uncertainty_text),('Operational continuity',cycle_text),('Full-scale HEMM requirements',full_text),('Most important numerical findings',headline_text),('SIH requirement-to-result matrix',matrix),('Comparison to current R1 production maturity',lineage),('Limitations',limitations),('Physical validation still required','Keep all controlled electrical HOLDs. Verify purchased sensors/protocol/identity, wiring/voltage, calibrated range and freshness, loaded truck response/deceleration under grade/surface/weather, physical E-stop/watchdog, driver HMI and supervised site trials. This study makes no physical verification claim.'),('Reproduction instructions','From repo: `python -m pip install -r studies/sih26007_simulation/requirements.txt` into a separate study environment; `python -B studies/sih26007_simulation/run_all.py`; then `python -B studies/sih26007_simulation/run_all.py --verify`. See study README for production regression commands. No hardware required.'),('Artifact inventory',figure_text+'\n\nCSV/JSON/config/source/report/figure hashes: hashes.json; provenance/environment: manifest.json. Source PDFs/PPTX are retained as evidence, not edited.'),('Submission-ready conclusions','The study quantifies conditional requirements and limitations, not achieved hardware performance. Show the 3–5 m restriction, full-scale range requirement and normalized cycle result with assumptions beside each. Ready status additionally requires recorded R1 regression and visual QA gates; consult reports/QUALITY_GATE.md.')]
    executive=mdtable(['SIH Need','Simulation evidence','Primary metric','Actual result','Physical validation needed'],[
      ['3–5 m low visibility','SIM-01','Reference cap at 3 / 4 / 5 m',' / '.join(f(one('sim01_safe_speed_vs_range',parameter_set='reference',trustworthy_perception_range_m=r)['speed_kmph']) for r in [3,4,5])+' km/h','Perception/driver response/braking'],
      ['Collision risk','SIM-03','Stationary minimum clearance',f(encounters[0]['minimum_clearance_m'])+' m, own 5 m/s; 20 m detection','Geometry, brake response, moving targets'],
      ['Safe movement','SIM-02','Infeasible candidate points',str(negative)+' grid points rejected at candidate speed','Loaded vehicle envelope'],
      ['Efficient movement','SIM-08','Reference cap at 40 m',f(one('sim08_operational_continuity',parameter_set='reference',range_case_m=40,dwell_index=.25,policy='perception_concept')['speed_kmph'])+' km/h, assumed desired limit','Achieved trustworthy range'],
      ['Operational continuity','SIM-10','Available condition-epoch fraction',f(available),'Dynamic recovery and vehicle response'],
      ['Haul-cycle/productivity impact','SIM-08','Reference throughput at 40 m',f(one('sim08_operational_continuity',parameter_set='reference',range_case_m=40,dwell_index=.25,policy='perception_concept')['normalized_productivity'])+' baseline units','Actual cycle mix and downtime'],
      ['Reliability','SIM-06','Maximum live command','0 across '+str(len(fault))+' recorded steps','Physical transport/watchdog/E-stop'],
      ['Full-scale feasibility','SIM-09','Reference range at 36 km/h',f(headlines[3]['value'])+' m','HEMM sensing, road/load/grade/braking']])
    sections[0]=('Executive summary',executive+'\nAll nonzero values use declared research assumptions, not measured mine performance.\n')
    report('TARK_SIH26007_SIMULATION_REPORT','\n\n'.join(f'## {i}. {title}\n\n{body}' for i,(title,body) in enumerate(sections,1)))
    (root/'reports').mkdir(exist_ok=True)
    (root/'reports/MODEL_LINEAGE.md').write_text('# Model lineage\n\n'+lineage+'\n\n'+model+'\n',encoding='utf-8',newline='\n')


def _numeric_equal(a,b):
    try:return float(a)==float(b)
    except (ValueError,TypeError):return False
