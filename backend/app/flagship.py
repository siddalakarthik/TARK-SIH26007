"""Read-only flagship presentation contract; no device or decision authority.

The two-participant course is a deterministic SOFTWARE DEMONSTRATION, not a
second location pipeline. Its geometry is never ingested into TarkSystem and
must not be spatially associated with the existing radar/safety simulation.
Actual decision evidence remains in /api/v1/status. New BOM selections do not
automatically inherit verification from older device drivers.
"""
from __future__ import annotations

from math import atan2, cos, degrees, hypot, radians


SCHEMA_VERSION = "tark.flagship.v1"
CENTER = (78.4867, 17.385)  # Display anchor ONLY; not a mine or measured site.
COURSE_XY = ((-48., -26.), (24., -26.), (48., -8.), (48., 26.),
             (-24., 26.), (-48., 8.), (-48., -26.))
HISTORY_LIMIT = 61


def _coordinate(x: float, y: float) -> list[float]:
    return [round(CENTER[0] + x / (111_320 * cos(radians(CENTER[1]))), 8),
            round(CENTER[1] + y / 111_320, 8)]


def _point_along(distance_m: float) -> tuple[list[float], float]:
    segments = [(a, b, hypot(b[0] - a[0], b[1] - a[1]))
                for a, b in zip(COURSE_XY, COURSE_XY[1:])]
    distance_m %= sum(segment[2] for segment in segments)
    for a, b, length in segments:
        if distance_m <= length:
            fraction = distance_m / length
            course = degrees(atan2(b[0] - a[0], b[1] - a[1])) % 360
            return _coordinate(a[0] + fraction * (b[0] - a[0]),
                               a[1] + fraction * (b[1] - a[1])), round(course, 2)
        distance_m -= length
    raise AssertionError("closed course must contain the bounded distance")


def _feature(identifier: str, label: str, geometry_type: str, coordinates: list,
             **properties: object) -> dict:
    return {"type": "Feature", "id": identifier,
            "properties": {"id": identifier, "label": label,
                           "source_mode": "SIMULATION", "operational_authority": False,
                           **properties},
            "geometry": {"type": geometry_type, "coordinates": coordinates}}


def _collection(*features: dict) -> dict:
    return {"type": "FeatureCollection", "features": list(features)}


def _scene(sequence: int, enabled: bool) -> dict:
    scene = {"id": "demo-course-v1", "label": "Synthetic test course · SIMULATION · not surveyed",
             "source": "SIMULATION" if enabled else "UNAVAILABLE",
             "coordinate_system": "WGS84_DISPLAY_ANCHOR_ONLY",
             "center": list(CENTER) if enabled else [78.9629, 20.5937],
             "bounds": [*_coordinate(-80, -55), *_coordinate(80, 55)] if enabled else [68., 6., 98., 36.],
             "review_status": "DEMO_FIXTURE_NOT_SURVEYED",
             "roads": _collection(), "route": _collection(), "zones": _collection(),
             "waypoints": _collection(), "hazards": _collection(), "history": _collection()}
    if not enabled:
        scene["id"] = "unavailable-course"
        scene["review_status"] = "UNAVAILABLE_NOT_SURVEYED"
        scene["label"] = "India overview · no flagship participant location available"
        return scene
    road = [_coordinate(x, y) for x, y in COURSE_XY]
    scene["roads"] = _collection(_feature("road-loop", "Demonstration course", "LineString", road))
    scene["route"] = _collection(_feature("route-loop", "Assigned demo route · not a surveyed road",
                                         "LineString", road))
    scene["zones"] = _collection(_feature("exclusion", "Synthetic exclusion zone", "Polygon",
        [[_coordinate(-16, -9), _coordinate(16, -9), _coordinate(16, 9),
          _coordinate(-16, 9), _coordinate(-16, -9)]], kind="exclusion"))
    scene["waypoints"] = _collection(
        _feature("station-start", "Start / loading point", "Point", _coordinate(-48, -26)),
        _feature("station-hold", "Holding area", "Point", _coordinate(48, 26)),
        _feature("station-return", "Return point", "Point", _coordinate(-48, 8)))
    scene["hazards"] = _collection(_feature("obstacle-fixture", "Synthetic inert obstacle",
        "Point", _coordinate(28, 15), kind="TEST_FIXTURE", observation_source="SIMULATION",
        note="Display fixture only; not an input to the core safety decision"))
    for participant_id, speed, offset in (("A", .8, 0.), ("B", .55, 122.)):
        # Bounded trace, derived from sequence rather than mutated by API reads.
        steps = range(max(0, sequence - (HISTORY_LIMIT - 1) * 4), sequence + 1, 4)
        coordinates = [_point_along(step * .25 * speed + offset)[0] for step in steps]
        current = _point_along(sequence * .25 * speed + offset)[0]
        if coordinates[-1] != current:
            coordinates.append(current)
        coordinates = coordinates[-HISTORY_LIMIT:]
        if len(coordinates) < 2:
            coordinates = coordinates * 2
        scene["history"]["features"].append(_feature(f"history-{participant_id}",
            f"{participant_id} simulated history", "LineString", coordinates, participant_id=participant_id))
    return scene


