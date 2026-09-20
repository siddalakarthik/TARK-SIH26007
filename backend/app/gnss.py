"""GNSS-only location pipeline.  This module has no controller or motor imports."""
from __future__ import annotations

import math
import os
import time
from datetime import datetime, timezone
from collections import deque
from dataclasses import asdict, dataclass
from typing import Literal
from app.sensor_identity import DeviceIdentity

Source = Literal["GNSS", "SIMULATION", "REPLAY", "UNKNOWN"]
Status = Literal["NO_RECEIVER", "SEARCHING", "NO_FIX", "2D_FIX", "3D_FIX", "STALE", "ERROR", "ONLINE"]

@dataclass(frozen=True)
class GnssFix:
    vehicle_id: str
    timestamp_ns: int
    source: Source
    latitude_deg: float | None
    longitude_deg: float | None
    altitude_m: float | None = None
    speed_mps: float | None = None
    heading_deg: float | None = None
    horizontal_accuracy_m: float | None = None
    vertical_accuracy_m: float | None = None
    fix_type: str = "UNKNOWN"
    satellites: int | None = None
    freshness_ms: float | None = None
    quality: str = "UNKNOWN"
    status: Status = "NO_FIX"
    # Receiver UTC is optional and never substituted with the local monotonic
    # receipt timestamp. timestamp_ns remains the backwards-compatible alias
    # for received_monotonic_ns used by existing consumers.
    measurement_time_utc: str | None = None
    received_monotonic_ns: int | None = None

    def payload(self, now_ns: int) -> dict:
        value = asdict(self)
        received = self.received_monotonic_ns if self.received_monotonic_ns is not None else self.timestamp_ns
        value["received_monotonic_ns"] = received
        value["freshness_ms"] = max(0.0, (now_ns - received) / 1_000_000)
        return value

@dataclass(frozen=True)
class GnssConfig:
    device_path: str = ""
    baud: int = 115200
    freshness_ms: int = 3000
    maximum_speed_mps: float = 55.0
    maximum_jump_m: float = 150.0
    minimum_satellites: int = 4
    maximum_accuracy_m: float = 100.0
    breadcrumb_limit: int = 300
    serial_timeout_s: float = .5
    reconnect_interval_s: float = .5
    raw_log_enabled: bool = False
    raw_log_path: str = ""
    max_line_bytes: int = 1024

    @classmethod
    def from_environment(cls) -> "GnssConfig":
        def number(name: str, default: float) -> float:
            try: return float(os.getenv(name, str(default)))
            except ValueError: return default
        return cls(os.getenv("TARK_GNSS_DEVICE_PATH", "").strip(), int(number("TARK_GNSS_BAUD", 115200)), int(number("TARK_GNSS_FRESHNESS_MS", 3000)), number("TARK_GNSS_MAX_SPEED_MPS", 55), number("TARK_GNSS_MAX_JUMP_M", 150), int(number("TARK_GNSS_MIN_SATELLITES", 4)), number("TARK_GNSS_MAX_ACCURACY_M", 100), int(number("TARK_GNSS_BREADCRUMB_LIMIT", 300)), number("TARK_GNSS_SERIAL_TIMEOUT_S", .5), number("TARK_GNSS_RECONNECT_INTERVAL_S", .5), os.getenv("TARK_GNSS_RAW_LOG_ENABLED", "false").lower() in {"1","true","yes"}, os.getenv("TARK_GNSS_RAW_LOG_PATH", "").strip(), int(number("TARK_GNSS_MAX_LINE_BYTES", 1024)))

def _decimal(value: str, hemisphere: str) -> float | None:
    if not value or hemisphere not in {"N", "S", "E", "W"}: return None
    try:
        degrees = 2 if hemisphere in {"N", "S"} else 3
        whole, minutes = value[:degrees], float(value[degrees:])
        if len(whole) != degrees or not 0 <= minutes < 60: return None
        answer = int(whole) + minutes / 60
        if answer > (90 if hemisphere in {"N", "S"} else 180): return None
        return -answer if hemisphere in {"S", "W"} else answer
    except ValueError: return None

def _rmc_utc(clock: str, date: str) -> str | None:
    """NMEA RMC UTC/date, when both fields are actually present."""
    if not clock or not date: return None
    try:
        whole, _, fraction = clock.partition(".")
        stamp = datetime.strptime(date + whole, "%d%m%y%H%M%S").replace(tzinfo=timezone.utc)
        return stamp.isoformat().replace("+00:00", "Z") if not fraction else stamp.isoformat().replace("+00:00", "Z")
    except ValueError: return None

