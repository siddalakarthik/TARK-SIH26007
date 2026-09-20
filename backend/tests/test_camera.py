from pathlib import Path
import time
from fastapi.testclient import TestClient
from app.camera import CameraConfig, PiUvcCameraAdapter, discover_uvc_candidates
from app.main import create_app

class FakeCapture:
    def __init__(self, opened=True):self.opened=opened;self.released=False
    def isOpened(self):return self.opened
    def set(self,*_):return True
    def get(self,*_):return 10
    def read(self):return False,None
    def release(self):self.released=True

class FakeCv2:
    CAP_PROP_FRAME_WIDTH=1;CAP_PROP_FRAME_HEIGHT=2;CAP_PROP_FPS=3;IMWRITE_JPEG_QUALITY=4
    def __init__(self,opened=True):self.capture=FakeCapture(opened)
    def VideoCapture(self,_):return self.capture

def test_camera_no_device_discovery_fixture_frame_stale_and_shutdown(tmp_path):
    adapter=PiUvcCameraAdapter(CameraConfig(stale_ms=1))
    assert adapter.discover()["state"]=="NO_CAMERA" and not adapter.start()
    assert discover_uvc_candidates('/dev/video7')[0]['identity']=='UNVERIFIED'
    adapter.inject_frame_for_test(b'jpeg');assert adapter.read_frame(adapter.read_frame(0).metadata.timestamp_ns).metadata.source_mode=='SIMULATION'
    assert adapter.read_frame(10**20).metadata.state=='STALE'
    adapter.stop();assert adapter.read_frame(1).metadata.state=='NOT_CONNECTED'

def test_camera_open_failure_duplicate_prevention_and_api_contract():
    adapter=PiUvcCameraAdapter(CameraConfig(device_path='/dev/video9',reconnect_s=10),FakeCv2(opened=False));assert adapter.start();assert not adapter.start();time.sleep(.02);assert adapter.read_frame(1).metadata.state=='ERROR';adapter.stop()
    app=create_app();client=TestClient(app);status=client.get('/api/v1/cameras/vehicle-rgb');caps=client.get('/api/v1/cameras/vehicle-rgb/capabilities')
    assert status.status_code==200 and status.json()['stream_url'] is None and status.json()['state']=='NOT_CONNECTED'
    assert caps.status_code==200 and caps.json()['identity']=='UNVERIFIED'

def test_mocked_simulation_frame_can_exercise_mjpeg_contract_without_hardware_claim():
    app=create_app();app.state.system.camera.inject_frame_for_test(b'fake-jpeg')
    response=TestClient(app).get('/api/v1/cameras/vehicle-rgb')
    assert response.status_code==200 and response.json()['source_mode']=='SIMULATION'
    assert response.json()['stream_url']=='/api/v1/cameras/vehicle-rgb/stream' and response.json()['hardware_claim']=='NOT_CONNECTED'
