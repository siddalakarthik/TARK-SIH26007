import json
import struct
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from pydantic import ValidationError
from app.r3.contracts import *
from app.r3.registry import *
from app.r3.evidence import EvidenceChannel
from app.r3.adapters import *
from app.r3.vendor import *
from app.r3.cooperative import PeerMessage, PeerReceiver, encode_peer

ROOT=Path(__file__).parents[2]
NOW=1_000_000_000

def setup_channel(source='gnss-base',mode='SIMULATION'):
    profile=HardwareProfile.model_validate_json((ROOT/'config/r3_pi5_advisory.json').read_text())
    channel=EvidenceChannel(profile,'host-1')
    p=channel.profiles[source]
    identity=Identity(source_id=source,node_id=p.node_id,device_class=p.device_class,manufacturer=p.manufacturer,
        part_number=p.part_number,driver_version='fixture-1',boot_id='boot-1',session_id='session-1',asset_id='fixture-asset')
    bundle=ConfigurationBundle(bundle_id='fixture-bundle',hardware_profile=profile.profile_id,driver_profile='fixture',sensor_modes={},
        radar_profile=None,camera_mode=None,thermal_mode=None,gnss_configuration=None,network_profile='fixture',
        calibration_bundle={},mounts={},ai_model=None,pvsoe_parameter_set='existing-unmodified',vehicle_parameters={},software_version='fixture-1')
    channel.configurations.register(bundle)
    channel.begin_source(identity,mode)
    mapping=ClockMapping(mapping_id='map-1',source_id=source,clock_domain='fixture-clock',source_boot_id='boot-1',host_epoch='host-1',
        native_anchor=0,host_anchor_ns=0,ns_per_tick=1.,offset_uncertainty_ns=1000,drift_ppm=0.,drift_uncertainty_ppm=0.,
        last_synchronization_ns=0,valid_until_ns=10_000_000_000,max_drift_ppm=50.,evidence_reference='synthetic-clock-fixture',status='TIME_VALID')
    channel.clocks.register(mapping)
    def observation(sequence=1,stamp=NOW):
        return Observation(observation_id=f'fixture-{sequence}',identity=identity,
            time=ObservationTime(native_timestamp=stamp,native_timestamp_units='ns',native_clock_domain='fixture-clock',host_epoch='host-1',
                host_monotonic_arrival=stamp+1000,estimated_capture_time=stamp,capture_time_uncertainty=1000,
                clock_mapping_version='map-1',publication_time=stamp+2000,measurement_age=2000),
            integrity=Integrity(sequence_number=sequence,source_counter=sequence,payload_length=10,check_result='PASS'),
            measurement=Measurement(kind='FIXTURE',payload={'value':1.},units={'value':'synthetic'},sensor_frame='FIXTURE_ONLY',mode_profile='fixture',configuration_hash=bundle.content_hash),
            qualification=Qualification(connection_state='CONNECTED',production_state='PRODUCING',health_state='ONLINE',plausibility_state='PLAUSIBLE',uncertainty={'synthetic':1.},uncertainty_origin='SYNTHETIC_FIXTURE'),
            provenance=Provenance(mode=mode,evidence_origin='REAL_CAPTURE' if mode=='REAL' else 'SYNTHETIC_FIXTURE',software_version='fixture-1',configuration_bundle_id=bundle.bundle_id))
    return channel,observation

def mutate(observation,path,value):
    data=observation.model_dump(mode='json'); cursor=data
    for part in path[:-1]: cursor=cursor[part]
    cursor[path[-1]]=value
    return Observation.model_validate(data)

def test_evidence_schema_roundtrip_preserves_null_identity():
    _,factory=setup_channel(); o=factory()
    assert Observation.model_validate_json(o.model_dump_json())==o
    assert o.identity.hardware_revision is None and o.time.utc_time is None