def parse_nmea(line: bytes | str, now_ns: int | None = None, vehicle_id: str = "TARK-001") -> GnssFix | None:
    """Accept RMC/GGA sentences; reject malformed/unchecked data without crashing."""
    try: text = bytes(line).decode("ascii", "strict") if isinstance(line, (bytes, bytearray)) else line
    except UnicodeDecodeError: return None
    text = text.strip()
    if not text.startswith("$") or "*" not in text: return None
    body, checksum = text[1:].split("*", 1)
    try:
        if len(checksum) != 2 or int(checksum, 16) != (lambda v: __import__('functools').reduce(lambda a,b:a^ord(b),v,0))(body): return None
    except ValueError: return None
    fields = body.split(","); kind = fields[0][-3:]; now = now_ns or time.monotonic_ns()
    if kind == "RMC" and len(fields) >= 9:
        latitude, longitude = _decimal(fields[3], fields[4]), _decimal(fields[5], fields[6])
        measurement=_rmc_utc(fields[1], fields[9] if len(fields)>9 else "")
        if fields[2] != "A": return GnssFix(vehicle_id, now, "GNSS", None, None, status="NO_FIX", quality="NO_FIX",measurement_time_utc=measurement,received_monotonic_ns=now)
        if latitude is None or longitude is None: return None
        try: speed = float(fields[7]) * 0.514444 if fields[7] else None; heading = float(fields[8]) if fields[8] else None
        except ValueError: return None
        return GnssFix(vehicle_id, now, "GNSS", latitude, longitude, speed_mps=speed, heading_deg=heading, fix_type="UNKNOWN", quality="RMC_VALID", status="ONLINE",measurement_time_utc=measurement,received_monotonic_ns=now)
    if kind == "GGA" and len(fields) >= 10:
        latitude, longitude = _decimal(fields[2], fields[3]), _decimal(fields[4], fields[5]); quality = fields[6]
        if quality in {"", "0"}: return GnssFix(vehicle_id, now, "GNSS", None, None, status="NO_FIX", quality="NO_FIX",received_monotonic_ns=now)
        if latitude is None or longitude is None: return None
        try: satellites=int(fields[7]) if fields[7] else None; altitude=float(fields[9]) if fields[9] else None
        except ValueError: return None
        # GGA's quality code establishes that a fix exists, but does not itself
        # establish 2D versus 3D. Altitude presence is not dimensional proof.
        return GnssFix(vehicle_id, now, "GNSS", latitude, longitude, altitude_m=altitude, satellites=satellites, fix_type="UNKNOWN", quality=f"GGA_QUALITY_{quality}", status="ONLINE",received_monotonic_ns=now)
    if kind == "GSA" and len(fields) >= 3:
        # GSA is standard NMEA. Its mode field, not altitude, establishes 2D/3D.
        state = {"1": "NO_FIX", "2": "2D_FIX", "3": "3D_FIX"}.get(fields[2])
        if state is None: return None
        return GnssFix(vehicle_id, now, "GNSS", None, None, fix_type=state, quality=f"GSA_MODE_{fields[2]}", status=state, received_monotonic_ns=now)
    return None

def distance_m(a: GnssFix, b: GnssFix) -> float:
    if None in {a.latitude_deg, a.longitude_deg, b.latitude_deg, b.longitude_deg}: return math.inf
    radius=6_371_000; lat1,lat2=math.radians(a.latitude_deg),math.radians(b.latitude_deg); dlat=lat2-lat1; dlon=math.radians(b.longitude_deg-a.longitude_deg)
    return 2*radius*math.asin(math.sqrt(math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2))