def _hardware() -> list[dict]:
    selections = (
        ("compute", "Raspberry Pi 5 + Hailo-8 AI HAT+ 26 TOPS", "Local inference", "MIGRATION_REQUIRED",
         "R3 inference-provider boundary implemented; released HEF/model pipeline and Pi profiling still required. No accelerator verification."),
        ("radar", "TI IWR6843ISK", "Documented processed-radar output", "MIGRATION_REQUIRED",
         "R3 Cartesian TLV payload decoder implemented; exact TI firmware/frame profile remains required. LD2450 is a separate legacy driver."),
        ("rgb", "Arducam B0200 IMX291", "UVC", "EXISTING_BOUNDARY_REVIEW_REQUIRED",
         "Existing UVC acquisition boundary; selected camera profile, timestamps and identity require review."),
        ("thermal", "Lepton 3.5 + PureThermal 3", "USB video / device metadata", "MIGRATION_REQUIRED",
         "R3 Lepton frame/FFC/radiometry contract implemented; PureThermal mode binding remains unverified. MLX90640 is not interchangeable."),
        ("gnss", "Waveshare LG290P × 3 (A, B, base)", "GNSS observations + correction relay", "EXISTING_BOUNDARY_REVIEW_REQUIRED",
         "Existing normalized GNSS boundary; LG290P integration, base/rover corrections and peer transport still require verification."),
        ("imu", "BNO085", "SPI via measurement MCU", "MIGRATION_REQUIRED",
         "R3 SH-2 report decoder and clock qualification implemented; SHTP/SPI platform binding and measured time alignment remain pending. BNO055 is different."),
        ("wheels", "AMT102-V × 2", "Quadrature measurement wheels", "MIGRATION_REQUIRED",
         "R3 encoder observation codec and Python/C vectors implemented; physical counters, scale calibration and slip/disagreement commissioning pending. Not ground-truth speed."),
        ("mcu", "ESP32-S3-DevKitC-1-N8 × 2", "Timestamped observations / peer bridge", "EXISTING_BOUNDARY_REVIEW_REQUIRED",
         "R3 observation message uses the existing session/COBS/CRC32C/CBOR codec. Software fixtures do not establish physical USB/Wi-Fi verification."),
        ("hmi", "Waveshare 7-inch HDMI LCD (C)", "Browser via HDMI", "EXISTING_BOUNDARY_REVIEW_REQUIRED",
         "Application display exists; physical screen ergonomics and local-browser setup remain hardware pending."),
    )
    return [{"id": identifier, "name": name, "interface": interface,
             "status": "HARDWARE_PENDING", "software_readiness": readiness, "reason": reason}
            for identifier, name, interface, readiness, reason in selections]


def flagship_snapshot(mode: str, snapshot: dict, now_ns: int) -> dict:
    """Project cached runtime metadata into a finite, bounded display contract.

    Only exact configured simulation mode enables synthetic geometry. Unknown,
    replay and hardware modes fail closed. No I/O, clocks, global mutable state,
    system.tick calls, device probes, safety calculations or actuation occur.
    """
    enabled = mode == "simulation"
    sequence = snapshot["command"]["sequence"]
    timestamp_ns = snapshot["timestamp_ns"]
    if any(type(value) is not int for value in (sequence, timestamp_ns, now_ns)):
        raise ValueError("invalid runtime observation metadata")
    if sequence < 0 or timestamp_ns < 0 or now_ns < timestamp_ns:
        raise ValueError("invalid runtime observation metadata")
    participants = []
    for identifier, name, role, speed, offset, capabilities in (
        ("A", "Vehicle A", "INSTRUMENTED_VEHICLE", .8, 0.,
         ["RGB", "THERMAL", "RADAR", "GNSS", "IMU", "WHEEL_RESPONSE", "DRIVER_HMI"]),
        ("B", "Cooperative node B", "LOCATION_ONLY", .55, 122., ["GNSS", "PEER_TELEMETRY"]),
    ):
        point, course = _point_along(sequence * .25 * speed + offset) if enabled else (None, None)
        participants.append({"id": identifier, "name": name, "role": role,
            "source_mode": "SIMULATION" if enabled else "UNAVAILABLE",
            "state": "SIMULATED" if enabled else "UNAVAILABLE",
            "position": {"longitude_deg": point[0], "latitude_deg": point[1]} if point else None,
            "speed_mps": speed if enabled else None, "course_deg": course,
            "heading_deg": None, "accuracy_m": 3.0 if enabled else None,
            "age_ms": round((now_ns - timestamp_ns) / 1_000_000, 3) if enabled else None,
            "timestamp_ns": timestamp_ns if enabled else None,
            "quality": "SIMULATED_FIX" if enabled else "NOT_CONNECTED",
            "capabilities": capabilities})
    return {"schema_version": SCHEMA_VERSION, "mode": mode.upper(),
            "source_mode": "SIMULATION" if enabled else "UNAVAILABLE",
            "timestamp_ns": timestamp_ns, "sequence": sequence,
            "traction": "DISABLED_PHASE_1", "monitoring_only": True, "hardware_verified": False,
            "decision_source": "/api/v1/status", "scene": _scene(sequence, enabled),
            "participants": participants, "hardware": _hardware(),
            "limitations": [
                "Fleet scene is an independent software fixture, not acquired GNSS or synchronized core radar evidence.",
                "No surveyed mine map, operational route approval or real peer discovery is claimed.",
                "Node B is location-only; it has no camera, radar, IMU or independent safety decision.",
                "Capabilities describe the selected design, not connected or verified hardware.",
                "No automatic steering, propulsion or braking; the browser is monitoring-only.",
                "New flagship device integration remains gated; selecting hardware is not a working device driver.",
            ]}
