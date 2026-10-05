"""Additive R3 integration owned by the existing system lifecycle.

The legacy decision engine stays authoritative for its legacy input scope. New
R3 observations are qualified and recorded, not covertly injected into that scope.
"""
from __future__ import annotations
import hashlib
import uuid
import os
import json
import time
from pathlib import Path
from app.r3.contracts import HardwareProfile, digest
from app.r3.registry import ConfigurationBundle, Calibration
from app.r3.evidence import EvidenceChannel
from app.r3.experiments import ExperimentStore
from app.r3.sources import FixtureSources, ObservationAdapter
from app.r3.inference import UnavailableInferenceProvider
from app.r3.reasoning_models import ReasoningConfig
from app.r3.reasoning import R3Reasoner

ROOT=Path(__file__).parents[3]

def r3_software_fingerprint():
    h=hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob('*.py')):
        h.update(path.name.encode()); h.update(path.read_bytes().replace(b'\r\n',b'\n'))
    return h.hexdigest()

class R3Runtime:
    def __init__(self,settings,database_path:Path,*,profile_path:Path|None=None,active_profile='LEGACY_SMALL_SCALE'):
        if active_profile not in {'LEGACY_SMALL_SCALE','R3_PI5_ADVISORY'}: raise ValueError('unknown hardware profile')
        self.active_profile=active_profile
        self.profile=HardwareProfile.model_validate_json((profile_path or ROOT/'config/r3_pi5_advisory.json').read_text(encoding='utf-8'))
        self.channel=EvidenceChannel(self.profile,uuid.uuid4().hex)
        self.bundle=ConfigurationBundle(bundle_id='r3-uncommissioned-'+settings.configuration_hash[:80],hardware_profile=self.profile.profile_id,
            driver_profile='R3_OBSERVATION_BOUNDARIES_V1',sensor_modes={},radar_profile=None,camera_mode=None,thermal_mode=None,gnss_configuration=None,
            network_profile='ORDINARY_LOCAL_WIFI_UNMEASURED',calibration_bundle={},mounts={},ai_model=None,
            pvsoe_parameter_set=settings.configuration_hash,vehicle_parameters={},software_version=r3_software_fingerprint())
        bundle_path=os.getenv('TARK_R3_BUNDLE_PATH','').strip()
        if bundle_path:
            path=Path(bundle_path)
            if path.stat().st_size>262144: raise ValueError('R3 bundle too large')
            document=json.loads(path.read_text(encoding='utf-8'))
            self.bundle=ConfigurationBundle.model_validate(document['configuration'])
            if self.bundle.hardware_profile!=self.profile.profile_id or self.bundle.software_version!=r3_software_fingerprint():
                raise ValueError('R3 bundle hardware/software mismatch')
            for record in document.get('calibrations',[]): self.channel.calibrations.register(Calibration.model_validate(record))
            for key,reason in document.get('invalid_calibrations',{}).items(): self.channel.calibrations.invalidate(key,reason)
        self.channel.configurations.register(self.bundle)
        reasoning_path=os.getenv('TARK_R3_REASONING_PATH','').strip()
        if reasoning_path:
            if Path(reasoning_path).stat().st_size>65536:raise ValueError('reasoning configuration too large')
            reasoning_config=ReasoningConfig.model_validate_json(Path(reasoning_path).read_text(encoding='utf-8'))
        else:reasoning_config=ReasoningConfig()
        self.reasoner=R3Reasoner(reasoning_config,self.bundle.software_version)
        self.advisory=None
        self.reasoning_metrics={'cycle_latency_ns':None,'track_count':0,'queue_depth':0}
        self.experiments=ExperimentStore(database_path)
        self.workers=[]
        self.faults=[]
        self.inference=UnavailableInferenceProvider()
        fixture=os.getenv('TARK_R3_FIXTURE_PATH','').strip()
        if fixture:
            if settings.mode!='simulation' or active_profile!='R3_PI5_ADVISORY':
                self.experiments.close()
                raise ValueError('R3 fixtures require explicit simulation and R3_PI5_ADVISORY profile')
            self.workers.append(FixtureSources(self.channel,self.bundle,Path(fixture)))
    def pump(self,now:int):
        for worker in self.workers:worker.pump(now)
    def ingest(self,observation,now:int):
        if self.active_profile!='R3_PI5_ADVISORY': raise ValueError('R3 input cannot enter legacy profile')
        return ObservationAdapter(self.channel,observation.identity.source_id).ingest(observation,now)
    def capture(self,now:int,decision:dict):
        # A callback must not change evidence between its HMI snapshot and its
        # recorded provenance. One lock, one consistent observation boundary.
        with self.channel._lock:
            start=time.perf_counter_ns()
            self.advisory=self.reasoner.step(self.channel,now)
            self.reasoning_metrics={**self.reasoner.metrics,'cycle_latency_ns':time.perf_counter_ns()-start}
            view=self.snapshot(now,decision);record=self.channel.record()
            record['reasoning_environment']=self.reasoner.config.environment.model_dump(mode='json')
            return view,record
    def snapshot(self,now:int,decision:dict|None=None):
        readiness=self.channel.snapshot(now)
        readiness.update(active_profile=self.active_profile,configuration_bundle_id=self.bundle.bundle_id,
                         configuration_hash=self.bundle.content_hash,software_version=self.bundle.software_version,
                         calibration_bundle=sorted({key for keys in self.bundle.calibration_bundle.values() for key in keys}),experiment=self.experiments.current(),
                         integration_gates=[{'id':g,'software_status':'IMPLEMENTED','hardware_status':'HARDWARE_TEST_PENDING'} for g in ('G14','G15','G16','G17')],
                         inference=self.inference.metrics(),advisory=self.advisory,reasoning_metrics=self.reasoning_metrics)
        readiness['explanation']={
            'schema_version':'TARK_WHY_1','decision_scope':'LEGACY_RADAR_RESEARCH_PIPELINE',
            'decision_state':decision['state'] if decision else 'UNKNOWN',
            'primary_reason':decision['reason_code'] if decision else 'NO_DECISION',
            'supporting_evidence':[],
            'degraded_evidence':[r['source_id'] for r in readiness['sources'] if r['producing'] and not r['qualified']],
            'unavailable_evidence':[r['source_id'] for r in readiness['sources'] if not r['producing']],
            'configuration_bundle_id':self.bundle.bundle_id,
            'reason':'R3 sources do not participate in the legacy decision. The separately versioned R3 advisory has its own evidence and research assumptions.',
            'motion_authority':False}
        return readiness
    def recording_metadata(self):
        if r3_software_fingerprint()!=self.bundle.software_version:
            raise ValueError('R3 software changed on disk; restart before recording')
        return {'version':'TARK_R3_PROVENANCE_1','software_fingerprint':self.bundle.software_version,
                'profile':self.profile.model_dump(mode='json'),'profile_hash':digest(self.profile.model_dump(mode='json')),
                'active_profile':self.active_profile,'configuration':self.bundle.model_dump(mode='json'),
                'configuration_hash':self.bundle.content_hash,'experiment':self.experiments.current(),
                'reasoning':{'configuration':self.reasoner.config.model_dump(mode='json'),'configuration_hash':self.reasoner.config.content_hash,'checkpoint':self.reasoner.checkpoint()},
                'claims':'HARDWARE_UNVERIFIED; R3_RESEARCH_ADVISORY; LEGACY_DECISION_SCOPE_PRESERVED'}
    def close(self):
        for worker in self.workers: worker.close()
        self.experiments.close()
