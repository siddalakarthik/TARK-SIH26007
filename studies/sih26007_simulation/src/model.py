"""Research kinematics. No imports from the live TARK application or hardware."""
from dataclasses import dataclass
from math import isfinite, sqrt


def nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
    return float(value)


@dataclass(frozen=True)
class Parameters:
    delay_s: float
    deceleration_mps2: float
    margin_m: float
    uncertainty_m: float

    def __post_init__(self):
        for k, v in vars(self).items():
            nonnegative(v, k)
        if self.deceleration_mps2 <= 0:
            raise ValueError('deceleration must be positive')


def components(v, p):
    v = nonnegative(v, 'speed')
    response = v * p.delay_s
    braking = v * v / (2 * p.deceleration_mps2)
    stop = response + braking + p.margin_m
    return dict(response_distance_m=response, braking_distance_m=braking,
                stopping_distance_m=stop, required_perception_range_m=stop+p.uncertainty_m)


def speed_cap(r, p):
    """Positive quadratic root; 0 means no positive speed, not necessarily feasible."""
    budget = nonnegative(r, 'range') - p.margin_m - p.uncertainty_m
    if budget <= 0:
        return 0.0
    # Rationalized root avoids subtraction cancellation near the boundary.
    return 2 * budget / (p.delay_s + sqrt(p.delay_s*p.delay_s + 2*budget/p.deceleration_mps2))


def operating_point(r, desired, p, *, age_s=0, stale_s=1, available=True):
    nonnegative(desired, 'desired speed'); nonnegative(age_s, 'age'); nonnegative(stale_s, 'stale threshold')
    r = nonnegative(r, 'range')
    # Explicit research freshness policy. Age consumes response-distance budget.
    # This is NOT the R1 production PV-SOE state machine.
    aged = Parameters(p.delay_s+age_s, p.deceleration_mps2, p.margin_m, p.uncertainty_m)
    v = min(desired, speed_cap(r, aged)) if available and age_s <= stale_s else 0.0
    c = components(v, aged)
    margin = r-c['required_perception_range_m']
    operation = bool(available and age_s <= stale_s and v > 0 and margin >= -1e-8)
    return dict(speed_mps=v, speed_kmph=3.6*v, safety_margin_m=margin,
                operation_available=operation, restricted=operation and v < desired-1e-8,
                halted=not operation, analytical_state='HALT_UNAVAILABLE' if not operation else
                'RESTRICTED_MODEL' if v < desired-1e-8 else 'MODEL_COMPATIBLE', **c)


def encounter(separation, v, target_v, r, p, post_stop_s):
    """Point-front clear gap; target constant speed. Exact piecewise minimum.

    Target is not assumed to brake. Oncoming encounters are reported only over
    the explicit finite horizon, with eventual impact separately acknowledged.
    """
    for key, value in [('separation', separation), ('speed', v), ('range', r), ('horizon', post_stop_s)]:
        nonnegative(value, key)
    if isinstance(target_v, bool) or not isfinite(target_v):
        raise ValueError('target velocity must be finite')
    closing = v-target_v
    if r <= 0 or (separation > r and closing <= 0):
        return dict(detected=False, initial_closing_rate_mps=closing,
                    ttc_analysis_s=separation/closing if closing > 0 else None)
    wait = max(0.0, (separation-r)/closing) if closing > 0 else 0.0
    detected_gap = separation-closing*wait
    stop_time = p.delay_s+v/p.deceleration_mps2
    horizon = stop_time+post_stop_s
    def x(t):
        brake_t = min(max(t-p.delay_s, 0.0), v/p.deceleration_mps2)
        return v*min(t,p.delay_s)+v*brake_t-0.5*p.deceleration_mps2*brake_t**2
    def clearance(t):
        return detected_gap+target_v*t-x(t)
    points = [0.0, p.delay_s, stop_time, horizon]
    extremum = p.delay_s+(v-target_v)/p.deceleration_mps2
    if p.delay_s <= extremum <= stop_time:
        points.append(extremum)
    closure = max(x(t)-target_v*t for t in points)
    minimum = min(clearance(t) for t in points)
    required = closure+p.margin_m+p.uncertainty_m
    return dict(detected=True, detection_wait_s=wait, available_distance_m=detected_gap,
                initial_closing_rate_mps=closing, ttc_analysis_s=separation/closing if closing > 0 else None,
                minimum_clearance_m=minimum, safety_margin_m=detected_gap-required,
                required_detection_range_m=required, model_collision=minimum <= 0,
                stop_time_s=wait+stop_time, stop_position_m=v*wait+x(stop_time),
                observation_horizon_s=wait+horizon,
                eventual_oncoming_collision=target_v < 0, **components(v,p))


def requirements(v, r, p):
    nonnegative(v,'speed'); nonnegative(r,'range')
    spare = r-p.margin_m-p.uncertainty_m
    delay = (spare-v*v/(2*p.deceleration_mps2))/v if v else None
    braking_budget = spare-v*p.delay_s
    a = v*v/(2*braking_budget) if braking_budget > 0 and v else None
    u = r-components(v,p)['stopping_distance_m']
    return dict(max_response_delay_s=delay if delay is not None and delay >= 0 else None,
                min_effective_deceleration_mps2=a, max_uncertainty_allowance_m=u if u >= 0 else None,
                **components(v,p))


def normalized_cycle(fixed, nonfog, fog, desired, constrained, recovery_speed, dwell):
    for k,v in locals().copy().items():
        nonnegative(v,k)
    if abs(fixed+nonfog+fog-1) > 1e-9 or desired <= 0 or recovery_speed <= 0:
        raise ValueError('normalized shares must sum to 1, speeds positive')
    travel_speed = constrained if constrained > 0 else recovery_speed
    wait = dwell if constrained <= 0 else 0.0
    cycle = fixed+nonfog+fog*desired/travel_speed+wait
    return dict(normalized_cycle_time=cycle, normalized_productivity=1/cycle,
                normalized_trips_per_unit_time=1/cycle, relative_throughput_index=1/cycle,
                fog_induced_delay_index=cycle-1, halt_fraction=wait/cycle,
                restriction_fraction=(fog*desired/travel_speed/cycle) if constrained > 0 and constrained < desired else 0.0)
