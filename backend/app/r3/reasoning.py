"""Deterministic R3-only perception and advisory. Never calls a control API.

Intervals are conservative configured error bounds, not covariance estimates.
No use of the legacy decision, map participants, browser state or wall clock.
"""
from copy import deepcopy
from time import perf_counter_ns
from math import atan2, degrees, hypot, sqrt, tan, radians, cos
from app.r3.adapters import validate_sample
from app.r3.reasoning_models import *

ORDER={'NORMAL':0,'WARN':1,'RESTRICT':2,'UNKNOWN':3,'STOP':4}
TRANSFORM_CONVENTION='SOURCE_TO_BODY_X_FORWARD_Y_LEFT_Z_UP'

def quality_at_least(current,reference):
    if not set(reference['sources']).issubset(current['sources']) or not set(reference['peers']).issubset(current['peers']):return False
    if reference['range'] is not None and (current['range'] is None or current['range']<reference['range']):return False
    for source,purposes in reference['purposes'].items():
        if not set(purposes).issubset(current['purposes'].get(source,[])):return False
    for source,bounds in reference['bounds'].items():
        if source not in current['bounds']:return False
        if any(key not in current['bounds'][source] or current['bounds'][source][key]>value for key,value in bounds.items()):return False
    return True

def calibration(channel,observation,kind):
    bundle=channel.configurations.require(observation)
    for key in bundle.calibration_bundle.get(observation.identity.source_id,[]):
        if channel.calibrations.valid(key,kind=kind,asset_id=observation.identity.asset_id or observation.identity.serial_number,
                                      mount_revision=bundle.mounts.get(observation.identity.source_id)):
            return key,channel.calibrations.records[key]
    return None,None

def body_point(transform,point):
    return [sum(transform[i*4+j]*point[j] for j in range(3))+transform[i*4+3] for i in range(3)]

def purpose_observations(channel,now,config):
    semantics=[];usable={};excluded={}
    for source in sorted(channel.profiles):
        row=channel.readiness(source,now);o=channel.latest.get(source)
        if o is None:excluded[source]='NO_DATA';continue
        purposes=[];reason=row['fault_reason'];payload=None;kind=o.measurement.kind
        try:payload=validate_sample(channel.profiles[source].adapter,o.measurement.payload)
        except (ValueError,TypeError):reason='INVALID_MODALITY_PAYLOAD'
        if row['producing'] and row['fresh'] and payload is not None:purposes=['DISPLAY']
        q=o.qualification.uncertainty or {};bundle=channel.configurations.require(o)
        if row['qualified'] and payload is not None:
            if kind=='ti_iwr6843':
                _,cal=calibration(channel,o,'RADAR_TO_BODY')
                bound=q.get('position_m')
                if cal and cal.coordinate_frame_convention==TRANSFORM_CONVENTION and cal.residuals.get('position_bound_m') is not None and bound is not None and bound+cal.residuals['position_bound_m']<=config.position_bound_max_m:
                    purposes+=['RANGE','TRACK_ASSOCIATION','PVSOE_INPUT']
                    if q.get('radial_velocity_mps') is not None:purposes+=['RADIAL_VELOCITY']
                else:reason='GEOMETRY_OR_UNCERTAINTY_UNQUALIFIED'
            elif kind in {'uvc_rgb','lepton_purethermal'}:
                purposes+=['PVSOE_INPUT']
                if kind=='lepton_purethermal' and payload['ffc_state']!='IDLE':
                    purposes=['DISPLAY'];reason='THERMAL_FFC_UNAVAILABLE'
                elif payload.get('inference_qualification')=='CONFIGURED_RESEARCH' and payload.get('model_reference') and payload.get('detections'):
                    purposes+=['SEMANTIC_CLASSIFICATION']
            elif kind in {'lg290p','node_b'}:
                bound=payload.get('horizontal_uncertainty_m')
                if payload['fix_type'] not in {'NO_FIX','UNKNOWN'} and bound is not None:
                    purposes+=['LOCALIZATION']
                    if source=='gnss-b' and bound<=config.peer_position_bound_m:
                        corrected=payload['fix_type']=='RTK_FIXED' and payload.get('correction_age_s') is not None and payload['correction_age_s']<=config.max_correction_age_s
                        if not config.peer_requires_corrections or corrected:purposes+=['COOPERATIVE_CONTEXT']
                        else:reason='COOPERATIVE_CORRECTION_UNQUALIFIED'
                else:reason='POSITION_UNCERTAINTY_UNAVAILABLE'
            elif kind in {'bno085','esp32_encoder'}:purposes+=['EGO_MOTION']
        if len(purposes)>1:
            usable[source]=(o,payload,purposes,row)
            if reason is None:reason=None
        if len(purposes)<=1:excluded[source]=reason or 'PURPOSE_UNQUALIFIED'
        semantics.append(SemanticObservation(source_id=source,evidence_id=o.observation_id,capture_ns=o.time.estimated_capture_time,
            capture_uncertainty_ns=o.time.capture_time_uncertainty,age_bound_ns=row['age_bound_ns'],mode=o.provenance.mode,
            frame=o.measurement.sensor_frame,purposes=purposes,calibration_refs=bundle.calibration_bundle.get(source,[]),
            uncertainty=o.qualification.uncertainty,lineage=o.provenance.transformation_lineage+['R3_PURPOSE_1'],
            measurement_kind=kind,measurement={k:v for k,v in o.measurement.payload.items() if k!='temperatures_c'},
            units=o.measurement.units,exclusion_reason=reason))
    return semantics,usable,excluded

