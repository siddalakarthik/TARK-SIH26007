from pathlib import Path

ROOT=Path(__file__).parents[2]

def test_frontend_uses_same_origin_and_has_no_localhost_production_dependency():
    source=(ROOT/"frontend"/"src"/"api.ts").read_text(encoding="utf-8")
    assert "request('/api/v1/status')" in source
    assert "locationLike.host" in source
    for forbidden in ("localhost", "127.0.0.1", ":8000", "ws://localhost", "http://localhost"):
        assert forbidden not in source

def test_public_port_and_deployment_profiles_are_environment_driven():
    source=(ROOT/"backend"/"app"/"main.py").read_text(encoding="utf-8")
    assert 'os.getenv("PORT", "8000")' in source
    assert "public_demo" in source and "public_hardware" in source
    assert 'socket.query_params.get("access_token"' not in source

def test_render_blueprint_explicitly_requests_free_simulation_only_demo():
    blueprint=(ROOT/"render.yaml").read_text(encoding="utf-8")
    assert "runtime: docker" in blueprint
    assert "plan: free" in blueprint
    assert "healthCheckPath: /ready" in blueprint
    assert "key: TARK_ENV\n        value: public_demo" in blueprint
    assert "key: TARK_AUTH_MODE\n        value: public_demo" in blueprint

def test_map_uses_openfreemap_and_keeps_radar_in_a_local_frame():
    source=(ROOT/"frontend"/"src"/"MapView.tsx").read_text(encoding="utf-8")
    config=(ROOT/"frontend"/"src"/"mapConfig.ts").read_text(encoding="utf-8")
    assert "https://tiles.openfreemap.org/styles/liberty" in config
    assert "RADAR LOCAL FRAME" in source
    assert "INDIA_VIEW" in source and "Locate me" in source and "watchPosition" in source
    assert "clearWatch" in source
    assert "coordinates:[t.y_m,t.x_m]" not in source

def test_csp_allows_map_assets_without_opening_script_execution():
    source=(ROOT/"backend"/"app"/"main.py").read_text(encoding="utf-8")
    assert "img-src 'self' data: blob: https:" in source
    assert "script-src 'self'" in source
