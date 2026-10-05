from fastapi.testclient import TestClient
from app.main import DeploymentConfig, create_app, map_display_config
from app.config import Settings
from pathlib import Path
import re
import pytest
from starlette.websockets import WebSocketDisconnect
from runtime_fixtures import ControlledRuntime

def receive_error(socket,code):
    for _ in range(5):
        message=socket.receive_json()
        if message.get("type")=="error":
            assert message["payload"]["code"]==code
            return
    raise AssertionError(f"Did not receive error {code}")

def test_health_is_observation_only_and_phase1_disabled():
    response=TestClient(create_app()).get("/health")
    assert response.status_code==200
    assert response.json()["traction"]=="DISABLED_PHASE_1"

def test_map_display_defaults_to_india_overview_without_claiming_a_location(monkeypatch):
    monkeypatch.delenv("TARK_DEFAULT_MAP_CENTER", raising=False)
    monkeypatch.delenv("TARK_DEFAULT_MAP_ZOOM", raising=False)
    assert map_display_config()=={"longitude":78.9629,"latitude":20.5937,"zoom":4.2,"location_configured":False,"location_status":"INDIA_OVERVIEW_NO_VEHICLE_LOCATION","view_mode":"INDIA_OVERVIEW"}

def test_map_display_accepts_only_valid_display_center(monkeypatch):
    monkeypatch.setenv("TARK_DEFAULT_MAP_CENTER","77.5946,12.9716")
    monkeypatch.setenv("TARK_DEFAULT_MAP_ZOOM","12")
    assert map_display_config()["location_configured"] is True
    assert map_display_config()["view_mode"]=="CONFIGURED_LOCATION"
    monkeypatch.setenv("TARK_DEFAULT_MAP_CENTER","999,999")
    assert map_display_config()["location_configured"] is False

def test_fastapi_serves_compiled_frontend_and_assets():
    client=TestClient(create_app())
    page=client.get("/")
    assert page.status_code==200 and "<div id=\"root\"></div>" in page.text
    asset=re.search(r'src="([^"]+\.js)"',page.text)
    assert asset and client.get(asset.group(1)).status_code==200

def test_health_and_frontend_have_safe_deployment_headers():
    response=TestClient(create_app()).get("/health")
    assert response.status_code==200
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert response.headers["x-content-type-options"]=="nosniff"
    assert "geolocation=(self)" in response.headers["permissions-policy"]
    assert "camera=()" in response.headers["permissions-policy"]

def test_browser_camera_capability_requires_explicit_server_enablement(monkeypatch):
    monkeypatch.delenv("TARK_ENABLE_BROWSER_CAMERA", raising=False)
    assert TestClient(create_app()).get("/api/v1/diagnostics").json()["capabilities"]["browser_camera_preview"] is False
    monkeypatch.setenv("TARK_ENABLE_BROWSER_CAMERA", "true")
    response=TestClient(create_app()).get("/api/v1/diagnostics")
    assert response.json()["capabilities"]["browser_camera_preview"] is True
    assert "camera=(self)" in response.headers["permissions-policy"]

def test_public_demo_csp_excludes_insecure_websocket_transport():
    response=TestClient(create_app(deployment=DeploymentConfig(environment="public_demo"))).get("/health")
    policy=response.headers["content-security-policy"]
    assert "connect-src 'self' https: wss:" in policy
    assert " wss: ws:" not in policy

def test_public_deployment_profiles_reject_unsafe_authentication_combinations():
    with pytest.raises(ValueError, match="public_demo deployments"):
        DeploymentConfig(environment="public_demo", auth_mode="authenticated")
    with pytest.raises(ValueError, match="public_hardware deployments"):
        DeploymentConfig(environment="public_hardware", auth_mode="public_demo")

def test_cors_rejects_wildcards_and_non_origin_values():
    for origin in ("*", "https://example.test/path", "file:///tmp/tark"):
        with pytest.raises(ValueError, match="TARK_CORS_ORIGINS"):
            DeploymentConfig(cors_origins=(origin,))
    client=TestClient(create_app(deployment=DeploymentConfig(cors_origins=("https://console.example",))))
    response=client.get("/api/v1/status", headers={"Origin":"https://console.example"})
    assert response.headers["access-control-allow-origin"]=="https://console.example"

def test_authenticated_mode_blocks_api_until_a_session_is_created():
    with TestClient(create_app(deployment=DeploymentConfig(environment="development",auth_mode="authenticated",access_token="test-token"))) as client:
        assert client.get("/api/v1/status").status_code==401
        assert client.post("/api/v1/auth/session",headers={"Authorization":"Bearer wrong"}).status_code==401
        assert client.post("/api/v1/auth/session",headers={"Authorization":"Bearer test-token"}).status_code==204
        assert client.get("/api/v1/status").status_code==200

