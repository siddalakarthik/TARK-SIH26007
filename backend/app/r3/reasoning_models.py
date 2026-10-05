"""Versioned research reasoning contracts. No field grants motion authority."""
from typing import Literal
from pydantic import Field, model_validator
from app.r3.contracts import Contract, Count, Finite, Nonnegative, Token, Mode, digest

State = Literal['NORMAL','WARN','RESTRICT','UNKNOWN','STOP']
Purpose = Literal['DISPLAY','LOCALIZATION','TRACK_ASSOCIATION','SEMANTIC_CLASSIFICATION',
                  'RANGE','RADIAL_VELOCITY','EGO_MOTION','COOPERATIVE_CONTEXT','PVSOE_INPUT']
Origin = Literal['MEASURED','CONFIGURED_RESEARCH','UNKNOWN']

class Environment(Contract):
    visibility: Literal['GOOD','DEGRADED','SEVERE','UNKNOWN'] = 'UNKNOWN'
    provenance: Origin = 'UNKNOWN'
    evidence_reference: Token = 'NO_VISIBILITY_MEASUREMENT'

class CoverageModel(Contract):
    source_id: Token
    hazard_classes: list[Token] = Field(min_length=1,max_length=8)
    range_m: Nonnegative | None = None
    uncertainty_m: Nonnegative | None = None
    half_angle_deg: Nonnegative = Field(lt=90)
    provenance: Origin = 'UNKNOWN'
    evidence_reference: Token
    degraded_factor: float = Field(ge=0,le=1,default=0.5)
    severe_factor: float = Field(ge=0,le=1,default=0.)
    @model_validator(mode='after')
    def justified(self):
        if self.provenance!='UNKNOWN' and (self.range_m is None or self.uncertainty_m is None):
            raise ValueError('coverage requires range and its uncertainty')
        if self.severe_factor>self.degraded_factor:raise ValueError('worse visibility cannot increase coverage')
        return self

class VehicleModel(Contract):
    profile: Literal['SMALL_SCALE_POC','R3_RESEARCH_CART','HEMM_REFERENCE_MODEL']='R3_RESEARCH_CART'
    provenance: Origin='CONFIGURED_RESEARCH'
    evidence_reference: Token='UNVALIDATED_RESEARCH_PARAMETERS'
    response_s: Nonnegative=1.
    deceleration_mps2: float=Field(gt=0,default=0.5)
    margin_m: Nonnegative=0.5
    maximum_speed_mps: float=Field(gt=0,default=1.5)

class ConflictZone(Contract):
    zone_id: Token
    latitude_min: Finite=Field(ge=-90,le=90)
    latitude_max: Finite=Field(ge=-90,le=90)
    longitude_min: Finite=Field(ge=-180,le=180)
    longitude_max: Finite=Field(ge=-180,le=180)
    provenance: Origin
    evidence_reference: Token
    @model_validator(mode='after')
    def valid_box(self):
        if self.latitude_min>=self.latitude_max or self.longitude_min>=self.longitude_max or self.provenance=='UNKNOWN':
            raise ValueError('explicit non-wrapping geographic research zone required')
        return self

class ReasoningConfig(Contract):
    version: Literal['TARK_R3_REASONING_CONFIG_1']='TARK_R3_REASONING_CONFIG_1'
    config_id: Token='R3_UNCOMMISSIONED_REASONING'
    vehicle: VehicleModel=Field(default_factory=VehicleModel)
    required_hazard_classes: list[Token]=Field(default_factory=lambda:['STATIC_OBSTACLE','VEHICLE','PERSON'],min_length=1,max_length=8)
    coverage: list[CoverageModel]=Field(default_factory=list,max_length=16)
    environment: Environment=Field(default_factory=Environment)
    corridor_half_width_m: float|None=Field(default=None,gt=0,le=100)
    corridor_near_m: Nonnegative=1.
    corridor_far_m: float=Field(gt=0,le=500,default=30.)
    position_bound_max_m: float=Field(gt=0,default=2.)
    association_gate_m: float=Field(gt=0,default=2.)
    association_time_ns: Count=100_000_000
    track_expiry_ns: Count=500_000_000
    max_tracks: int=Field(ge=1,le=64,default=32)
    recovery_frames: int=Field(ge=2,le=100,default=3)
    recovery_dwell_ns: Count=500_000_000
    fixed_body_axes_research: bool=False
    maximum_angular_rate_rad_s: Nonnegative=0.02
    maximum_motion_interval_ns: Count=500_000_000
    relative_acceleration_bound_mps2: Nonnegative=1.
    max_velocity_uncertainty_mps: float=Field(gt=0,default=1.)
    ttc_horizon_s: float=Field(gt=0,le=30,default=5.)
    encoder_count_semantics: Literal['UNKNOWN','INTERVAL_DELTA']='UNKNOWN'
    wheel_slip_bound_mps: Nonnegative|None=None
    max_wheel_disagreement_mps: Nonnegative=0.3
    conflict_zones: list[ConflictZone]=Field(default_factory=list,max_length=8)
    peer_position_bound_m: float=Field(gt=0,default=2.)
    peer_requires_corrections: bool=True
    max_correction_age_s: float=Field(gt=0,default=2.)
    peer_restrict_speed_mps: Nonnegative=0.3
    @model_validator(mode='after')
    def coherent(self):
        if self.corridor_near_m<=0 or self.corridor_far_m<=self.corridor_near_m:raise ValueError('invalid local corridor')
        if self.track_expiry_ns<=0 or self.maximum_motion_interval_ns<=0:raise ValueError('invalid time limit')
        if self.peer_restrict_speed_mps>self.vehicle.maximum_speed_mps:raise ValueError('peer restriction exceeds speed ceiling')
        return self
    @property
    def content_hash(self):return digest(self.model_dump(mode='json'))