def observability(usable,config,environment):
    ranges={kind:[] for kind in config.required_hazard_classes};support=[];origins=[]
    for model in config.coverage:
        item=usable.get(model.source_id)
        if not item or 'PVSOE_INPUT' not in item[2] or model.provenance=='UNKNOWN':continue
        o,p,_,_=item
        # Coverage must span the configured local corridor, not just its centre.
        if config.corridor_half_width_m is None or model.half_angle_deg<degrees(atan2(config.corridor_half_width_m,config.corridor_near_m)):continue
        factor=1.
        if o.measurement.kind=='uvc_rgb':
            factor={'GOOD':1.,'DEGRADED':model.degraded_factor,'SEVERE':model.severe_factor,'UNKNOWN':0.}[environment.visibility]
            if environment.provenance=='UNKNOWN':factor=0.
        # Non-RGB modalities are not degraded by a generic fog heuristic.
        bound=(o.qualification.uncertainty or {}).get('position_m',0.)
        value=max(0.,model.range_m*factor-model.uncertainty_m-bound)
        for kind in model.hazard_classes:
            if kind in ranges:ranges[kind].append(value)
        support.append(model.source_id);origins.append(model.provenance)
    class_ranges={key:max(values) if values else None for key,values in ranges.items()}
    envelope=min(class_ranges.values()) if all(x is not None for x in class_ranges.values()) else None
    return ObservabilityEnvelope(forward_range_m=envelope,provenance='UNKNOWN' if envelope is None else 'CONFIGURED_RESEARCH' if 'CONFIGURED_RESEARCH' in origins else 'MEASURED',
        class_ranges_m=class_ranges,modality_support=sorted(set(support)),environment=environment,
        limiting_reason='INSUFFICIENT_OBSERVABILITY' if envelope is None else 'CONFIGURED_COVERAGE_NOT_ROAD_CLEAR')

