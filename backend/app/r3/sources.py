"""Device validation and explicitly synthetic fixture input for the R3 channel."""
import json
from pathlib import Path
from app.r3.adapters import validate_sample
from app.r3.contracts import Identity, Observation, ObservationTime, Integrity, Measurement, Qualification, Provenance, digest
from app.r3.registry import ClockMapping

class ObservationAdapter:
    """Called by a reviewed device reader; no serial/USB/I2C calls or motor API."""
    def __init__(self,channel,source_id):
        self.channel=channel;self.profile=channel.profiles[source_id]
    def ingest(self,observation:Observation,now_ns:int):
        if observation.identity.source_id!=self.profile.source_id: raise ValueError('wrong adapter source')
        if observation.measurement.kind!=self.profile.adapter: raise ValueError('wrong R3 device payload kind')
        validate_sample(self.profile.adapter,observation.measurement.payload)
        return self.channel.accept(observation,now_ns)

class FixtureSources:
    """One bounded batch per runtime tick. Samples are synthetic, never live."""
    def __init__(self,channel,bundle,path:Path):
        if path.stat().st_size>262144: raise ValueError('fixture file too large')
        raw=json.loads(path.read_text(encoding='utf-8'))
        if raw.get('format')!='TARK_R3_SYNTHETIC_1' or not isinstance(raw.get('samples'),dict): raise ValueError('not a synthetic fixture manifest')
        if not raw['samples'] or set(raw['samples'])-set(channel.profiles): raise ValueError('unexpected fixture sources')
        self.samples={source:validate_sample(channel.profiles[source].adapter,value) for source,value in raw['samples'].items()}
        self.channel=channel;self.bundle=bundle;self.sequence=0;self.closed=False;self.identities={}
        self.reference=path.name;self.hash=digest(raw)
    def pump(self,now:int):
        if self.closed:return
        if not self.identities:
            for source in self.samples:
                p=self.channel.profiles[source]
                identity=Identity(source_id=source,node_id=p.node_id,device_class=p.device_class,manufacturer=p.manufacturer,
                    part_number=p.part_number,asset_id='synthetic-'+source,driver_version='R3_SYNTHETIC_1',boot_id='fixture-boot',session_id=self.channel.host_epoch)
                self.channel.begin_source(identity,'SIMULATION')
                self.identities[source]=identity
                self.channel.clocks.register(ClockMapping(mapping_id='fixture-clock-'+source,source_id=source,clock_domain='SYNTHETIC_HOST_CLOCK',
                    source_boot_id=identity.boot_id,host_epoch=self.channel.host_epoch,native_anchor=now,host_anchor_ns=now,ns_per_tick=1.,
                    offset_uncertainty_ns=1000,drift_ppm=0.,drift_uncertainty_ppm=0.,last_synchronization_ns=now,valid_until_ns=now+86_400_000_000_000,
                    max_drift_ppm=1.,evidence_reference='SYNTHETIC_FIXTURE_NOT_PHYSICAL_SYNC',status='TIME_VALID'))
        self.sequence+=1
        for source,payload in self.samples.items():
            profile=self.channel.profiles[source]
            observation=Observation(observation_id=f'{source}-fixture-{self.sequence}',identity=self.identities[source],
                time=ObservationTime(native_timestamp=now,native_timestamp_units='ns',native_clock_domain='SYNTHETIC_HOST_CLOCK',
                    host_epoch=self.channel.host_epoch,host_monotonic_arrival=now,estimated_capture_time=now,capture_time_uncertainty=1000,
                    clock_mapping_version='fixture-clock-'+source,publication_time=now,measurement_age=0),
                integrity=Integrity(sequence_number=self.sequence,source_counter=self.sequence,payload_length=len(json.dumps(payload).encode())),
                measurement=Measurement(kind=profile.adapter,payload=payload,units={'contract':'DEVICE_SPECIFIC_SI_FIELDS'},
                    sensor_frame='SYNTHETIC_UNCALIBRATED',mode_profile='FIXTURE_ONLY',configuration_hash=self.bundle.content_hash),
                qualification=Qualification(connection_state='CONNECTED',production_state='PRODUCING',health_state='ONLINE',
                    plausibility_state='PLAUSIBLE',uncertainty={'fixture_not_physical':1.},uncertainty_origin='SYNTHETIC_FIXTURE'),
                provenance=Provenance(mode='SIMULATION',evidence_origin='SYNTHETIC_FIXTURE',raw_record_reference=self.reference,raw_sha256=self.hash,
                    transformation_lineage=['NORMALIZED_SYNTHETIC_FIXTURE'],software_version=self.bundle.software_version,configuration_bundle_id=self.bundle.bundle_id))
            ObservationAdapter(self.channel,source).ingest(observation,now)
    def close(self):
        self.closed=True
        for source in self.identities:self.channel.stop_source(source,'FIXTURE_STOPPED')