@pytest.mark.parametrize('path,value',[
    (['integrity','sequence_number'],True),(['integrity','sequence_number'],-1),
    (['measurement','payload'],{'bad':float('nan')}),(['measurement','payload'],{'bad':float('inf')}),
    (['time','measurement_age'],0),(['time','estimated_capture_time'],NOW+2001),
    (['time','utc_time'],'2026-10-04T00:00:00Z'),(['provenance','mode'],'REAL'),
    (['qualification','uncertainty_origin'],None),(['measurement','payload'],{'large':'x'*66000})])
def test_bad_contract_rejected(path,value):
    _,factory=setup_channel()
    with pytest.raises((ValueError,ValidationError)): mutate(factory(),path,value)

def test_claimed_qualified_is_not_authoritative():
    c,f=setup_channel('radar-a'); o=mutate(f(),['qualification','qualified_for'],['ALL_SAFETY'])
    c.accept(o,NOW+2000); row=c.readiness('radar-a',NOW+2000)
    assert row['fresh'] and row['time_valid'] and not row['calibration_valid'] and not row['qualified']
    assert row['qualified_for']==[]

def test_freshness_expiry_duplicates_do_not_refresh():
    c,f=setup_channel(); c.accept(f(),NOW+2000)
    assert c.readiness('gnss-base',NOW+2000)['qualified']
    assert not c.accept(f(),NOW+900000000)
    assert c.latest['gnss-base'].time.host_monotonic_arrival==NOW+1000
    assert not c.readiness('gnss-base',NOW+2_000_000_000)['fresh']

def test_real_identity_is_not_verified_by_sample():
    c,f=setup_channel(mode='REAL'); c.accept(f(),NOW+2000)
    assert not c.readiness('gnss-base',NOW+2000)['identity_verified']
    assert not c.readiness('gnss-base',NOW+2000)['qualified']

def test_replay_cannot_enter_live_channel():
    c,f=setup_channel()
    data=f().model_dump(mode='json'); data['provenance'].update(mode='REPLAY',evidence_origin='REPLAY_RECORD',original_mode='SIMULATION')
    with pytest.raises(ValueError): c.accept(Observation.model_validate(data),NOW+2000)

def test_host_restart_and_source_restart_invalidate_old_evidence():
    c,f=setup_channel(); c.accept(f(),NOW+2000)
    with pytest.raises(ValueError): c.accept(mutate(f(2),['time','host_epoch'],'host-2'),NOW+2000)
    new=f().identity.model_copy(update={'boot_id':'new-boot','session_id':'new-session'})
    c.begin_source(new,'SIMULATION'); assert c.latest=={}
    with pytest.raises(ValueError): c.accept(f(),NOW+2000)

def test_wrong_device_not_legacy_substituted():
    c,f=setup_channel('imu-a')
    with pytest.raises(ValueError): c.begin_source(f().identity.model_copy(update={'part_number':'BNO055'}),'SIMULATION')

@pytest.mark.parametrize('change,expected',[
    ({'source_boot_id':'other'},'CLOCK_RESET'),({'host_epoch':'other'},'CLOCK_RESET'),
    ({'native_anchor':NOW+1},'TIMESTAMP_INVALID'),({'drift_ppm':51.},'CLOCK_DRIFT_EXCEEDED'),
    ({'valid_until_ns':100},'TIME_UNSYNCED'),({'status':'TIME_UNSYNCED'},'TIME_UNSYNCED')])
def test_clock_faults(change,expected):
    c,_=setup_channel(); m=c.clocks.records['map-1'].model_copy(update=change); c.clocks.records['map-1']=m
    assert c.clocks.capture('map-1',NOW,source_id='gnss-base',boot_id='boot-1',host_epoch='host-1',now=NOW+2000)[2]==expected

def test_arrival_fresh_can_be_time_unqualified():
    c,f=setup_channel(); c.clocks.records.clear(); c.accept(f(),NOW+2000)
    row=c.readiness('gnss-base',NOW+2000); assert row['fresh'] and row['producing'] and not row['time_valid'] and not row['qualified']