def test_authenticated_public_hardware_session_uses_secure_cookie_attributes():
    client=TestClient(create_app(deployment=DeploymentConfig(environment="public_hardware",auth_mode="authenticated",access_token="test-token")))
    response=client.post("/api/v1/auth/session",headers={"Authorization":"Bearer test-token"})
    cookie=response.headers["set-cookie"].lower()
    assert response.status_code==204
    assert "httponly" in cookie and "secure" in cookie and "samesite=strict" in cookie

def test_authenticated_mode_rejects_unauthorized_websocket():
    client=TestClient(create_app(deployment=DeploymentConfig(environment="development",auth_mode="authenticated",access_token="test-token")))
    with pytest.raises(WebSocketDisconnect) as closed:
        with client.websocket_connect("/api/v1/ws"):
            pass
    assert closed.value.code==1008

def test_authenticated_websocket_does_not_accept_a_url_token():
    client=TestClient(create_app(deployment=DeploymentConfig(environment="development",auth_mode="authenticated",access_token="test-token")))
    with pytest.raises(WebSocketDisconnect) as closed:
        with client.websocket_connect("/api/v1/ws?access_token=test-token"):
            pass
    assert closed.value.code==1008

def test_public_demo_is_locked_to_simulation():
    settings=Settings.from_file(Path(__file__).parents[2] / "config" / "phase1.json").model_copy(update={"mode":"real_radar"})
    with pytest.raises(ValueError, match="public_demo deployments must use simulation mode"):
        create_app(settings=settings, deployment=DeploymentConfig(environment="public_demo"))

def test_no_direct_motor_control_route_exists():
    app=create_app()
    paths={route.path for route in app.routes}
    assert not any("motor" in path or "traction" in path or "command" in path for path in paths)

def test_websocket_publishes_observation_only_status():
    with TestClient(create_app()) as client, client.websocket_connect("/api/v1/ws") as socket:
        status=socket.receive_json()
        assert status["type"]=="status" and status["payload"]["traction"]=="DISABLED_PHASE_1"
        assert status["payload"]["vehicle_location"]["location"]["source"]=="SIMULATION"
        location=socket.receive_json()
        assert location["type"]=="location_update" and location["payload"]["location"]["source"]=="SIMULATION"
        socket.send_json({"type":"attempt_command"})
        receive_error(socket,"UNSUPPORTED_OBSERVATION_MESSAGE")
        socket.send_json([])
        receive_error(socket,"MALFORMED_OBSERVATION_MESSAGE")

def test_events_and_recording_sessions_are_persisted_without_fabrication(tmp_path, monkeypatch):
    monkeypatch.setenv("TARK_DATABASE_PATH",str(tmp_path/"events.db"))
    controlled=ControlledRuntime()
    with TestClient(create_app(runtime_factory=controlled)) as client:
        events=client.get("/api/v1/events").json()
        assert events and events[0]["event_type"]=="PVSOE_DECISION"
        assert client.get("/api/v1/runs").json()==[]
        session=client.post("/api/v1/recordings/start").json()
        assert session["status"]=="RECORDING"
        client.get("/api/v1/status")
        client.portal.call(controlled.step)
        stopped=client.post("/api/v1/recordings/stop").json()
        assert stopped["status"]=="COMPLETE" and stopped["record_count"]==1
        assert client.get("/api/v1/replay/sessions").json()[0]["session_id"]==session["session_id"]
        assert client.get(f"/api/v1/replay/sessions/{session['session_id']}/records").json()[0]["kind"]=="OBSERVATION_TICK_V2"
        timeline=client.get(f"/api/v1/replay/sessions/{session['session_id']}/timeline")
        assert timeline.status_code==200 and timeline.json()["source_mode"]=="REPLAY" and timeline.json()["state"]=="READY"
        assert client.post(f"/api/v1/replay/sessions/{session['session_id']}/verify").json()["result"]=="MATCH"
        assert client.get("/api/v1/replay/sessions/missing").status_code==404

def test_replay_timeline_and_verification_reject_incompatible_configuration(tmp_path, monkeypatch):
    monkeypatch.setenv("TARK_DATABASE_PATH",str(tmp_path/"events.db"))
    controlled=ControlledRuntime()
    app=create_app(runtime_factory=controlled)
    with TestClient(app) as client:
        session=client.post("/api/v1/recordings/start").json()
        client.get("/api/v1/status")
        client.portal.call(controlled.step)
        client.post("/api/v1/recordings/stop")
        app.state.system.recording_store.db.execute("UPDATE recording_sessions SET configuration_hash='different' WHERE id=?",(session["session_id"],))
        app.state.system.recording_store.db.commit()
        assert client.get(f"/api/v1/replay/sessions/{session['session_id']}/timeline").status_code==409
        assert client.post(f"/api/v1/replay/sessions/{session['session_id']}/verify").status_code==409