def wheel_response(usable,channel,config):
    item=usable.get('encoders-a')
    if not item or 'EGO_MOTION' not in item[2] or config.encoder_count_semantics!='INTERVAL_DELTA' or config.wheel_slip_bound_mps is None:return None,None
    o,p,_,_=item;_,cal=calibration(channel,o,'ENCODER_GEOMETRY')
    if not cal:return None,None
    scale=cal.parameters.get('metres_per_count');bound=(o.qualification.uncertainty or {}).get('wheel_speed_mps')
    dt=(p['interval_end_ns']-p['interval_start_ns'])/1e9
    if scale is None or scale<=0 or bound is None or dt<=0 or dt>config.maximum_motion_interval_ns/1e9 or p['invalid_edges'] or p['lost_edges'] not in {None,0}:return None,None
    left=p['left_count']*scale/dt;right=p['right_count']*scale/dt
    if abs(left-right)>config.max_wheel_disagreement_mps:return None,None
    return abs((left+right)/2),bound+config.wheel_slip_bound_mps

def fixed_axes(usable,config):
    item=usable.get('imu-a')
    if not config.fixed_body_axes_research or not item or 'EGO_MOTION' not in item[2]:return False
    o,p,_,_=item;v=p['angular_velocity_rad_s'];bound=(o.qualification.uncertainty or {}).get('angular_velocity_rad_s')
    return v is not None and bound is not None and sqrt(sum(x*x for x in v))+bound<=config.maximum_angular_rate_rad_s

def relevance(point,bound,config):
    if config.corridor_half_width_m is None:return 'UNKNOWN'
    x,y,_=point;w=config.corridor_half_width_m
    if x+bound<0 or x-bound>config.corridor_far_m or abs(y)-bound>w:return 'IRRELEVANT'
    if x-bound>=0 and x+bound<=config.corridor_far_m and abs(y)+bound<=w:return 'RELEVANT'
    return 'UNKNOWN'

def track_ttc(track,config):
    result=TTC(track_id=track.track_id,input_evidence=track.evidence_ids)
    if track.lifecycle=='COASTING' or track.relative_velocity_mps is None or track.velocity_bound_mps is None:return result
    if track.relevance!='RELEVANT':return result.model_copy(update={'reason':'RELEVANCE_UNKNOWN'})
    vx,vy=track.relative_velocity_mps;u=track.velocity_bound_mps
    low=-vx-u;high=-vx+u
    if low<=0:return result.model_copy(update={'reason':'CLOSING_NOT_POSITIVE_AND_KNOWN'})
    gap=max(0.,track.position_body_m[0]-config.vehicle.margin_m);pos=track.position_bound_m
    lower=max(0.,gap-pos)/high;upper=(gap+pos)/low
    if upper>config.ttc_horizon_s:return result.model_copy(update={'reason':'RESEARCH_MOTION_HORIZON_EXCEEDED'})
    y=track.position_body_m[1]+vy*upper
    lateral_bound=pos+u*upper+0.5*config.relative_acceleration_bound_mps2*upper*upper
    if config.corridor_half_width_m is None or abs(y)+lateral_bound>config.corridor_half_width_m:
        return result.model_copy(update={'reason':'LATERAL_INTERSECTION_UNCERTAIN'})
    return result.model_copy(update={'value_s':gap/(-vx),'lower_bound_s':lower,'upper_bound_s':upper,'valid':True,'reason':'CONDITIONAL_CONSTANT_RELATIVE_MOTION'})

