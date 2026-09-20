from __future__ import annotations

import argparse
import asyncio
import hmac
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from app.config import Settings
from app.services.system import TarkSystem
from app.replay.engine import ReplayConfigurationError, ReplayFormatError, replay_recording, replay_timeline
from app.replay.store import RecordingError
from app.location import (DisabledReverseGeocoder, DisabledRouteProvider, NominatimReverseGeocoder,
                          OSRMRouteProvider, ProviderUnavailable, ReverseGeocodeRequest,
                          RouteRequest, validated_provider_url)

ROOT = Path(__file__).parents[2]
SESSION_COOKIE = "tark_session"


def map_display_config() -> dict:
    """Display-only map metadata; India overview is never a vehicle location."""
    raw_center = os.getenv("TARK_DEFAULT_MAP_CENTER", "").strip()
    raw_zoom = os.getenv("TARK_DEFAULT_MAP_ZOOM", "4.2").strip()
    try:
        zoom = float(raw_zoom)
        if not 0 <= zoom <= 22:
            raise ValueError
    except ValueError:
        zoom = 4.2
    try:
        longitude_text, latitude_text = raw_center.split(",", maxsplit=1)
        longitude, latitude = float(longitude_text), float(latitude_text)
        if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
            raise ValueError
        return {"longitude": longitude, "latitude": latitude, "zoom": zoom, "location_configured": True, "location_status": "CONFIGURED_DISPLAY_CENTER", "view_mode": "CONFIGURED_LOCATION"}
    except ValueError:
        # India overview deliberately supplies context only. It is not a mine,
        # TARK vehicle, radar or browser-device location.
        return {"longitude": 78.9629, "latitude": 20.5937, "zoom": 4.2, "location_configured": False, "location_status": "INDIA_OVERVIEW_NO_VEHICLE_LOCATION", "view_mode": "INDIA_OVERVIEW"}


@dataclass(frozen=True)
class DeploymentConfig:
    environment: str = "development"
    auth_mode: str = "public_demo"
    access_token: str = ""
    cors_origins: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.environment not in {"development", "edge", "public_demo", "public_hardware"}:
            raise ValueError("TARK_ENV must be development, edge, public_demo, or public_hardware")
        if self.auth_mode not in {"public_demo", "authenticated"}:
            raise ValueError("TARK_AUTH_MODE must be public_demo or authenticated")
        if self.environment == "public_demo" and self.auth_mode != "public_demo":
            raise ValueError("public_demo deployments must use public_demo authentication mode")
        if self.environment == "public_hardware" and self.auth_mode != "authenticated":
            raise ValueError("public_hardware deployments must use authenticated mode")
        for origin in self.cors_origins:
            parsed = urlsplit(origin)
            if origin == "*" or parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
                raise ValueError("TARK_CORS_ORIGINS must contain explicit http(s) origins without paths")

    @classmethod
    def from_environment(cls) -> "DeploymentConfig":
        environment = os.getenv("TARK_ENV", "development").lower()
        auth_mode = os.getenv("TARK_AUTH_MODE", "public_demo").lower()
        origins = tuple(origin.strip() for origin in os.getenv("TARK_CORS_ORIGINS", "").split(",") if origin.strip())
        return cls(environment, auth_mode, os.getenv("TARK_ACCESS_TOKEN", ""), origins)


