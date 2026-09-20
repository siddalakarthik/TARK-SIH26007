from fastapi.testclient import TestClient
from app.main import create_app

def test_startup_contract_is_simulation_only_without_hardware():
    client=TestClient(create_app())
    health=client.get("/health")
    status=client.get("/api/v1/status")
    assert health.status_code==200 and health.json()["status"]=="ready"
    assert health.json()["traction"]=="DISABLED_PHASE_1"
    assert status.status_code==200
    payload=status.json()
    assert payload["mode"]=="SIMULATION" and payload["traction"]=="DISABLED_PHASE_1"
    assert any(sensor["source_mode"]=="NOT_CONNECTED_PHASE_2" for sensor in payload["sensors"])
