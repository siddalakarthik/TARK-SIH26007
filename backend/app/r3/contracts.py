"""Canonical R3 evidence v1. Arrival, capture and publication are different clocks."""
from __future__ import annotations

import hashlib
import json
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Token = Annotated[str, Field(min_length=1, max_length=128)]
Count = Annotated[int, Field(strict=True, ge=0, le=2**63-1)]
Finite = Annotated[float, Field(allow_inf_nan=False)]
Nonnegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Mode = Literal['REAL', 'SIMULATION', 'REPLAY']


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True, allow_inf_nan=False)


class Identity(Contract):
    source_id: Token
    node_id: Token
    device_class: Token
    manufacturer: Token | None = None
    part_number: Token | None = None
    hardware_revision: Token | None = None
    serial_number: Token | None = None
    asset_id: Token | None = None
    firmware_version: Token | None = None
    driver_version: Token
    boot_id: Token
    session_id: Token


class ObservationTime(Contract):
    native_timestamp: Count | None = None
    native_timestamp_units: Literal['ns', 'us', 'ms', 'ticks'] | None = None
    native_clock_domain: Token | None = None
    host_epoch: Token
    host_monotonic_arrival: Count
    estimated_capture_time: Count | None = None
    capture_time_uncertainty: Count | None = None
    clock_mapping_version: Token | None = None
    utc_mapping_version: Token | None = None
    utc_time: Token | None = None
    publication_time: Count
    measurement_age: Count | None = None

    @model_validator(mode='after')
    def valid_clock_claims(self):
        if self.publication_time < self.host_monotonic_arrival:
            raise ValueError('publication precedes arrival')
        if self.native_timestamp is not None and (self.native_timestamp_units is None or self.native_clock_domain is None):
            raise ValueError('native time requires units and clock domain')
        capture = self.estimated_capture_time
        if capture is None:
            if self.measurement_age is not None or self.capture_time_uncertainty is not None:
                raise ValueError('capture age/uncertainty unavailable without capture estimate')
        elif self.capture_time_uncertainty is None or self.clock_mapping_version is None:
            raise ValueError('capture estimate requires uncertainty and mapping identity')
        elif capture > self.host_monotonic_arrival or self.measurement_age != self.publication_time-capture:
            raise ValueError('invalid capture estimate or age')
        if (self.utc_time is None) != (self.utc_mapping_version is None):
            raise ValueError('UTC requires its legitimate mapping identity')
        return self


class Integrity(Contract):
    sequence_number: Count
    source_counter: Count | None = None
    payload_length: Count
    transport_error: Token | None = None
    check_result: Literal['PASS', 'FAIL', 'NOT_AVAILABLE'] = 'NOT_AVAILABLE'
    drop_count: Count = 0
    duplicate_count: Count = 0
    out_of_order_count: Count = 0
    parse_error: Token | None = None


class Measurement(Contract):
    kind: Token
    payload: dict[str, JsonValue]
    units: dict[str, Token]
    sensor_frame: Token
    mode_profile: Token
    configuration_hash: Token

    @model_validator(mode='after')
    def bounded_json(self):
        encoded=json.dumps(self.payload, allow_nan=False, separators=(',', ':')).encode()
        if len(encoded)>65_536 or len(self.units)>64:
            raise ValueError('measurement too large; use a hashed media reference')
        return self


class Qualification(Contract):
    connection_state: Literal['NOT_CONNECTED','CONNECTED','UNKNOWN'] = 'UNKNOWN'
    production_state: Literal['NO_DATA','PRODUCING','FAILED'] = 'NO_DATA'
    freshness_state: Literal['UNKNOWN','FRESH','STALE'] = 'UNKNOWN'
    clock_state: Literal['TIME_VALID','TIME_DEGRADED','TIME_UNSYNCED','CLOCK_RESET','CLOCK_DRIFT_EXCEEDED','TIMESTAMP_INVALID'] = 'TIME_UNSYNCED'
    calibration_state: Literal['MISSING','VALID','INVALID','NOT_REQUIRED'] = 'MISSING'
    health_state: Literal['UNKNOWN','ONLINE','DEGRADED','FAILED'] = 'UNKNOWN'
    plausibility_state: Literal['UNKNOWN','PLAUSIBLE','INVALID'] = 'UNKNOWN'
    fault_reason: Token | None = None
    measurement_age_bound: Count | None = None
    uncertainty: dict[str, Nonnegative] | None = None
    uncertainty_origin: Token | None = None
    calibration_id: Token | None = None
    calibration_version: Token | None = None
    qualified_for: list[Token] = Field(default_factory=list, max_length=16)

    @model_validator(mode='after')
    def uncertainty_has_origin(self):
        if self.uncertainty is not None and self.uncertainty_origin is None:
            raise ValueError('uncertainty needs an origin, not an assumed zero')
        return self


class Provenance(Contract):
    mode: Mode
    evidence_origin: Literal['REAL_CAPTURE','SYNTHETIC_FIXTURE','SIMULATOR','REPLAY_RECORD']
    original_mode: Mode | None = None
    raw_record_reference: Token | None = None
    raw_sha256: Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')] | None = None
    transformation_lineage: list[Token] = Field(default_factory=list, max_length=32)
    software_version: Token
    configuration_bundle_id: Token

    @model_validator(mode='after')
    def modes_cannot_impersonate(self):
        expected={'REAL':{'REAL_CAPTURE'}, 'SIMULATION':{'SIMULATOR','SYNTHETIC_FIXTURE'}, 'REPLAY':{'REPLAY_RECORD'}}
        if self.evidence_origin not in expected[self.mode]:
            raise ValueError('mode/origin mismatch')
        if self.mode=='REPLAY' and self.original_mode is None:
            raise ValueError('replay requires original provenance')
        if self.mode!='REPLAY' and self.original_mode is not None:
            raise ValueError('original_mode belongs only to replay')
        return self


class Observation(Contract):
    schema_version: Literal['TARK_EVIDENCE_1'] = 'TARK_EVIDENCE_1'
    observation_id: Token
    identity: Identity
    time: ObservationTime
    integrity: Integrity
    measurement: Measurement
    qualification: Qualification
    provenance: Provenance


class SourceProfile(Contract):
    source_id: Token
    node_id: Token
    device_class: Token
    manufacturer: Token
    part_number: Token
    adapter: Token
    transport: Token
    expected_rate_hz: Nonnegative | None
    max_age_ns: Count
    max_time_uncertainty_ns: Count
    required_calibrations: list[Token] = Field(max_length=8)
    allowed_purpose: Token
    max_queue: Annotated[int, Field(ge=1, le=256)] = 8
    status: Literal['PROPOSED_ACCEPTANCE_NOT_MEASURED'] = 'PROPOSED_ACCEPTANCE_NOT_MEASURED'


class HardwareProfile(Contract):
    profile_id: Literal['R3_PI5_ADVISORY']
    version: Literal[1]
    physical_access_enabled: Literal[False] = False
    traction: Literal['DISABLED_PHASE_1'] = 'DISABLED_PHASE_1'
    usb_topology: dict[str, Token]
    startup_order: list[Token]
    sources: list[SourceProfile] = Field(max_length=32)

    @model_validator(mode='after')
    def unique_sources(self):
        ids=[s.source_id for s in self.sources]
        if len(ids)!=len(set(ids)) or any(s.max_age_ns==0 for s in self.sources):
            raise ValueError('source IDs must be unique and ages positive')
        return self
