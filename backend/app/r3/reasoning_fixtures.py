"""Deterministic synthetic inputs through production admission/qualification.

Not real captures, measured calibrations, surveyed zones or trained-model output.
Used by tests and an explicit CLI demonstration, never implicitly by real mode.
"""
from pathlib import Path
from app.r3.contracts import *
from app.r3.registry import *
from app.r3.evidence import EvidenceChannel
from app.r3.sources import ObservationAdapter
from app.r3.reasoning_models import *
from app.r3.reasoning import TRANSFORM_CONVENTION, R3Reasoner

ROOT=Path(__file__).parents[3]
IDENTITY_MATRIX=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
# Explicit synthetic TI axes -> x-forward/y-left/z-up; not a physical calibration.
TI_MATRIX=[0.,1.,0.,0.,-1.,0.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
CAMERA_MATRIX=[0.,0.,1.,0.,-1.,0.,0.,0.,0.,-1.,0.,0.,0.,0.,0.,1.]

def demo_config():
    return ReasoningConfig(config_id='SYNTHETIC_RESEARCH_CART_1',corridor_half_width_m=1.5,
        encoder_count_semantics='INTERVAL_DELTA',wheel_slip_bound_mps=0.05,
        fixed_body_axes_research=True,maximum_angular_rate_rad_s=.001,relative_acceleration_bound_mps2=.01,
        max_velocity_uncertainty_mps=.5,environment=Environment(visibility='GOOD',provenance='CONFIGURED_RESEARCH',evidence_reference='SYNTHETIC_ENVIRONMENT'),
        coverage=[CoverageModel(source_id=s,hazard_classes=['STATIC_OBSTACLE','VEHICLE','PERSON'],range_m=r,uncertainty_m=.2,half_angle_deg=65.,
            provenance='CONFIGURED_RESEARCH',evidence_reference='SYNTHETIC_COVERAGE_NOT_DETECTION_VALIDATION') for s,r in [('radar-a',3.),('rgb-a',15.)]],
        conflict_zones=[ConflictZone(zone_id='SYNTHETIC_BLIND_CURVE',latitude_min=16.999,latitude_max=17.002,longitude_min=77.999,longitude_max=78.002,
            provenance='CONFIGURED_RESEARCH',evidence_reference='SYNTHETIC_NOT_SURVEYED')])

class ReasoningFixture:
    def __init__(self,config=None,software='FIXTURE_SOFTWARE'):
        profile=HardwareProfile.model_validate_json((ROOT/'config/r3_pi5_advisory.json').read_text())
        self.channel=EvidenceChannel(profile,'fixture-host');self.config=config or demo_config();self.engine=R3Reasoner(self.config,software)
        self.now=1_000_000_000;self.sequence=0;self.identities={};calrefs={};mounts={}
        for p in profile.sources:
            asset='synthetic-'+p.source_id
            identity=Identity(source_id=p.source_id,node_id=p.node_id,device_class=p.device_class,manufacturer=p.manufacturer,part_number=p.part_number,
                asset_id=asset,driver_version='SYNTHETIC_REASONING_1',boot_id='fixture-boot',session_id='fixture-session')
            self.identities[p.source_id]=identity;self.channel.begin_source(identity,'SIMULATION')
            kinds=list(p.required_calibrations)
            if p.source_id=='rgb-a' and 'RGB_INTRINSICS' not in kinds:kinds.append('RGB_INTRINSICS')
            if p.source_id=='thermal-a' and 'THERMAL_ALIGNMENT' not in kinds:kinds.append('THERMAL_ALIGNMENT')
            refs=[]
            for kind in kinds:
                matrix=TI_MATRIX if kind=='RADAR_TO_BODY' else CAMERA_MATRIX if kind in {'RGB_TO_BODY','THERMAL_TO_BODY'} else IDENTITY_MATRIX
                params={'metres_per_count':.001} if kind=='ENCODER_GEOMETRY' else {'fx':100.,'fy':100.,'cx':320.,'cy':240.,'projection_bound_px':1.}
                if kind=='THERMAL_ALIGNMENT':params.update(cx=80.,cy=60.)
                record=Calibration(calibration_id=p.source_id+'-'+kind,version='synthetic-1',kind=kind,asset_ids=[asset],mount_revision='SYNTHETIC_MOUNT',
                    method='SYNTHETIC_NOT_MEASURED',date='2026-10-04',operator='SOFTWARE_FIXTURE',transform=matrix if kind.endswith('_TO_BODY') else None,
                    parameters=params,units='SI',coordinate_frame_convention=TRANSFORM_CONVENTION,residuals={'position_bound_m':.005},
                    validity_domain='SYNTHETIC_TEST_ONLY',software_version=software,artifacts=['SYNTHETIC_CALIBRATION'])
                self.channel.calibrations.register(record);refs.append(record.calibration_id+':'+record.version)
            calrefs[p.source_id]=refs;mounts[p.source_id]='SYNTHETIC_MOUNT'
            self.channel.clocks.register(ClockMapping(mapping_id='clock-'+p.source_id,source_id=p.source_id,clock_domain='SYNTHETIC_HOST',source_boot_id='fixture-boot',
                host_epoch='fixture-host',native_anchor=0,host_anchor_ns=0,ns_per_tick=1.,offset_uncertainty_ns=1000,drift_ppm=0.,drift_uncertainty_ppm=0.,
                last_synchronization_ns=0,valid_until_ns=10**15,max_drift_ppm=1.,evidence_reference='SYNTHETIC_CLOCK_NOT_SYNC_PROOF',status='TIME_VALID'))
        self.bundle=ConfigurationBundle(bundle_id='SYNTHETIC_REASONING_BUNDLE',hardware_profile=profile.profile_id,driver_profile='FIXTURE',sensor_modes={},radar_profile='SYNTHETIC_CARTESIAN',
            camera_mode='SYNTHETIC',thermal_mode='SYNTHETIC',gnss_configuration='SYNTHETIC',network_profile='SYNTHETIC_NOT_RADIO',calibration_bundle=calrefs,mounts=mounts,
            ai_model='SYNTHETIC_DETECTIONS',pvsoe_parameter_set=self.config.content_hash,vehicle_parameters={},software_version=software)
        self.channel.configurations.register(self.bundle)
    def feed(self,*,points=(),omit=(),speed=.5,uncertainty=.01,peer=False,peer_uncertainty=.2,correction_age=0.,rgb_label=None,thermal_label=None,rgb_box=None,fail=(),environment=None):
        self.now+=100_000_000;self.sequence+=1
        payloads={
          'radar-a':{'firmware_profile':'SYNTHETIC_CARTESIAN','frame_number':self.sequence,'points':[{'x_m':-y,'y_m':x,'z_m':0.,'radial_velocity_mps':v} for x,y,v in points]},
          'rgb-a':{'frame_id':f'image-{self.sequence}','width':640,'height':480,'pixel_format':'RGB','media_reference':'SYNTHETIC_NO_IMAGE','sha256':'0'*64},
          'thermal-a':{'frame_id':f'thermal-{self.sequence}','width':160,'height':120,'pixel_format':'Y16','media_reference':'SYNTHETIC_NO_IMAGE','sha256':'0'*64,'ffc_state':'IDLE','radiometry':'UNAVAILABLE'},
          'imu-a':{'report_id':2,'angular_velocity_rad_s':[0.,0.,0.]},
          'encoders-a':{'left_count':round(speed*100),'right_count':round(speed*100),'interval_start_ns':self.now-100_000_000,'interval_end_ns':self.now,'invalid_edges':0,'lost_edges':0},
          'gnss-a':{'fix_type':'RTK_FIXED','latitude_deg':17.,'longitude_deg':78.,'horizontal_uncertainty_m':.2,'correction_age_s':0.},
          'gnss-b':{'fix_type':'RTK_FIXED','latitude_deg':17.001 if peer else 18.,'longitude_deg':78.001 if peer else 79.,'horizontal_uncertainty_m':peer_uncertainty,'correction_age_s':correction_age},
          'gnss-base':{'fix_type':'STANDALONE','latitude_deg':17.,'longitude_deg':78.,'horizontal_uncertainty_m':1.}}
        for source,label in [('rgb-a',rgb_label),('thermal-a',thermal_label)]:
            if label:
                p=payloads[source];p.update(detections=[{'label':label,'box_xyxy_pixels':[0.,0.,float(p['width']),float(p['height'])],'confidence':.9}],
                    inference_qualification='CONFIGURED_RESEARCH',model_reference='SYNTHETIC_MODEL_NOT_VALIDATED')
                if source=='rgb-a' and rgb_box is not None:p['detections'][0]['box_xyxy_pixels']=rgb_box
        for source,payload in payloads.items():
            if source in omit:continue
            p=self.channel.profiles[source]
            uncertainty_fields={'position_m':uncertainty,'radial_velocity_mps':.05,'wheel_speed_mps':.02,'angular_velocity_rad_s':.0001}
            o=Observation(observation_id=f'{source}-{self.sequence}',identity=self.identities[source],
                time=ObservationTime(native_timestamp=self.now,native_timestamp_units='ns',native_clock_domain='SYNTHETIC_HOST',host_epoch='fixture-host',
                    host_monotonic_arrival=self.now,estimated_capture_time=self.now,capture_time_uncertainty=1000,clock_mapping_version='clock-'+source,publication_time=self.now,measurement_age=0),
                integrity=Integrity(sequence_number=self.sequence,source_counter=self.sequence,payload_length=len(__import__('json').dumps(payload)),check_result='PASS'),
                measurement=Measurement(kind=p.adapter,payload=payload,units={'payload':'SI_EXPLICIT_FIELDS'},sensor_frame='SYNTHETIC_SOURCE_AXES',mode_profile='SYNTHETIC',configuration_hash=self.bundle.content_hash),
                qualification=Qualification(connection_state='CONNECTED',production_state='PRODUCING',health_state='FAILED' if source in fail else 'ONLINE',plausibility_state='PLAUSIBLE',
                    uncertainty=uncertainty_fields,uncertainty_origin='CONFIGURED_RESEARCH_NOT_MEASURED'),
                provenance=Provenance(mode='SIMULATION',evidence_origin='SYNTHETIC_FIXTURE',software_version=self.bundle.software_version,configuration_bundle_id=self.bundle.bundle_id,
                    transformation_lineage=['SYNTHETIC_REASONING_SCENARIO']))
            ObservationAdapter(self.channel,source).ingest(o,self.now)
        return self.engine.step(self.channel,self.now,environment)

    def metadata(self):
        return {'version':'TARK_R3_PROVENANCE_1','software_fingerprint':self.engine.software,
                'profile':self.channel.profile.model_dump(mode='json'),'profile_hash':digest(self.channel.profile.model_dump(mode='json')),
                'configuration':self.bundle.model_dump(mode='json'),'configuration_hash':self.bundle.content_hash,
                'reasoning':{'configuration':self.config.model_dump(mode='json'),'configuration_hash':self.config.content_hash,'checkpoint':self.engine.checkpoint()}}

    def record(self,decision,environment=None):
        data=self.channel.record();data['reasoning_environment']=(environment or self.config.environment).model_dump(mode='json')
        view=self.channel.snapshot(self.now);view['advisory']=decision
        return {'kind':'OBSERVATION_TICK_V2','sequence':self.sequence,'timestamp_ns':self.now,'payload':{'r3_readiness':view,'r3_evidence':data}}

def novelty_demo():
    fixture=ReasoningFixture();rows=[]
    stages=[('HEALTHY',10,{}),('RGB_FOG',3,{'environment':Environment(visibility='SEVERE',provenance='CONFIGURED_RESEARCH',evidence_reference='SYNTHETIC_FOG')}),
            ('GEOMETRY_LOSS',8,{'omit':('radar-a','rgb-a')}),('RECOVERY',12,{})]
    for stage,count,kwargs in stages:
        for _ in range(count):
            d=fixture.feed(**kwargs);rows.append({'stage':stage,'time':d['timestamp_ns'],'state':d['state'],'speed':d['advised_speed_mps'],'range':d['observability']['forward_range_m'],'reason':d['limiting_reason']})
    peer=ReasoningFixture();blind=[]
    for stage,count,kwargs in [('NO_CONFLICT',10,{}),('PEER_APPROACH',3,{'peer':True}),('PEER_STALE',15,{'omit':('gnss-b',)})]:
        for _ in range(count):
            d=peer.feed(**kwargs);blind.append({'stage':stage,'time':d['timestamp_ns'],'state':d['state'],'reason':d['limiting_reason'],'peers':d['cooperative_context']})
    return {'notice':'SYNTHETIC RESEARCH ONLY; NO HARDWARE VERIFIED','novelty':rows,'blind_curve':blind}