class GnssLocationService:
    def __init__(self, config: GnssConfig | None = None):
        self.config=config or GnssConfig.from_environment();self.identity=DeviceIdentity("SERIAL",self.config.device_path or "UNSET",state="UNVERIFIED",evidence_source="CONFIGURATION_ONLY"); self.state: Status="NO_RECEIVER"; self.reason="LC29H(AA) NOT CONNECTED"; self.last: GnssFix|None=None; self.trail: deque[dict]=deque(maxlen=self.config.breadcrumb_limit)
    def discover(self) -> dict:
        if not self.config.device_path: self.state="NO_RECEIVER"; self.reason="GNSS DEVICE PATH NOT CONFIGURED"; return {"state":self.state,"candidates":[]}
        self.state="SEARCHING"; self.reason="CONFIGURED DEVICE NOT YET VERIFIED"; return {"state":self.state,"candidates":[{"path":self.config.device_path,"identity":self.identity.state}]}
    def record_verified_identity(self,evidence_source:str,**facts:str|None)->None:self.identity=DeviceIdentity(**{**self.identity.__dict__,**facts}).verified(evidence_source)
    def accept(self, fix: GnssFix, now_ns: int | None = None) -> bool:
        now=now_ns or time.monotonic_ns()
        if fix.status == "NO_FIX" or fix.fix_type == "NO_FIX":
            self.state, self.reason = "NO_FIX", "RECEIVER REPORTS NO FIX"
            return False
        if fix.latitude_deg is None or fix.longitude_deg is None:
            if fix.fix_type in {"2D_FIX", "3D_FIX"}: self.state, self.reason = fix.fix_type, "RECEIVER FIX MODE; COORDINATES AWAITED"
            else: self.state, self.reason = "NO_FIX", "GNSS COORDINATES UNAVAILABLE"
            return False
        if not (-90<=fix.latitude_deg<=90 and -180<=fix.longitude_deg<=180): self.state="ERROR";self.reason="INVALID GNSS COORDINATE";return False
        if fix.speed_mps is not None and (fix.speed_mps<0 or fix.speed_mps>self.config.maximum_speed_mps): self.state="ERROR";self.reason="IMPLAUSIBLE GNSS SPEED";return False
        if fix.satellites is not None and fix.satellites<self.config.minimum_satellites: self.state="NO_FIX";self.reason="INSUFFICIENT SATELLITES";return False
        if fix.horizontal_accuracy_m is not None and fix.horizontal_accuracy_m>self.config.maximum_accuracy_m: self.state="NO_FIX";self.reason="GNSS ACCURACY TOO POOR";return False
        if self.last and fix.timestamp_ns<=self.last.timestamp_ns: self.state="ERROR";self.reason="NONMONOTONIC GNSS TIMESTAMP";return False
        if self.last and distance_m(self.last,fix)>self.config.maximum_jump_m: self.state="ERROR";self.reason="IMPLAUSIBLE GNSS POSITION JUMP";return False
        self.last=fix; self.state=fix.fix_type if fix.source == "GNSS" and fix.fix_type in {"2D_FIX", "3D_FIX"} else "ONLINE";self.reason=f"VALID {fix.source} FIX";self.trail.append({"latitude_deg":fix.latitude_deg,"longitude_deg":fix.longitude_deg,"timestamp_ns":fix.timestamp_ns,"source":fix.source});return True
    def set_receiver_state(self, state: Status, reason: str) -> None:
        """Reader lifecycle state only; it never affects TARK control authority."""
        self.state, self.reason = state, reason
    def response(self, now_ns: int | None = None) -> dict:
        now=now_ns or time.monotonic_ns()
        if self.last and (now-self.last.timestamp_ns)/1_000_000>self.config.freshness_ms:
            self.state,self.reason="STALE","GNSS FIX EXCEEDED FRESHNESS THRESHOLD"
            return {"state":"STALE","reason":self.reason,"location":None,"breadcrumbs":list(self.trail)}
        return {"state":self.state,"reason":self.reason,"location":self.last.payload(now) if self.last and self.state in {"ONLINE", "2D_FIX", "3D_FIX"} else None,"breadcrumbs":list(self.trail)}

class GnssSimulator:
    def __init__(self, origin: tuple[float,float]=(17.385,78.4867)): self.origin=origin
    def fix(self, step: int, now_ns: int | None = None) -> GnssFix:
        """Deterministic, labelled route for software-only map and API testing."""
        now=now_ns or time.monotonic_ns(); lat,lon=self.origin
        angle=math.radians((step * 3) % 360)
        # Each step is approximately 0.25 m: compatible with a 4 Hz, 1 m/s
        # software simulation update and well inside the location plausibility bound.
        fix_type="3D_FIX" if (step//20)%2==0 else "2D_FIX"
        return GnssFix("TARK-001",now,"SIMULATION",lat+step*0.00000225,lon+0.00012*math.sin(angle),speed_mps=1.0+0.2*math.sin(angle),heading_deg=(90.0+step*3)%360,horizontal_accuracy_m=3.5+0.5*math.cos(angle),fix_type=fix_type,satellites=12,quality="SIMULATION",status="ONLINE",received_monotonic_ns=now)