def test_bounded_queue_overload_and_out_of_order():
    c,f=setup_channel()
    for i in range(1,101): c.accept(f(i,NOW+i*1000),NOW+i*1000+2000)
    assert len(c.queues['gnss-base'])==8 and c.counters['gnss-base']['history_evictions']==92
    assert c.counters['gnss-base']['drops']==0  # retained-history trimming is not packet loss
    assert not c.accept(f(99,NOW+100_000),NOW+102_000)
    assert c.counters['gnss-base']['out_of_order']==1

def test_concurrent_duplicate_has_one_acceptance():
    c,f=setup_channel()
    with ThreadPoolExecutor(8) as pool: results=list(pool.map(lambda _:c.accept(f(),NOW+2000),range(32)))
    assert sum(results)==1 and c.counters['gnss-base']['duplicates']==31

def test_missing_calibration_never_identity_transform():
    registry=CalibrationRegistry()
    assert not registry.valid('missing',kind='RADAR_TO_BODY',asset_id='x',mount_revision='m1')
    record=Calibration(calibration_id='cal1',version='1',kind='RADAR_TO_BODY',asset_ids=['a'],mount_revision='m1',method='FIXTURE',date='2026-10-04',operator='test',
        transform=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.],units='m',coordinate_frame_convention='x-forward-y-left-z-up',
        residuals={'m':.02},validity_domain='SYNTHETIC',software_version='test',artifacts=['fixture'])
    registry.register(record)
    assert registry.valid('cal1:1',kind=record.kind,asset_id='a',mount_revision='m1')
    assert not registry.valid('cal1:1',kind=record.kind,asset_id='a',mount_revision='m2')
    registry.invalidate('cal1:1','MAST_MOVED')
    assert not registry.valid('cal1:1',kind=record.kind,asset_id='a',mount_revision='m1')
    with pytest.raises(ValueError): registry.register(record.model_copy(update={'method':'changed'}))

def test_ti_payload_preserves_radial_velocity_not_full_vector():
    result=ti_cartesian_points(struct.pack('<ffff',1,2,3,-.5),count=1,frame_number=3,firmware_profile='SYNTHETIC_OOB_TLV')
    assert result.points[0].radial_velocity_mps==-.5
    with pytest.raises(ValueError): ti_cartesian_points(b'',count=1,frame_number=3,firmware_profile='fixture')
    with pytest.raises(ValueError): ti_cartesian_points(struct.pack('<ffff',float('nan'),0,0,0),count=1,frame_number=3,firmware_profile='fixture')

@pytest.mark.parametrize('report_id,scale,key',[(1,256,'acceleration_m_s2'),(2,512,'angular_velocity_rad_s'),(4,256,'acceleration_m_s2')])
def test_sh2_documented_units(report_id,scale,key):
    report=bytes([report_id,1,3,0])+struct.pack('<hhh',scale,0,-scale)
    result=sh2_sensor_report(report); assert getattr(result,key)==[1.,0.,-1.] and result.sh2_timestamp_us is None
    with pytest.raises(ValueError): sh2_sensor_report(report[:-1])

def test_no_fake_thermal_or_stationary_heading():
    with pytest.raises(ValueError): LeptonFrame(frame_id='f',width=160,height=120,pixel_format='Y16',media_reference='fixture',sha256='0'*64,ffc_state='UNKNOWN',radiometry='UNAVAILABLE',temperatures_c=[0.]*19200)
    with pytest.raises(ValueError): Lg290pFix(fix_type='RTK_FIXED',speed_mps=0.,course_deg=0.)

def test_reader_reconnect_and_shutdown():
    samples=[]; calls=[]
    def unavailable(): calls.append(1); raise OSError('fixture absent')
    reader=ConfiguredReader('lg290p',unavailable,samples.append,reconnect_ns=100)
    reader.pump(0); reader.pump(99); assert len(calls)==1 and reader.state=='UNAVAILABLE'
    reader.pump(100); assert len(calls)==2
    reader.close(); reader.pump(200); assert len(calls)==2 and not samples

