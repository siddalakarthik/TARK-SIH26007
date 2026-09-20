import time
from app.i2c_transport import I2cSensorWorker, I2cTransport
from app.imu import Bno055Adapter, ImuConfig
from app.thermal import Mlx90640Adapter, ThermalConfig

class FakeBus:
    def __init__(self):self.closed=False;self.writes=[]
    def read_byte_data(self,address,register):return 7
    def read_i2c_block_data(self,address,register,length):return list(range(length))
    def write_byte_data(self,address,register,value):self.writes.append((address,register,value))
    def close(self):self.closed=True

def test_transport_identity_is_not_verified_by_address_and_read_write_are_bounded():
    bus=FakeBus();transport=I2cTransport(1,0x28,lambda _:bus)
    assert transport.candidate_identity().identity_state=='UNVERIFIED'
    assert transport.read_byte(0)==7 and transport.read_block(1,3)==b'\x00\x01\x02';transport.write_byte(2,4);transport.close();assert bus.closed

def test_worker_single_start_clean_stop_and_sensor_identity_gate():
    values=[];worker=I2cSensorWorker(lambda:5,values.append,.01,.01);assert worker.start() and not worker.start();time.sleep(.03);worker.stop();assert values and worker.thread is None
    imu=Bno055Adapter(ImuConfig(address='0x28'));thermal=Mlx90640Adapter(ThermalConfig(address='0x33'))
    assert not imu.start_verified_worker(lambda:None) and not thermal.start_verified_worker(lambda:())
    imu.record_verified_identity('mocked chip-id evidence',chip_id='fixture');thermal.record_verified_identity('mocked identity evidence',chip_id='fixture')
    assert imu.identity.state=='VERIFIED' and thermal.identity.state=='VERIFIED'