def image_associations(tracks,usable,channel,config):
    """Calibrated pinhole association; no triangulation or image-derived range."""
    unresolved=[]
    for source,item in usable.items():
        o,p,purposes,_=item
        if 'SEMANTIC_CLASSIFICATION' not in purposes:continue
        kind='RGB_TO_BODY' if o.measurement.kind=='uvc_rgb' else 'THERMAL_TO_BODY'
        _,extr=calibration(channel,o,kind)
        _,intr=calibration(channel,o,'RGB_INTRINSICS' if kind=='RGB_TO_BODY' else 'THERMAL_ALIGNMENT')
        if not extr or extr.coordinate_frame_convention!=TRANSFORM_CONVENTION or not intr:
            unresolved.append({'source_id':source,'evidence_id':o.observation_id,'reason':'SEMANTIC_GEOMETRY_UNRESOLVED'});continue
        params=intr.parameters
        if not all(key in params for key in ('fx','fy','cx','cy','projection_bound_px')) or params['fx']<=0 or params['fy']<=0 or params['projection_bound_px']<0:
            unresolved.append({'source_id':source,'evidence_id':o.observation_id,'reason':'SEMANTIC_GEOMETRY_UNRESOLVED'});continue
        for detection in p['detections']:
            candidates=[]
            for track in tracks:
                if track.lifecycle=='COASTING' or track.mode!=o.provenance.mode or abs(track.capture_ns-o.time.estimated_capture_time)+track.capture_uncertainty_ns+o.time.capture_time_uncertainty>config.association_time_ns:continue
                t=extr.transform;delta=[track.position_body_m[j]-t[j*4+3] for j in range(3)]
                camera=[sum(t[j*4+i]*delta[j] for j in range(3)) for i in range(3)]
                # Camera source axes explicitly use optical x-right/y-down/z-forward.
                if camera[2]<=track.position_bound_m:continue
                px=params['fx']*camera[0]/camera[2]+params['cx'];py=params['fy']*camera[1]/camera[2]+params['cy']
                error=params['projection_bound_px']+max(params['fx'],params['fy'])*track.position_bound_m/(camera[2]-track.position_bound_m)
                x1,y1,x2,y2=detection['box_xyxy_pixels']
                if not 0<=px<p['width'] or not 0<=py<p['height']:continue
                if x1-error<=px<=x2+error and y1-error<=py<=y2+error:
                    contained=x1+error<=px<=x2-error and y1+error<=py<=y2-error
                    candidates.append((track,contained))
            for track,contained in candidates:
                index=next(i for i,t in enumerate(tracks) if t.track_id==track.track_id)
                track=tracks[index];labels=list(track.classifications)
                if len(candidates)!=1 or not contained:association='POSSIBLE' if not labels else track.association
                else:
                    label=detection['label']
                    if labels and label not in labels:association='CONFLICTING'
                    else:association='ASSOCIATED'
                    if label not in labels and len(labels)<8:labels.append(label)
                tracks[index]=track.model_copy(update={'association':association,'classifications':labels,
                    'semantic_evidence_ids':sorted(set(track.semantic_evidence_ids+[o.observation_id]))[:8],
                    'contributors':sorted(set(track.contributors+[o.identity.source_id]))[:8]})
            if len(candidates)!=1 or not candidates[0][1]:
                unresolved.append({'source_id':source,'evidence_id':o.observation_id,'label':detection['label'],'reason':'SEMANTIC_GEOMETRY_UNRESOLVED'})
    return unresolved

def cooperative(usable,config):
    peer=usable.get('gnss-b');own=usable.get('gnss-a')
    if not peer or 'COOPERATIVE_CONTEXT' not in peer[2]:return []
    o,p,_,row=peer;zones=[]
    def overlaps(fix,zone):
        lat=fix['latitude_deg'];lon=fix['longitude_deg'];u=fix['horizontal_uncertainty_m']
        if lat is None or lon is None or u is None:return False
        # Conservative small-area display-context conversion, not collision range.
        dy=u/110000.;dx=u/(110000.*max(.01,cos(radians(lat))))
        return lat+dy>=zone.latitude_min and lat-dy<=zone.latitude_max and lon+dx>=zone.longitude_min and lon-dx<=zone.longitude_max
    if own and 'LOCALIZATION' in own[2] and own[0].provenance.mode==o.provenance.mode and own[1]['horizontal_uncertainty_m']<=config.peer_position_bound_m:
        for zone in config.conflict_zones:
            if overlaps(p,zone) and overlaps(own[1],zone):zones.append(zone.zone_id)
    return [{'peer_id':o.identity.node_id,'source_id':'gnss-b','evidence_id':o.observation_id,'mode':o.provenance.mode,
             'position':p,'age_bound_ns':row['age_bound_ns'],'potential_conflict':bool(zones),'zone_ids':zones,
             'relationship':'CONFIGURED_ZONE_OVERLAP' if zones else 'UNKNOWN','local_observation':False,'unequipped_target_detection':False}]

