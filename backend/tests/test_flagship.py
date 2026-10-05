"""Software-only flagship contract tests; no adapter or port is opened."""
from copy import deepcopy
import json
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

from app.flagship import HISTORY_LIMIT, flagship_snapshot


def observation(sequence=1):
    return {"command": {"sequence": sequence, "left_command": 0, "right_command": 0},
            "timestamp_ns": 1_000_000_000, "decision": {"state": "UNKNOWN"}}


def test_flagship_fixture_is_deterministic_finite_non_actuating_and_detached():
    original = observation()
    before = deepcopy(original)
    first = flagship_snapshot("simulation", original, 1_001_000_000)
    second = flagship_snapshot("simulation", original, 1_001_000_000)
    assert first == second
    assert original == before
    assert first["schema_version"] == "tark.flagship.v1"
    assert first["source_mode"] == "SIMULATION"
    assert first["traction"] == "DISABLED_PHASE_1"
    assert first["monitoring_only"] is True and first["hardware_verified"] is False
    assert first["decision_source"] == "/api/v1/status"
    json.dumps(first, allow_nan=False)
    first["participants"][0]["capabilities"].append("CORRUPT")
    assert "CORRUPT" not in second["participants"][0]["capabilities"]


def test_participant_b_is_location_only_and_course_is_not_body_heading():
    data = flagship_snapshot("simulation", observation(), 1_020_000_000)
    a, b = data["participants"]
    assert a["id"] == "A" and "RADAR" in a["capabilities"]
    assert b["id"] == "B" and b["role"] == "LOCATION_ONLY"
    assert b["capabilities"] == ["GNSS", "PEER_TELEMETRY"]
    for participant in (a, b):
        assert participant["source_mode"] == "SIMULATION"
        assert participant["state"] == "SIMULATED"
        assert participant["quality"] == "SIMULATED_FIX"
        assert participant["age_ms"] == 20
        assert participant["heading_deg"] is None
        assert 0 < participant["speed_mps"] <= 1
        assert 0 <= participant["course_deg"] < 360


@pytest.mark.parametrize("mode", ["real_radar", "replay", "unknown", "SIMULATION"])
def test_only_exact_simulation_mode_can_generate_positions(mode):
    with patch("app.flagship._point_along", side_effect=AssertionError("must not simulate")):
        data = flagship_snapshot(mode, observation(), 1_000_000_000)
    assert data["mode"] == mode.upper()
    assert data["source_mode"] == "UNAVAILABLE"
    assert data["scene"]["source"] == "UNAVAILABLE"
    assert data["scene"]["review_status"] == "UNAVAILABLE_NOT_SURVEYED"
    assert "India overview" in data["scene"]["label"]
    for participant in data["participants"]:
        assert participant["position"] is None
        assert participant["timestamp_ns"] is None
        assert participant["age_ms"] is None
        assert participant["speed_mps"] is None
        assert participant["course_deg"] is None
        assert participant["accuracy_m"] is None
    for name in ("roads", "route", "zones", "waypoints", "hazards", "history"):
        assert data["scene"][name]["features"] == []


@pytest.mark.parametrize("sequence", [0, 1, 4, 251, 100_000, 4_294_967_295])
def test_course_and_histories_remain_bounded_and_finite(sequence):
    data = flagship_snapshot("simulation", observation(sequence), 1_000_000_000)
    scene = data["scene"]
    west, south, east, north = scene["bounds"]
    for participant in data["participants"]:
        assert west <= participant["position"]["longitude_deg"] <= east
        assert south <= participant["position"]["latitude_deg"] <= north
    assert scene["review_status"] == "DEMO_FIXTURE_NOT_SURVEYED"
    for collection in ("roads", "route", "zones", "waypoints", "hazards", "history"):
        for feature in scene[collection]["features"]:
            assert feature["properties"]["source_mode"] == "SIMULATION"
            assert feature["properties"]["operational_authority"] is False
    for feature in scene["history"]["features"]:
        assert 2 <= len(feature["geometry"]["coordinates"]) <= HISTORY_LIMIT
        participant = next(p for p in data["participants"] if p["id"] == feature["properties"]["participant_id"])
        assert feature["geometry"]["coordinates"][-1] == [participant["position"]["longitude_deg"],
                                                          participant["position"]["latitude_deg"]]
    json.dumps(data, allow_nan=False)
    assert len(json.dumps(data)) < 30_000


def test_hardware_inventory_does_not_claim_new_drivers_or_hardware_verified():
    hardware = flagship_snapshot("simulation", observation(), 1_000_000_000)["hardware"]
    assert len(hardware) == 9
    assert all(row["status"] == "HARDWARE_PENDING" for row in hardware)
    by_id = {row["id"]: row for row in hardware}
    for identifier in ("radar", "thermal", "imu", "compute", "wheels"):
        assert by_id[identifier]["software_readiness"] == "MIGRATION_REQUIRED"
    assert "LD2450" in by_id["radar"]["reason"]
    assert "BNO055" in by_id["imu"]["reason"]
    assert "MLX90640" in by_id["thermal"]["reason"]


@pytest.mark.parametrize("timestamp,sequence,now", [
    (-1, 1, 0), (1, -1, 2), (2, 1, 1), (True, 1, 2), (1, False, 2),
    (1.1, 1, 2), (1, 1.5, 2), ("1", 1, 2), (1, 1, float("nan")),
    (1, 1, float("inf")), (1, 1, True),
])
def test_invalid_runtime_metadata_is_not_normalized_into_valid_evidence(timestamp, sequence, now):
    snapshot = observation(sequence)
    snapshot["timestamp_ns"] = timestamp
    with pytest.raises(ValueError, match="invalid runtime"):
        flagship_snapshot("simulation", snapshot, now)


