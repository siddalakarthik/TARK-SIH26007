from __future__ import annotations
import json
from app.domain.models import RadarDetection

class FrameError(ValueError): pass

class LD2450Parser:
    """Parses deterministic SIM1 fixtures; vendor binary decoding requires reviewed vendor framing."""
    def parse(self, raw: bytes, arrival_ns: int) -> list[RadarDetection]:
        if not raw.startswith(b"SIM1 ") or not raw.endswith(b"\n"):
            raise FrameError("unsupported or malformed frame; raw bytes retained for diagnosis")
        try: payload=json.loads(raw[5:-1])
        except json.JSONDecodeError as error: raise FrameError("invalid SIM1 JSON") from error
        detections=[]
        for item in payload.get("detections", []):
            detections.append(RadarDetection(candidate_id=int(item["id"]), x_m=float(item["x_m"]), y_m=float(item["y_m"]), velocity_mps=float(item["velocity_mps"]), quality=float(item["quality"]), uncertainty_m=float(item.get("uncertainty_m", 0.5)), timestamp_ns=arrival_ns))
        return detections

