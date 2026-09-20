from pathlib import Path
from app.config import Settings
from app.domain.models import RadarDetection, Freshness, SafetyState
from app.services.pipeline import Pipeline, freshness, ttc

SETTINGS=Settings.from_file(Path(__file__).parents[2]/"config"/"phase1.json")
def test_freshness_progresses_without_time_jump():
    assert freshness(1_000_000_000,1_100_000_000,250,1000)==Freshness.FRESH
    assert freshness(1_000_000_000,2_100_000_000,250,1000)==Freshness.STALE
def test_phase1_command_is_always_non_actuating():
    p=Pipeline(SETTINGS); d=RadarDetection(candidate_id=1,x_m=3,y_m=0,velocity_mps=-1,quality=.8,uncertainty_m=.1,timestamp_ns=1_000_000_000)
    result=p.ingest([d],1_000_000_000); command=p.command(result,1_000_000_000)
    assert result.permitted_speed_mps==0 and command.left_command==0 and command.right_command==0
def test_stale_sensor_never_normal():
    p=Pipeline(SETTINGS); result=p.decision(3_000_000_000)
    assert result.state==SafetyState.UNKNOWN