class R3Reasoner:
    def __init__(self,config:ReasoningConfig,software_fingerprint:str):
        self.config=ReasoningConfig.model_validate_json(config.model_dump_json());self.software=software_fingerprint
        self.tracks=[];self.counter=0;self.last_ids={};self.previous=None;self.recovery_count=0;self.recovery_since=None;self.epoch=None;self.recovery_quality=None;self.metrics={}
    def checkpoint(self):
        return deepcopy({'version':'TARK_R3_REASONING_CHECKPOINT_1','tracks':[x.model_dump(mode='json') for x in self.tracks],
            'counter':self.counter,'last_ids':self.last_ids,'previous':self.previous,'recovery_count':self.recovery_count,'recovery_since':self.recovery_since,'epoch':self.epoch,'recovery_quality':self.recovery_quality})
    def restore(self,value):
        value=ReasoningCheckpoint.model_validate(value).model_dump(mode='json')
        if value.get('version')!='TARK_R3_REASONING_CHECKPOINT_1' or len(value['tracks'])>self.config.max_tracks:raise ValueError('invalid reasoning checkpoint')
        self.tracks=[Track.model_validate(x) for x in value['tracks']];self.counter=value['counter'];self.last_ids=deepcopy(value['last_ids'])
        self.previous=deepcopy(value['previous']);self.recovery_count=value['recovery_count'];self.recovery_since=value['recovery_since'];self.epoch=value['epoch']
        self.recovery_quality=deepcopy(value.get('recovery_quality'))
    def _track(self,usable,channel,now):
        config=self.config;seen=set();updated=[];motion=fixed_axes(usable,config)
        for source,item in usable.items():
            o,p,purposes,_=item
            if 'RANGE' not in purposes or o.observation_id==self.last_ids.get(source):continue
            seen.add(source);_,cal=calibration(channel,o,'RADAR_TO_BODY')
            bound=o.qualification.uncertainty['position_m']+cal.residuals['position_bound_m']
            available=[t for t in self.tracks if t.source_id==source and t.mode==o.provenance.mode]
            for point in p['points'][:config.max_tracks]:
                position=body_point(cal.transform,[point['x_m'],point['y_m'],point['z_m']])
                matches=[t for t in available if hypot(position[0]-t.position_body_m[0],position[1]-t.position_body_m[1])<=config.association_gate_m+bound+t.position_bound_m]
                old=matches[0] if len(matches)==1 else None
                if old:available.remove(old)
                else:self.counter+=1
                velocity=None;vu=None;method='UNAVAILABLE'
                if old and motion:
                    dt=(o.time.estimated_capture_time-old.capture_ns)/1e9
                    time_error=(old.capture_uncertainty_ns+o.time.capture_time_uncertainty)/1e9
                    if dt>time_error and dt<=config.maximum_motion_interval_ns/1e9:
                        velocity=[(position[j]-old.position_body_m[j])/dt for j in range(2)]
                        vu=(bound+old.position_bound_m+hypot(*velocity)*time_error)/(dt-time_error)+config.relative_acceleration_bound_mps2*dt
                        vu+=hypot(*position[:2])*config.maximum_angular_rate_rad_s
                        if vu>config.max_velocity_uncertainty_mps:velocity=None;vu=None
                        else:method='TWO_POSITION_FIXED_BODY_AXES_RESEARCH'
                relevant=relevance(position,bound,config)
                if relevant=='IRRELEVANT' and velocity is not None and config.corridor_half_width_m is not None:
                    # A lateral crossing candidate must not be discarded solely
                    # because it is outside the corridor at this instant.
                    h=config.ttc_horizon_s;end=[position[j]+velocity[j]*h for j in range(2)]
                    error=bound+vu*h+0.5*config.relative_acceleration_bound_mps2*h*h
                    if (max(position[0],end[0])+error>=0 and min(position[0],end[0])-error<=config.corridor_far_m
                        and min(position[1],end[1])-error<=config.corridor_half_width_m
                        and max(position[1],end[1])+error>=-config.corridor_half_width_m):relevant='UNKNOWN'
                updated.append(Track(track_id=old.track_id if old else f'R3-T{self.counter}',lifecycle='CONFIRMED' if old else 'NEW',source_id=source,contributors=[source],
                    evidence_ids=([old.evidence_ids[-1]] if old else [])+[o.observation_id],mode=o.provenance.mode,position_body_m=position,position_bound_m=bound,
                    radial_velocity_mps=point['radial_velocity_mps'],radial_velocity_bound_mps=o.qualification.uncertainty.get('radial_velocity_mps'),
                    relative_velocity_mps=velocity,velocity_bound_mps=vu,velocity_method=method,capture_ns=o.time.estimated_capture_time,
                    capture_uncertainty_ns=o.time.capture_time_uncertainty,last_evidence_ns=o.time.estimated_capture_time,
                    age_ns=now-o.time.estimated_capture_time,relevance=relevant))
        used={t.track_id for t in updated}
        for track in self.tracks:
            if track.track_id in used:continue
            age=now-track.last_evidence_ns
            if 0<=age<=config.track_expiry_ns:
                current=usable.get(track.source_id)
                coasting=age>0 or track.source_id in seen or current is None or 'RANGE' not in current[2]
                updated.append(track.model_copy(update={'age_ns':age,'lifecycle':'COASTING' if coasting else track.lifecycle,
                    'classifications':[],'semantic_evidence_ids':[],'contributors':[track.source_id],'association':'UNRESOLVED',
                    'relative_velocity_mps':None if coasting else track.relative_velocity_mps,'velocity_bound_mps':None if coasting else track.velocity_bound_mps}))
        self.tracks=updated[:config.max_tracks]
        self.unresolved_semantics=image_associations(self.tracks,usable,channel,config)
    def step(self,channel,now,environment=None):
        start=perf_counter_ns()
        c=self.config;environment=environment or c.environment
        if self.epoch is not None and self.epoch!=channel.host_epoch:
            self.tracks=[];self.last_ids={};self.previous=None;self.recovery_count=0;self.recovery_since=None;self.recovery_quality=None
        self.epoch=channel.host_epoch
        semantics,usable,excluded=purpose_observations(channel,now,c)
        ids={x.source_id:x.evidence_id for x in semantics if x.purposes}
        new_evidence=bool(ids) and ids!=self.last_ids
        self._track(usable,channel,now)
        perception_done=perf_counter_ns()
        envelope=observability(usable,c,environment);speed,speed_bound=wheel_response(usable,channel,c)
        peers=cooperative(usable,c);ttcs=[track_ttc(t,c) for t in self.tracks]
        hazards=[];distance=envelope.forward_range_m
        reason='EVIDENCE_SUPPORTS_RESEARCH_ENVELOPE';state='NORMAL';v=c.vehicle
        stopping=None if speed is None else (speed+speed_bound)*v.response_s+(speed+speed_bound)**2/(2*v.deceleration_mps2)+v.margin_m
        cap=None if distance is None else max(0.,-v.deceleration_mps2*v.response_s+sqrt((v.deceleration_mps2*v.response_s)**2+2*v.deceleration_mps2*max(0.,distance-v.margin_m)))
        if cap is not None:cap=min(v.maximum_speed_mps,cap)
        if c.corridor_half_width_m is None:state='UNKNOWN';reason='RELEVANCE_UNKNOWN';cap=None
        elif distance is None:state='UNKNOWN';reason='INSUFFICIENT_OBSERVABILITY';cap=None
        elif distance<=v.margin_m:state='STOP';reason='NO_POSITIVE_OPERATING_ENVELOPE';cap=0.
        elif speed is None:state='UNKNOWN';reason='MOTION_UNKNOWN';cap=None
        elif cap<v.maximum_speed_mps or speed+speed_bound>cap:state='RESTRICT';reason='FORWARD_OBSERVABILITY_BELOW_REQUIRED_RANGE'
        elif excluded or environment.visibility!='GOOD':state='WARN';reason='DEGRADED_EVIDENCE'
        for track,ttc in zip(self.tracks,ttcs):
            if track.relevance=='IRRELEVANT':continue
            gap=max(0.,track.position_body_m[0]-track.position_bound_m)
            hazards.append({'track_id':track.track_id,'range_lower_bound_m':gap,'relevance':track.relevance,'lifecycle':track.lifecycle,
                            'evidence_ids':track.evidence_ids,'ttc_valid':ttc.valid,'association':track.association})
            if track.lifecycle!='COASTING' and track.relevance=='RELEVANT' and gap<=v.margin_m:
                state='STOP';reason='CRITICAL_LOCAL_DISTANCE';cap=0.;continue
            if state=='STOP':continue
            if track.lifecycle=='COASTING' or track.relevance=='UNKNOWN' or track.association=='CONFLICTING':
                state='UNKNOWN';reason='SOURCE_CONFLICT' if track.association=='CONFLICTING' else 'RELEVANCE_UNKNOWN' if track.relevance=='UNKNOWN' else 'TRACK_EVIDENCE_LOST';cap=None
            elif track.relative_velocity_mps is None:
                state='UNKNOWN';reason='MOTION_UNKNOWN';cap=None
            elif cap is not None:
                distance=min(distance,gap)
                target_cap=max(0.,-v.deceleration_mps2*v.response_s+sqrt((v.deceleration_mps2*v.response_s)**2+2*v.deceleration_mps2*max(0.,gap-v.margin_m)))
                cap=min(cap,target_cap)
                if stopping is not None and gap<=stopping or ttc.valid and ttc.lower_bound_s<=v.response_s:
                    state='STOP';reason='STOPPING_REQUIREMENT_NOT_MET';cap=0.
                elif ORDER[state]<ORDER['RESTRICT']:state='RESTRICT';reason='RELEVANT_LOCAL_HAZARD'
        if any(p['potential_conflict'] for p in peers) and cap is not None:
            cap=min(cap,c.peer_restrict_speed_mps)
            if ORDER[state]<=ORDER['RESTRICT']:state='RESTRICT';reason='COOPERATIVE_CONFLICT'
        # Incomplete processing and mixed experimental domains cannot justify
        # an operating envelope, even if the retained subset looks favourable.
        if state!='STOP' and self.unresolved_semantics:
            state='UNKNOWN';cap=None;reason='SEMANTIC_GEOMETRY_UNRESOLVED'
        overflow=sum(len(p.get('points',[])) for _,p,purposes,_ in usable.values() if 'RANGE' in purposes)>c.max_tracks
        mixed=len({o.provenance.mode for o,_,_,_ in usable.values()})>1
        if state!='STOP' and (overflow or mixed):
            state='UNKNOWN';cap=None;reason='TRACK_CAPACITY_EXCEEDED' if overflow else 'SOURCE_MODE_CONFLICT'
        quality={'sources':sorted(usable),'range':envelope.forward_range_m,'bounds':{s:(o.qualification.uncertainty or {}) for s,(o,_,_,_) in usable.items()},
                 'peers':[p['peer_id'] for p in peers],'purposes':{source:item[2] for source,item in usable.items()}}
        previous=self.previous
        degradation=False
        if previous:
            old=previous['quality']
            degradation=not quality_at_least(quality,old)
            if degradation and self.recovery_quality is None:self.recovery_quality=deepcopy(old)
            recovered_quality=self.recovery_quality is None or quality_at_least(quality,self.recovery_quality)
            improvement=ORDER[state]<ORDER[previous['state']] or cap is not None and cap>(previous['cap'] or 0.)
            if degradation or not recovered_quality or not new_evidence:self.recovery_count=0;self.recovery_since=None
            elif improvement:
                self.recovery_count+=1
                if self.recovery_since is None:self.recovery_since=now
            else:self.recovery_count=0;self.recovery_since=None
            recover=recovered_quality and not degradation and self.recovery_count>=c.recovery_frames and self.recovery_since is not None and now-self.recovery_since>=c.recovery_dwell_ns
            if recover:self.recovery_quality=None
            if improvement and not recover:
                state=previous['state'];cap=previous['cap'];reason='EVIDENCE_DEGRADED_HOLD' if degradation else 'RECOVERY_PENDING'
            if previous['quality']['peers'] and not peers and state!='STOP':state='UNKNOWN';cap=None;reason='COOPERATIVE_EVIDENCE_UNAVAILABLE'
        elif state!='STOP':
            state='UNKNOWN';cap=None;reason='RECOVERY_PENDING'
        self.last_ids=ids
        self.previous={'state':state,'cap':cap,'quality':deepcopy(quality)}
        deadlines=[now+min(p.max_age_ns for p in channel.profiles.values())]
        for source,(o,_,_,row) in usable.items():
            if o.time.estimated_capture_time is not None:deadlines.append(o.time.estimated_capture_time+channel.profiles[source].max_age_ns-o.time.capture_time_uncertainty)
            if row['clock_valid_until_ns'] is not None:deadlines.append(row['clock_valid_until_ns'])
        modes={o.provenance.mode for o in channel.latest.values()};mode=next(iter(modes)) if len(modes)==1 else 'MIXED' if modes else 'UNAVAILABLE'
        refs=sorted({ref for item in semantics for ref in item.calibration_refs})
        action={'NORMAL':'PROCEED_WITHIN_RESEARCH_ENVELOPE','WARN':'PROCEED_WITH_CAUTION','RESTRICT':'REDUCE_SPEED','UNKNOWN':'HOLD_INSUFFICIENT_EVIDENCE','STOP':'STOP_ADVISORY'}[state]
        result=R3Decision(timestamp_ns=now,valid_until_ns=max(now,min(deadlines)),state=state,advisory=action,advised_speed_mps=cap,
            vehicle_profile=v,ego_speed_mps=speed,ego_speed_bound_mps=speed_bound,stopping_requirement_m=stopping,observability=envelope,
            semantic_observations=semantics,tracks=self.tracks,ttc=ttcs,hazards=hazards,cooperative_context=peers,limiting_reason=reason,
            qualified_sources=sorted(usable),excluded_sources=excluded,configuration_hash=c.content_hash,configuration_id=c.config_id,
            calibration_refs=refs,software_fingerprint=self.software,source_mode=mode,
            explanation={'schema_version':'TARK_R3_WHY_1','primary_reason':reason,'action':action,'supporting_evidence':[s.evidence_id for s in semantics if len(s.purposes)>1],
                'excluded':excluded,'track_ids':[t.track_id for t in self.tracks],'peer_ids':[p['peer_id'] for p in peers],
                'unresolved_semantics':self.unresolved_semantics[:64],
                'required_range_m':stopping,'qualified_range_m':envelope.forward_range_m,'research_parameters':True,
                'scope':'R3_ADVISORY_NOT_LEGACY_DECISION','motion_authority':False}).model_dump(mode='json')
        self.metrics={'perception_latency_ns':perception_done-start,'reasoning_latency_ns':perf_counter_ns()-perception_done,
                      'track_count':len(self.tracks),'queue_depth':0,'measurement_host':'DEVELOPMENT_PC_NOT_PI5'}
        return result
