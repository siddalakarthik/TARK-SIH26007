from fastapi.testclient import TestClient
from app.imu import Bno055Adapter, ImuConfig
from app.thermal import Mlx90640Adapter, ThermalConfig
from app.hardware.interfaces import ImuSample
from app.main import create_app


def test_imu_discovery_validation_stale_simulation_and_recovery():
    imu=Bno055Adapter(ImuConfig(stale_ms=1));assert imu.discover()['state']=='NOT_CONNECTED'
    invalid=ImuSample(1,'SIMULATION',None,None,'UNKNOWN',quaternion=(float('nan'),0,0,0));assert not imu.accept(invalid) and imu.read_sample(1).state=='ERROR'
    imu.inject_simulation(now_ns=10,yaw_deg=15);assert imu.read_sample(10).state=='ONLINE' and imu.read_sample(2_000_000).state=='STALE'
    imu.inject_simulation(now_ns=2_000_001);assert imu.read_sample(2_000_001).source_mode=='SIMULATION' and imu.read_sample(2_000_001).state=='ONLINE'


def test_thermal_dimensions_invalid_stale_simulation_and_api_contract():
    thermal=Mlx90640Adapter(ThermalConfig(stale_ms=1));assert thermal.discover()['state']=='NOT_CONNECTED';assert not thermal.accept((1.0,)*767)
    thermal.inject_simulation(now_ns=10,warm_index=3);frame=thermal.read_frame(10);assert frame.state=='ONLINE' and len(frame.temperatures_c or ())==768
    assert thermal.read_frame(2_000_000).state=='STALE'
    client=TestClient(create_app());assert client.get('/api/v1/imu').json()['state']=='NOT_CONNECTED';assert client.get('/api/v1/thermal').json()['state']=='NOT_CONNECTED'