class SemanticObservation(Contract):
    version: Literal['TARK_R3_SEMANTIC_1']='TARK_R3_SEMANTIC_1'
    source_id: Token
    evidence_id: Token
    capture_ns: Count|None
    capture_uncertainty_ns: Count|None
    age_bound_ns: Count|None
    mode: Mode
    frame: Token
    purposes: list[Purpose]=Field(max_length=9)
    calibration_refs: list[Token]=Field(max_length=8)
    uncertainty: dict[str,Nonnegative]|None
    lineage: list[Token]=Field(max_length=32)
    measurement_kind: Token
    measurement: dict
    units: dict
    exclusion_reason: Token|None

class Track(Contract):
    version: Literal['TARK_R3_TRACK_1']='TARK_R3_TRACK_1'
    track_id: Token
    lifecycle: Literal['NEW','CONFIRMED','COASTING']
    source_id: Token
    evidence_ids: list[Token]=Field(max_length=4)
    mode: Mode
    position_body_m: list[Finite]=Field(min_length=3,max_length=3)
    position_bound_m: Nonnegative
    radial_velocity_mps: Finite
    radial_velocity_bound_mps: Nonnegative|None
    relative_velocity_mps: list[Finite]|None=Field(default=None,min_length=2,max_length=2)
    velocity_bound_mps: Nonnegative|None=None
    velocity_method: Token='UNAVAILABLE'
    absolute_target_velocity: None=None
    capture_ns: Count
    capture_uncertainty_ns: Count
    last_evidence_ns: Count
    age_ns: Count
    prediction_horizon_ns: Count=0
    relevance: Literal['RELEVANT','IRRELEVANT','UNKNOWN']='UNKNOWN'
    classifications: list[Token]=Field(default_factory=list,max_length=8)
    semantic_evidence_ids: list[Token]=Field(default_factory=list,max_length=8)
    contributors: list[Token]=Field(default_factory=list,max_length=8)
    association: Literal['ASSOCIATED','POSSIBLE','UNRESOLVED','CONFLICTING']='UNRESOLVED'

class TTC(Contract):
    track_id: Token
    value_s: Nonnegative|None=None
    lower_bound_s: Nonnegative|None=None
    upper_bound_s: Nonnegative|None=None
    method: Token='CONDITIONAL_FIXED_BODY_AXES'
    valid: bool=False
    reason: Token='INSUFFICIENT_MOTION_EVIDENCE'
    input_evidence: list[Token]=Field(default_factory=list,max_length=4)

class EvidenceQuality(Contract):
    sources: list[Token]=Field(max_length=32)
    range: Nonnegative|None
    bounds: dict[Token,dict[Token,Nonnegative]]=Field(max_length=32)
    peers: list[Token]=Field(max_length=8)
    purposes: dict[Token,list[Purpose]]=Field(max_length=32)

class PreviousDecision(Contract):
    state: State
    cap: Nonnegative|None
    quality: EvidenceQuality

class ReasoningCheckpoint(Contract):
    version: Literal['TARK_R3_REASONING_CHECKPOINT_1']
    tracks: list[Track]=Field(max_length=64)
    counter: Count
    last_ids: dict[Token,Token]=Field(max_length=32)
    previous: PreviousDecision|None
    recovery_count: Count
    recovery_since: Count|None
    epoch: Token|None
    recovery_quality: EvidenceQuality|None

class ObservabilityEnvelope(Contract):
    forward_range_m: Nonnegative|None
    provenance: Origin
    class_ranges_m: dict[str,Nonnegative|None]
    modality_support: list[Token]=Field(max_length=16)
    limiting_reason: Token
    environment: Environment
    road_clear_claim: Literal[False]=False

class R3Decision(Contract):
    decision_version: Literal['TARK_R3_ADVISORY_1']='TARK_R3_ADVISORY_1'
    timestamp_ns: Count
    valid_until_ns: Count
    state: State
    advisory: Token
    advised_speed_mps: Nonnegative|None
    vehicle_profile: VehicleModel
    ego_speed_mps: Nonnegative|None
    ego_speed_bound_mps: Nonnegative|None
    ego_speed_semantics: Literal['WHEEL_RESPONSE_NOT_GROUND_TRUTH']='WHEEL_RESPONSE_NOT_GROUND_TRUTH'
    stopping_requirement_m: Nonnegative|None
    observability: ObservabilityEnvelope
    semantic_observations: list[SemanticObservation]=Field(max_length=32)
    tracks: list[Track]=Field(max_length=64)
    ttc: list[TTC]=Field(max_length=64)
    hazards: list[dict]=Field(max_length=64)
    cooperative_context: list[dict]=Field(max_length=8)
    limiting_reason: Token
    qualified_sources: list[Token]=Field(max_length=32)
    excluded_sources: dict[str,Token]
    configuration_hash: Token
    configuration_id: Token
    calibration_refs: list[Token]=Field(max_length=256)
    software_fingerprint: Token
    source_mode: Token
    explanation: dict
    motion_authority: Literal[False]=False
    traction: Literal['DISABLED_PHASE_1']='DISABLED_PHASE_1'
    hardware_verified: Literal[False]=False
    @model_validator(mode='after')
    def valid_claims(self):
        # Dict sections also reject NaN/Infinity on a JSON round trip.
        digest(self.model_dump(mode='json'))
        if self.state=='UNKNOWN' and self.advised_speed_mps is not None:raise ValueError('unknown capability is not a numeric speed')
        if self.valid_until_ns<self.timestamp_ns:raise ValueError('decision deadline before evaluation')
        return self
