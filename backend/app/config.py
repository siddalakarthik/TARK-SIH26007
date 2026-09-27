from __future__ import annotations

import hashlib
import json
from pathlib import Path
from pydantic import BaseModel, Field, model_validator


class Parameter(BaseModel):
    value: float = Field(ge=0, allow_inf_nan=False)
    unit: str
    status: str


class Settings(BaseModel):
    mode: str = "simulation"
    configuration_hash: str
    fresh_age_ms: int = Field(gt=0)
    stale_age_ms: int = Field(gt=0)
    track_timeout_ms: int = Field(gt=0)
    hard_cap_mps: float = Field(ge=0, allow_inf_nan=False)
    reaction_bound_s: Parameter
    effective_deceleration_mps2: Parameter
    margin_m: Parameter
    esp32_timeout_ms: int = Field(gt=0, le=500)

    @model_validator(mode="after")
    def sensible_ages(self) -> "Settings":
        if self.effective_deceleration_mps2.value <= 0:
            raise ValueError("effective_deceleration_mps2 must be strictly positive")
        if self.stale_age_ms <= self.fresh_age_ms:
            raise ValueError("stale_age_ms must exceed fresh_age_ms")
        if self.mode not in {"simulation", "replay", "real_radar"}:
            raise ValueError("mode must be simulation, replay, or real_radar")
        return self

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        raw = path.read_bytes()
        data = json.loads(raw)
        settings = cls.model_validate(data)
        # A release may replace this marker with a reviewed hash. Never silently hash a changed file as authority.
        if settings.configuration_hash == "AUTO":
            settings.configuration_hash = hashlib.sha256(raw).hexdigest()
        return settings