def peer_message(sequence=1):
    return PeerMessage(protocol_version=1,node_id='B',boot_id='boot',session_id='session',sequence=sequence,source_timestamp_ns=100,
        publication_time_ns=200,clock_domain='B_MONOTONIC',clock_mapping_id='map',capture_uncertainty_ns=10,
        fix=Lg290pFix(fix_type='RTK_FLOAT',latitude_deg=17.,longitude_deg=78.,horizontal_uncertainty_m=2.),health='ONLINE',faults=[],configuration_id='cfg',source_mode='SIMULATION')

def test_peer_integrity_expiry_and_restart():
    key=b'x'*32
    receiver=PeerReceiver(node_id='B',configuration_id='cfg',key=key,max_age_ns=500,max_uncertainty_ns=20,mode='SIMULATION',max_position_uncertainty_m=3.)
    receiver.admit_session('boot','session')
    raw=encode_peer(peer_message(),key)
    assert receiver.receive(raw,200,lambda m,n:(100,10))
    assert receiver.status(200)['state']=='QUALIFIED_COOPERATIVE_CONTEXT'
    assert not receiver.receive(raw,300,lambda m,n:(100,10))
    assert receiver.status(800)['position'] is None
    receiver.admit_session('boot2','session2')
    with pytest.raises(ValueError): receiver.receive(raw,900,lambda m,n:(100,10))
    assert receiver.status(900)['position'] is None

def test_peer_bad_auth_and_unknown_time():
    key=b'x'*32; receiver=PeerReceiver(node_id='B',configuration_id='cfg',key=key,max_age_ns=500,max_uncertainty_ns=20,mode='SIMULATION')
    receiver.admit_session('boot','session')
    with pytest.raises(ValueError): receiver.receive(encode_peer(peer_message(),b'y'*32),200,lambda m,n:(100,10))
    assert receiver.receive(encode_peer(peer_message(),key),200,lambda m,n:(None,None))
    assert receiver.status(201)['position'] is None

def test_peer_uncertainty_correction_loss_and_packet_loss():
    key=b'x'*32
    receiver=PeerReceiver(node_id='B',configuration_id='cfg',key=key,max_age_ns=500,max_uncertainty_ns=20,mode='SIMULATION',max_position_uncertainty_m=3.,require_corrections=True)
    receiver.admit_session('boot','session')
    message=peer_message().model_copy(update={'correction_state':'APPLIED'})
    assert receiver.receive(encode_peer(message,key),200,lambda m,n:(100,10))
    assert receiver.status(200)['position'] is not None
    receiver.receive(encode_peer(message.model_copy(update={'sequence':4,'correction_state':'LOST'}),key),210,lambda m,n:(110,10))
    assert receiver.status(210)['position'] is None and receiver.drops==2
    large=message.model_copy(update={'sequence':5,'fix':message.fix.model_copy(update={'horizontal_uncertainty_m':100.})})
    receiver.receive(encode_peer(large,key),220,lambda m,n:(120,10))
    assert receiver.status(220)['position'] is None

def test_peer_datagram_worker_bounded_and_reconnects_without_devices():
    from app.r3.cooperative import DatagramPeerWorker
    from unittest.mock import Mock
    receiver=Mock();receiver.receive.return_value=True
    socket=Mock();socket.recvfrom.side_effect=[(b'packet',('fixture',123))]*40+[BlockingIOError()]
    worker=DatagramPeerWorker(receiver,('fixture',123),lambda:socket,lambda m,n:(None,None),retry_ns=100)
    worker.pump(1000);assert receiver.receive.call_count==32
    worker.pump(1100);assert receiver.receive.call_count==40
    socket.recvfrom.side_effect=OSError('fixture dropout');worker.pump(1200)
    assert worker.state=='NETWORK_UNAVAILABLE';worker.close();worker.pump(1300)
    assert worker.socket is None