def test_endpoint_uses_cached_runtime_and_does_not_change_decision_or_commands(tmp_path, monkeypatch):
    from app.main import create_app
    from runtime_fixtures import ControlledRuntime
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "events.db"))
    controlled = ControlledRuntime()
    with TestClient(create_app(runtime_factory=controlled)) as client:
        before = client.get("/api/v1/status").json()
        first = client.get("/api/v1/flagship")
        assert first.status_code == 200
        assert first.headers["cache-control"] == "no-store"
        for _ in range(5):
            assert client.get("/api/v1/flagship").json() == first.json()
        after = client.get("/api/v1/status").json()
        assert before == after
        assert first.json()["sequence"] == before["command"]["sequence"]
        client.portal.call(controlled.step)
        advanced = client.get("/api/v1/flagship").json()
        assert advanced["sequence"] == first.json()["sequence"] + 1
        assert advanced["participants"][0]["position"] != first.json()["participants"][0]["position"]
        assert client.get("/api/v1/status").json()["command"]["left_command"] == 0


def test_endpoint_uses_existing_authentication_and_has_no_write_method(tmp_path, monkeypatch):
    from app.main import DeploymentConfig, create_app
    from runtime_fixtures import ControlledRuntime
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "events.db"))
    app = create_app(deployment=DeploymentConfig(auth_mode="authenticated", access_token="test-token"),
                     runtime_factory=ControlledRuntime())
    with TestClient(app) as client:
        assert client.get("/api/v1/flagship").status_code == 401
        response = client.get("/api/v1/flagship", headers={"Authorization": "Bearer test-token"})
        assert response.status_code == 200
        assert client.post("/api/v1/flagship", json={"command": "move"}).status_code == 405


def test_endpoint_does_not_fabricate_scene_when_runtime_is_unavailable(tmp_path, monkeypatch):
    from app.main import create_app
    from runtime_fixtures import ControlledRuntime
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "events.db"))
    app = create_app(runtime_factory=ControlledRuntime())
    try:
        assert TestClient(app).get("/api/v1/flagship").status_code == 503
    finally:
        app.state.system.close()


@pytest.mark.parametrize("mode", ["real_radar", "replay"])
def test_endpoint_non_simulation_does_not_activate_a_fixture_or_new_hardware(mode, tmp_path, monkeypatch):
    from pathlib import Path
    from app.config import Settings
    from app.main import create_app
    from runtime_fixtures import ControlledRuntime
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "events.db"))
    # Explicitly disable every pre-existing physical adapter selector. This
    # tests an existing hardware-capable mode without opening any device.
    for key in ("TARK_GNSS_DEVICE_PATH", "TARK_CAMERA_DEVICE_PATH", "TARK_ESP32_DEVICE_PATH",
                "TARK_LD2450_DEVICE_PATH", "TARK_IMU_I2C_ADDRESS", "TARK_THERMAL_I2C_ADDRESS"):
        monkeypatch.delenv(key, raising=False)
    settings = Settings.from_file(Path(__file__).parents[2] / "config" / "phase1.json").model_copy(update={"mode": mode})
    with patch("app.services.system.TarkSystem._start_configured_gnss") as gnss, \
         patch("app.services.system.TarkSystem._start_configured_camera") as camera, \
         patch("app.services.system.TarkSystem._select_configured_esp32") as esp32, \
         patch("app.services.system.TarkSystem._start_configured_ld2450_raw_capture") as radar, \
         patch("app.services.system.TarkSystem._start_configured_i2c_sensors") as i2c:
        app = create_app(settings=settings, runtime_factory=ControlledRuntime())
        with TestClient(app) as client:
            startup_calls = [mock.call_count for mock in (gnss, camera, esp32, radar, i2c)]
            with patch("app.flagship._point_along", side_effect=AssertionError("no simulation in hardware/replay")):
                response = client.get("/api/v1/flagship")
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == mode.upper()
            assert data["source_mode"] == "UNAVAILABLE"
            assert all(p["position"] is None for p in data["participants"])
            assert data["scene"]["route"]["features"] == []
            assert all(row["status"] == "HARDWARE_PENDING" for row in data["hardware"])
            assert startup_calls == [mock.call_count for mock in (gnss, camera, esp32, radar, i2c)]


def test_endpoint_does_not_publish_when_runtime_snapshot_has_expired(tmp_path, monkeypatch):
    from app.main import create_app
    from runtime_fixtures import ControlledRuntime
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "events.db"))
    controlled = ControlledRuntime()
    app = create_app(runtime_factory=controlled)
    with TestClient(app) as client:
        assert client.get("/api/v1/flagship").status_code == 200
        controlled.now += (app.state.system.settings.stale_age_ms + 1) * 1_000_000
        assert client.get("/api/v1/flagship").status_code == 503


def test_endpoint_denies_access_when_server_token_is_unconfigured(tmp_path, monkeypatch):
    from app.main import DeploymentConfig, create_app
    from runtime_fixtures import ControlledRuntime
    monkeypatch.setenv("TARK_DATABASE_PATH", str(tmp_path / "events.db"))
    app = create_app(deployment=DeploymentConfig(auth_mode="authenticated", access_token=""),
                     runtime_factory=ControlledRuntime())
    with TestClient(app) as client:
        assert client.get("/api/v1/flagship").status_code == 503
