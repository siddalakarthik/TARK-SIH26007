"""Figures read exported CSV, never private generator arrays."""
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .experiments import read_csv


def render(root):
    plt.rcParams.update({'font.size':13,'axes.titlesize':19,'axes.labelsize':14,
                         'figure.figsize':(12.8,7.2),'axes.spines.top':False,'axes.spines.right':False,
                         'svg.hashsalt':'tark-sih26007','savefig.dpi':170})
    out=root/'figures';out.mkdir(exist_ok=True); inventory=[]
    def data(name): return read_csv(root/'tables'/f'{name}.csv')
    def nums(rows,key): return [float(r[key]) for r in rows]
    def start(title,x,y):
        fig,ax=plt.subplots();ax.set(title=title,xlabel=x,ylabel=y);ax.grid(alpha=.18)
        return fig,ax
    def finish(fig,name,source,desc):
        fig.subplots_adjust(left=.25 if name=='sim07_parameter_sensitivity' else .11,right=.95,top=.86,bottom=.20)
        fig.text(.11,.065,'ANALYTICAL STUDY • Assumed sensitivity inputs • Physical validation pending',fontsize=11)
        fig.text(.11,.035,'Source table: '+source+'.csv',fontsize=9,color='#444444')
        for ext in ['png','svg']:
            fig.savefig(out/f'{name}.{ext}',metadata={'Creator':'TARK research study','Date':None} if ext=='svg' else {'Software':'TARK research study'})
        plt.close(fig)
        inventory.append(dict(figure=name,source_table=f'tables/{source}.csv',description=desc,
                              source_sha256=hashlib.sha256((root/'tables'/f'{source}.csv').read_bytes()).hexdigest()))
    def curves(name,title,source,x,y,xlabel,ylabel,groups='parameter_set',selector=None):
        rows=data(source); rows=[r for r in rows if selector is None or selector(r)]
        fig,ax=start(title,xlabel,ylabel)
        for group in dict.fromkeys(r[groups] for r in rows):
            s=[r for r in rows if r[groups]==group];ax.plot(nums(s,x),nums(s,y),label=group,linewidth=2)
        ax.legend(title={'age_s':'Evidence age (s)','uncertainty_m':'Reserve (m)'}.get(groups));finish(fig,name,source,title)
    curves('sim01_safe_speed_vs_range','FIG-01 | Maximum model-compatible speed','sim01_safe_speed_vs_range','trustworthy_perception_range_m','speed_kmph','Trustworthy perception range (m)','Analytical speed cap (km/h)')
    curves('sim01_required_range_vs_speed','FIG-02 | Required perception distance','sim01_required_range_vs_speed','speed_kmph','required_perception_range_m','Candidate speed (km/h)','Required trustworthy range (m)')
    source='sim01_safe_speed_vs_range';rows=data(source)
    fig,ax=start('FIG-04 | Visual-distance-constrained reference','Visual reference distance (m)','Analytical speed cap (km/h)')
    for ps in ['favourable','reference','adverse']:
        s=[r for r in rows if r['parameter_set']==ps and r['visibility_m']]
        ax.plot(nums(s,'visibility_m'),nums(s,'speed_kmph'),'o-',label=ps)
    ax.set_xticks([3,4,5]);ax.set_ylim(bottom=0);ax.legend();finish(fig,'sim01_visual_reference',source,'3, 4 and 5 metre visual-only references; not fog sensor performance')
    fig,ax=start('Stopping requirement components at the reference speed cap','Trustworthy range (m)','Distance (m)')
    s=[r for r in rows if r['parameter_set']=='reference'];x=nums(s,'trustworthy_perception_range_m')
    ax.stackplot(x,nums(s,'response_distance_m'),nums(s,'braking_distance_m'),nums(s,'margin_m'),nums(s,'uncertainty_m'),labels=['Response','Braking','Fixed margin','Perception reserve'],alpha=.85);ax.legend(loc='upper left')
    finish(fig,'sim01_stopping_components',source,'Zero cap does not imply feasibility below combined reserves')
    source='sim02_operating_envelope';s=[r for r in data(source) if r['parameter_set']=='reference']
    xs=sorted(set(nums(s,'speed_kmph')));ys=sorted(set(nums(s,'trustworthy_perception_range_m')))
    z=np.array(nums(s,'safety_margin_m')).reshape(len(ys),len(xs));fig,ax=start('FIG-03 | Model margin, reference assumptions','Candidate speed (km/h)','Trustworthy range (m)')
    scale=max(abs(z.min()),abs(z.max()));m=ax.pcolormesh(xs,ys,z,cmap='RdBu',vmin=-scale,vmax=scale,shading='auto');ax.contour(xs,ys,z,levels=[0],colors='black',linewidths=2);fig.colorbar(m,ax=ax,label='Model margin (m)')
    finish(fig,'sim02_safety_efficiency_map',source,'Black contour is zero model margin, not certified safety')
    curves('sim02_speed_cap_curves','Model speed bounds from declared parameter sets','sim01_safe_speed_vs_range','trustworthy_perception_range_m','speed_kmph','Trustworthy range (m)','Speed cap (km/h)')
    source='sim03_encounters';rows=data(source);s=[r for r in rows if r['parameter_set']=='reference' and float(r['initial_separation_m'])==40 and float(r['trustworthy_perception_range_m'])==20]
    fig,ax=start('FIG-05 | Encounter clearance through own-stop + 5 s','Own initial speed (km/h)','Minimum point-clearance (m)')
    for kind in ['stationary','slower_lead','oncoming']:
        q=[r for r in s if r['encounter_type']==kind];ax.plot(nums(q,'speed_kmph'),nums(q,'minimum_clearance_m'),'o-',label=kind)
    ax.axhline(0,color='black');ax.legend();finish(fig,'sim03_clearance_map',source,'Initial separation 40 m; detect at 20 m; target never brakes; negative is model overlap')
    curves('sim03_closing_scenarios','Initial closing rate at 40 m separation',source,'speed_kmph','initial_closing_rate_mps','Own speed (km/h)','Closing speed (m/s)','encounter_type',lambda r:r['parameter_set']=='reference' and float(r['initial_separation_m'])==40 and float(r['trustworthy_perception_range_m'])==20)
    curves('sim03_required_detection_range','Required range for the finite encounter horizon',source,'speed_kmph','required_detection_range_m','Own speed (km/h)','Required detection distance (m)','encounter_type',lambda r:r['parameter_set']=='reference' and float(r['initial_separation_m'])==40 and float(r['trustworthy_perception_range_m'])==20)
    for source,name,title in [('sim04_fog_transition','sim04_fog_timeline','FIG-06 | Independent visual and perception conditions'),('sim10_integrated','sim10_integrated','FIG-12 | Integrated analytical demonstration')]:
        rows=data(source);fig,axes=plt.subplots(3,1,sharex=True,figsize=(12.8,9));x=nums(rows,'epoch_start_s')
        for key,label in [('visibility_m','Visual visibility'),('trustworthy_perception_range_m','Trustworthy model range')]:axes[0].step(x,nums(rows,key),where='post',label=label)
        if source=='sim10_integrated':axes[0].step(x,nums(rows,'separation_m'),where='post',label='Scenario separation (not trajectory)')
        axes[0].set(title=title,ylabel='Distance (m)');axes[0].legend(fontsize=10)
        axes[1].step(x,nums(rows,'speed_kmph'),where='post',label='Analytical cap');axes[1].set_ylabel('Cap (km/h)');axes[1].legend()
        axes[2].step(x,nums(rows,'safety_margin_m'),where='post',label='Model margin');axes[2].axhline(0,color='black');axes[2].set(ylabel='Margin (m)',xlabel='Synthetic epoch start (s)');axes[2].legend()
        finish(fig,name,source,'Piecewise condition assessments, not an instantaneous vehicle speed trajectory')
    source='sim04_fog_transition';rows=data(source);fig,ax=start('Envelope contraction and recovery','Synthetic epoch start (s)','Analytical cap (km/h)')
    ax.step(nums(rows,'epoch_start_s'),nums(rows,'speed_kmph'),where='post')
    finish(fig,'sim04_envelope_contraction',source,'Condition caps, not instantaneous physical braking')
    source='sim10_integrated';rows=data(source);fig,ax=start('Integrated scenario | Evidence and communication health','Synthetic epoch start (s)','Boolean state (separated rows)')
    for offset,key,label in [(0,'evidence_available','Evidence available'),(2,'link_available','Link available'),(4,'halted','Analytical halt')]:
        ax.step(nums(rows,'epoch_start_s'),[offset+int(r[key]=='True') for r in rows],where='post',label=label)
    ax.set_yticks([0,1,2,3,4,5],['No','Yes','No','Yes','No','Yes']);ax.legend(loc='center left',bbox_to_anchor=(.01,.5),fontsize=10)
    finish(fig,'sim10_health_timeline',source,'Synthetic condition flags, not a replacement protocol supervisor')
    source='sim05_perception_degradation'
    curves('sim05_uncertainty_sensitivity','FIG-07a | Uncertainty reduces modeled capability',source,'trustworthy_perception_range_m','speed_kmph','Trustworthy range (m)','Speed cap (km/h)',groups='uncertainty_m',selector=lambda r:r['report_kind']=='valid_target' and float(r['age_s'])==0)
    curves('sim05_range_degradation','Range and age constraints',source,'trustworthy_perception_range_m','speed_kmph','Trustworthy range (m)','Speed cap (km/h)',groups='age_s',selector=lambda r:r['report_kind']=='valid_target' and float(r['uncertainty_m'])==1)
    source='sim06_fault_story';rows=[r for r in data(source) if r['source_scenario']=='EV-20']
    fig,axes=plt.subplots(2,1,sharex=True,figsize=(12.8,8));x=nums(rows,'step')
    axes[0].step(x,[int(r['receiver_active']=='True') for r in rows],where='post',label='Receiver logical authority');axes[0].step(x,nums(rows,'live_permitted_speed_mps'),where='post',label='Live speed command = 0');axes[0].set(title='FIG-08 | Verified R1 communication story',ylabel='Logical flag / zero command');axes[0].legend()
    axes[1].plot(x,nums(rows,'analytical_cap_mps'),'o-',label='Separate analytical overlay');axes[1].set(xlabel='Ordered step / controlled time (s); equal times remain distinct',ylabel='Research cap (m/s)');axes[1].set_xticks(x[::2],[f'{int(x[i])} / {rows[i]["controlled_time_s"]}' for i in range(0,len(x),2)]);axes[1].legend();finish(fig,'sim06_fault_timeline',source,'EV-20 projection; all nine selected fault traces are available in CSV')
    source='sim07_samples';rows=data(source);fig,ax=start('FIG-07b | Engineering uncertainty samples','Model margin (m)','Sample count')
    ax.hist(nums(rows,'safety_margin_m'),bins=50,color='#244d78');ax.axvline(0,color='#b02a2a',label='Zero margin');ax.legend();finish(fig,'sim07_margin_distribution',source,'Uniform engineering samples, not accident probability')
    source='sim07_sensitivity';rows=data(source);fig,ax=start('Sensitivity within the declared uniform bounds','Marginal Pearson correlation with margin','Parameter')
    ax.barh([r['parameter'] for r in rows],nums(rows,'pearson_correlation'),color='#244d78');ax.set_xlim(-1,1);finish(fig,'sim07_parameter_sensitivity',source,'Rank depends on assumed ranges; not a universal sensitivity ranking')
    source='sim07_uncertainty_samples_summary';rows=data(source);fig,axes=plt.subplots(2,1,sharex=True,figsize=(12.8,8));x=nums(rows,'samples')
    for k in ['p05_m','median_m','p95_m']:axes[0].plot(x,nums(rows,k),'o-',label=k)
    axes[0].set(title='Sample-size stability',ylabel='Margin percentile (m)');axes[0].legend()
    axes[1].plot(x,nums(rows,'negative_margin_fraction'),'o-');axes[1].set(xlabel='Prefix sample count',ylabel='Negative-margin fraction');axes[1].set_ylim(0,1);finish(fig,'sim07_convergence',source,'Compare final two prefixes using predeclared tolerances')
    for name,key,title,ylabel in [('sim08_cycle_time_comparison','normalized_cycle_time','FIG-09 | Normalized cycle time','Cycle-time index'),('sim08_productivity_retention','normalized_productivity','FIG-10 | Normalized throughput retention','Throughput index'),('sim08_halt_fraction','halt_fraction','Modeled halt fraction','Fraction of cycle')]:
        curves(name,title,'sim08_operational_continuity','range_case_m',key,'Perception scenario range (m)',ylabel,groups='policy',selector=lambda r:r['parameter_set']=='reference' and float(r['dwell_index'])==.25)
    curves('sim09_required_perception_range','Full-scale requirement, not a sensor capability','sim09_fullscale_requirements','speed_kmph','required_perception_range_m','Candidate speed (km/h)','Required range (m)',selector=lambda r:float(r['trustworthy_perception_range_m'])==40)
    source='sim09_fullscale_requirements';rows=[r for r in data(source) if r['parameter_set']=='reference'];fig,ax=start('FIG-11 | Full-scale response-delay requirement','Candidate speed (km/h)','Available trustworthy range (m)')
    valid=[r for r in rows if r['max_response_delay_s']];m=ax.scatter(nums(valid,'speed_kmph'),nums(valid,'trustworthy_perception_range_m'),c=nums(valid,'max_response_delay_s'),cmap='viridis',s=140);fig.colorbar(m,ax=ax,label='Maximum response delay (s)')
    bad=[r for r in rows if not r['max_response_delay_s']];ax.scatter(nums(bad,'speed_kmph'),nums(bad,'trustworthy_perception_range_m'),marker='x',color='#a12626',label='No feasible nonnegative delay');ax.legend(fontsize=10);finish(fig,'sim09_requirement_feasibility_map',source,'No prototype detection-range performance claim')
    source='safety_efficiency_trade_space';rows=data(source);fig,ax=start('FIG-13 | Modelled safety-efficiency trade space','Analytical speed (km/h)','Nonnegative model margin (m)')
    for r in sorted(set(nums(rows,'trustworthy_perception_range_m'))):
        s=[q for q in rows if float(q['trustworthy_perception_range_m'])==r];ax.plot(nums(s,'speed_kmph'),nums(s,'safety_margin_m'),label=f'{r:g} m range')
    ax.set_ylim(bottom=0);ax.legend();finish(fig,'safety_efficiency_trade_space',source,'Within each fixed resource case the feasible speed/margin curve is non-dominated')
    (root/'results/figure_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8',newline='\n')
    return inventory