def create_app(settings: Settings | None = None, deployment: DeploymentConfig | None = None) -> FastAPI:
    settings = settings or Settings.from_file(ROOT / "config" / "phase1.json")
    deployment = deployment or DeploymentConfig.from_environment()
    if deployment.environment == "public_demo" and settings.mode != "simulation":
        raise ValueError("public_demo deployments must use simulation mode")
    system = TarkSystem(settings)
    browser_camera_enabled = os.getenv("TARK_ENABLE_BROWSER_CAMERA", "").strip().lower() in {"1", "true", "yes"}
    reverse_url = os.getenv("TARK_REVERSE_GEOCODER_URL", "").strip()
    route_url = os.getenv("TARK_ROUTE_PROVIDER_URL", "").strip()
    reverse_geocoder = NominatimReverseGeocoder(validated_provider_url(reverse_url)) if reverse_url else DisabledReverseGeocoder()
    route_provider = OSRMRouteProvider(validated_provider_url(route_url)) if route_url else DisabledRouteProvider()
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        system.close()

    app = FastAPI(title="TARK Phase 1 Backend", version="0.3.0", lifespan=lifespan)
    app.state.system, app.state.deployment = system, deployment
    app.state.reverse_geocoder, app.state.route_provider = reverse_geocoder, route_provider

    @app.middleware("http")
    async def set_security_headers(request: Request, call_next):
        response = await call_next(request)
        connect_sources = "'self' https: wss:" if deployment.environment in {"public_demo", "public_hardware"} else "'self' https: wss: ws:"
        # MapLibre may load a remote style sprite/tile image.  HTTPS imagery is
        # display-only; safety/command traffic remains same-origin.
        response.headers.setdefault("Content-Security-Policy", f"default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; connect-src {connect_sources}; worker-src 'self' blob:; form-action 'self'")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        # Device location is request-only and remains local to this browser.
        # Camera stays disabled unless an operator explicitly enables the
        # isolated development-only preview capability.
        response.headers.setdefault("Permissions-Policy", f"camera={'(self)' if browser_camera_enabled else '()'}, microphone=(), geolocation=(self)")
        return response

    if deployment.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=list(deployment.cors_origins), allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

    def require_access(request: Request, authorization: str | None = Header(default=None)) -> None:
        if deployment.auth_mode == "public_demo":
            return
        if not deployment.access_token:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authenticated mode has no server access token configured")
        supplied = request.cookies.get(SESSION_COOKIE, "")
        if authorization and authorization.startswith("Bearer "):
            supplied = authorization.removeprefix("Bearer ").strip()
        if not hmac.compare_digest(supplied, deployment.access_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ready", "mode": settings.mode, "environment": deployment.environment, "configuration_hash": settings.configuration_hash, "traction": "DISABLED_PHASE_1", "hardware": "NOT_CONNECTED_PHASE_2", "frontend": "served_when_built"}

    @app.get("/ready")
    def ready() -> dict:
        return {"ready": True, "mode": settings.mode, "traction": "DISABLED_PHASE_1", "hardware": "NOT_CONNECTED_PHASE_2"}

    @app.post("/api/v1/auth/session", status_code=status.HTTP_204_NO_CONTENT)
    def create_session(request: Request, authorization: str | None = Header(default=None)) -> Response:
        if deployment.auth_mode != "authenticated":
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        if not deployment.access_token or not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        supplied = authorization.removeprefix("Bearer ").strip()
        if not hmac.compare_digest(supplied, deployment.access_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response.set_cookie(SESSION_COOKIE, deployment.access_token, httponly=True, secure=request.url.scheme == "https" or deployment.environment in {"public_demo", "public_hardware"}, samesite="strict", max_age=8 * 60 * 60, path="/")
        return response

    @app.get("/api/v1/status", dependencies=[Depends(require_access)])
    def system_status() -> dict: return system.tick()

    @app.get("/api/v1/tracks", dependencies=[Depends(require_access)])
    def tracks() -> list[dict]: return system.tick()["tracks"]

    @app.get("/api/v1/sensors", dependencies=[Depends(require_access)])
    def sensors() -> list[dict]: return system.tick()["sensors"]

    @app.get("/api/v1/events", dependencies=[Depends(require_access)])
    def events() -> list[dict]:
        system.tick()
        return system.persisted_events()

    @app.get("/api/v1/diagnostics", dependencies=[Depends(require_access)])
    def diagnostics() -> dict:
        return {"software_version": "0.3.0", "firmware_version": "0.1.0", "protocol_version": 1, "configuration_hash": settings.configuration_hash, "mode": settings.mode.upper(), "phase_2_hardware": "NOT_CONNECTED", "deployment_environment": deployment.environment, "auth_mode": deployment.auth_mode, "map": map_display_config(), "capabilities": {"browser_device_location": True, "browser_camera_preview": browser_camera_enabled, "reverse_geocoding": bool(reverse_url), "routing": bool(route_url)}}

    @app.get("/api/v1/vehicle-location", dependencies=[Depends(require_access)])
    def vehicle_location() -> dict:
        return system.vehicle_location()

    @app.post("/api/v1/location/reverse", dependencies=[Depends(require_access)])
    def reverse_geocode(request: ReverseGeocodeRequest) -> dict:
        # This endpoint persists nothing. The browser calls it only after a user
        # explicitly chooses to resolve its own already-displayed location.
        try:
            return app.state.reverse_geocoder.reverse(request).model_dump()
        except ProviderUnavailable as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    @app.post("/api/v1/routes", dependencies=[Depends(require_access)])
    def calculate_route(request: RouteRequest) -> dict:
        try:
            return app.state.route_provider.route(request).model_dump()
        except ProviderUnavailable as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    @app.get("/api/v1/cameras/vehicle-rgb", dependencies=[Depends(require_access)])
    def vehicle_camera_status() -> dict:
        frame = system.camera.read_frame(time.monotonic_ns())
        metadata = frame.metadata.__dict__.copy()
        metadata["stream_url"] = "/api/v1/cameras/vehicle-rgb/stream" if system.camera.stream_available(time.monotonic_ns()) else None
        metadata["stream_transport"] = "MJPEG" if metadata["stream_url"] else "PENDING_PI_UVC_INTEGRATION"
        metadata["hardware_claim"] = "REAL_PI_UVC" if frame.metadata.source_mode == "PI_UVC" and frame.metadata.state == "ONLINE" else "NOT_CONNECTED"
        return metadata

    @app.get("/api/v1/cameras/vehicle-rgb/capabilities", dependencies=[Depends(require_access)])
    def vehicle_camera_capabilities() -> dict:
        return {"state": system.camera.discover()["state"], "candidates": system.camera.discover()["candidates"], "preferred_profile": {"width":system.camera.config.preferred_width,"height":system.camera.config.preferred_height,"fps":system.camera.config.preferred_fps}, "identity":"UNVERIFIED"}

    @app.get("/api/v1/imu", dependencies=[Depends(require_access)])
    def imu_status() -> dict:
        sample=system.imu.read_sample(time.monotonic_ns())
        return {**sample.__dict__,"diagnostics":system.imu.discover()}

    @app.get("/api/v1/thermal", dependencies=[Depends(require_access)])
    def thermal_status() -> dict:
        frame=system.thermal.read_frame(time.monotonic_ns())
        return {**frame.__dict__,"minimum_temperature_c":min(frame.temperatures_c) if frame.temperatures_c else None,"maximum_temperature_c":max(frame.temperatures_c) if frame.temperatures_c else None,"average_temperature_c":sum(frame.temperatures_c)/len(frame.temperatures_c) if frame.temperatures_c else None,"diagnostics":system.thermal.discover()}

    @app.get("/api/v1/cameras/vehicle-rgb/stream", dependencies=[Depends(require_access)])
    def vehicle_camera_stream():
        if not system.camera.stream_available(time.monotonic_ns()):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="CAMERA NOT CONNECTED")
        def stream():
            interval=1/max(1.0,system.camera.config.stream_fps)
            while True:
                frame=system.camera.latest_jpeg(time.monotonic_ns())
                if frame: yield b"--tarkframe\r\nContent-Type: image/jpeg\r\nContent-Length: "+str(len(frame)).encode()+b"\r\n\r\n"+frame+b"\r\n"
                time.sleep(interval)
        return StreamingResponse(stream(),media_type="multipart/x-mixed-replace; boundary=tarkframe",headers={"Cache-Control":"no-store"})

    def recording_error(error: RecordingError) -> HTTPException:
        code=status.HTTP_404_NOT_FOUND if "not found" in str(error) else status.HTTP_409_CONFLICT
        return HTTPException(code, str(error))

    @app.get("/api/v1/runs", dependencies=[Depends(require_access)])
    def runs() -> list[dict]:
        """Observation recordings only; an empty array means no recording exists."""
        return system.recording_sessions()

    @app.post("/api/v1/recordings/start", dependencies=[Depends(require_access)])
    def start_recording() -> dict:
        try: return system.start_recording()
        except (RecordingError, ValueError) as error: raise recording_error(RecordingError(str(error))) from error

    @app.post("/api/v1/recordings/stop", dependencies=[Depends(require_access)])
    def stop_recording() -> dict:
        try: return system.stop_recording()
        except RecordingError as error: raise recording_error(error) from error

    @app.get("/api/v1/replay/sessions", dependencies=[Depends(require_access)])
    def replay_sessions() -> list[dict]: return system.recording_sessions()

    @app.get("/api/v1/replay/sessions/{session_id}", dependencies=[Depends(require_access)])
    def replay_session(session_id: str) -> dict:
        try: return system.recording_session(session_id)
        except RecordingError as error: raise recording_error(error) from error

    @app.get("/api/v1/replay/sessions/{session_id}/records", dependencies=[Depends(require_access)])
    def replay_records(session_id: str, limit: int = 1_000) -> list[dict]:
        try: return system.recording_records(session_id, limit)
        except RecordingError as error: raise recording_error(error) from error

    @app.get("/api/v1/replay/sessions/{session_id}/timeline", dependencies=[Depends(require_access)])
    def replay_timeline_endpoint(session_id: str) -> dict:
        try:
            session=system.recording_session(session_id)
            return replay_timeline(system.recording_records(session_id,10_000),session,settings.configuration_hash)
        except RecordingError as error: raise recording_error(error) from error
        except ReplayConfigurationError as error: raise HTTPException(status.HTTP_409_CONFLICT,str(error)) from error
        except ReplayFormatError as error: raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,str(error)) from error

    @app.post("/api/v1/replay/sessions/{session_id}/verify", dependencies=[Depends(require_access)])
    def verify_replay(session_id: str) -> dict:
        try:
            session=system.recording_session(session_id)
            if session["configuration_hash"] != settings.configuration_hash:
                raise ReplayConfigurationError("recording configuration hash is incompatible with active configuration")
            result=replay_recording(system.recording_records(session_id,10_000),settings)
            return {"session_id":session_id,"result":result.result,"first_divergence":result.first_divergence,"replayed_decisions":result.decisions}
        except RecordingError as error: raise recording_error(error) from error
        except ReplayConfigurationError as error: raise HTTPException(status.HTTP_409_CONFLICT,str(error)) from error
        except ReplayFormatError as error: raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,str(error)) from error

    @app.websocket("/api/v1/ws")
    async def websocket_status(socket: WebSocket) -> None:
        if deployment.auth_mode == "authenticated":
            # Browser sessions use the HttpOnly same-site cookie. Do not accept a
            # credential in a WebSocket URL, which could leak through history/logs.
            supplied = socket.cookies.get(SESSION_COOKIE, "")
            if not deployment.access_token or not hmac.compare_digest(supplied, deployment.access_token):
                await socket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        await socket.accept()
        try:
            while True:
                now = time.monotonic_ns()
                snapshot=system.tick(now)
                await socket.send_json({"schema_version": 1, "type": "status", "server_time_ns": now, "configuration_hash": settings.configuration_hash, "payload": snapshot})
                await socket.send_json({"schema_version": 1, "type": "location_update", "server_time_ns": now, "configuration_hash": settings.configuration_hash, "payload": snapshot["vehicle_location"]})
                try:
                    message = await asyncio.wait_for(socket.receive_json(), timeout=0.25)
                    code = "MALFORMED_OBSERVATION_MESSAGE" if not isinstance(message, dict) else (None if message.get("type") in {"ping", "subscribe", "unsubscribe", "replay_control"} else "UNSUPPORTED_OBSERVATION_MESSAGE")
                    if code:
                        await socket.send_json({"schema_version": 1, "type": "error", "server_time_ns": time.monotonic_ns(), "configuration_hash": settings.configuration_hash, "payload": {"code": code}})
                except TimeoutError: pass
                except (TypeError, ValueError):
                    await socket.send_json({"schema_version": 1, "type": "error", "server_time_ns": time.monotonic_ns(), "configuration_hash": settings.configuration_hash, "payload": {"code": "MALFORMED_OBSERVATION_MESSAGE"}})
        except WebSocketDisconnect: return

    frontend = ROOT / "frontend" / "dist"
    if frontend.exists(): app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    parser = argparse.ArgumentParser(); parser.add_argument("--mode", choices=("simulation", "replay", "real_radar")); args=parser.parse_args()
    runtime_settings=Settings.from_file(ROOT / "config" / "phase1.json")
    if args.mode is not None: runtime_settings=runtime_settings.model_copy(update={"mode":args.mode})
    uvicorn.run(create_app(settings=runtime_settings), host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
