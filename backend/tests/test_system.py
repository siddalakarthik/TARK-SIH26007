from pathlib import Path
import re
from unittest.mock import Mock
from app.config import Settings
from app.gnss import GnssFix
from app.services.system import TarkSystem

def real_gnss_fix(now_ns: int) -> GnssFix:
    return GnssFix("TARK-001",now_ns,"GNSS",17.385,78.4867,speed_mps=1.0,heading_deg=45.0,horizontal_accuracy_m=4.0,fix_type="3D_FIX",satellites=12,quality="GGA_QUALITY_1",status="ONLINE",received_monotonic_ns=now_ns)

def test_full_simulation_snapshot_is_labelled_and_non_actuating():
    system=TarkSystem(Settings.from_file(Path(__file__).parents[2]/"config"/"phase1.json"))
    snapshot=system.tick(1_000_000_000)
    assert snapshot["mode"]=="SIMULATION" and snapshot["traction"]=="DISABLED_PHASE_1"
    assert snapshot["command"]["left_command"]==snapshot["command"]["right_command"]==0
    assert snapshot["protocol"]["source_mode"]=="SIMULATION"
    assert snapshot["protocol"]["transport_source_mode"]=="SIMULATION"
    assert snapshot["protocol"]["feedback"]["output_state"]=="DISABLED_PHASE_1"
    assert snapshot["protocol"]["feedback"]["payload"]["applied_left"]==snapshot["protocol"]["feedback"]["payload"]["applied_right"]==0
    assert snapshot["vehicle_location"]["state"]=="ONLINE"
    assert snapshot["vehicle_location"]["location"]["source"]=="SIMULATION"
    later=system.tick(2_000_000_000)["vehicle_location"]
    assert later["location"]["latitude_deg"]!=snapshot["vehicle_location"]["location"]["latitude_deg"]
    # A delayed API caller must not make simulated telemetry look like a real
    # GNSS timestamp fault when WebSocket and API publication overlap.
    assert system.vehicle_location(1_500_000_000)["state"]=="ONLINE"
    assert any(x["source_mode"]=="NOT_CONNECTED_PHASE_2" for x in snapshot["sensors"])
    assert all("device_id" in sensor and "sensor_id" not in sensor for sensor in snapshot["sensors"])

def test_gnss_modules_cannot_import_or_command_control_hardware():
    root=Path(__file__).parents[1]/"app"
    combined=(root/"gnss.py").read_text()+(root/"gnss_driver.py").read_text()
    assert not re.search(r"^(?:from|import)\s+.*(?:esp32|mdd10|motor|controller)",combined,re.MULTILINE|re.IGNORECASE)

def test_non_simulation_mode_never_injects_the_simulator():
    settings=Settings.from_file(Path(__file__).parents[2]/"config"/"phase1.json").model_copy(update={"mode":"real_radar"})
    system=TarkSystem(settings); system.gnss_simulator.fix=Mock(side_effect=AssertionError("simulator must not run"))
    location=system.vehicle_location(1_000_000_000)
    assert location["state"]=="NO_RECEIVER" and location["location"] is None
    system.gnss_simulator.fix.assert_not_called()

def test_real_gnss_fix_remains_authoritative_across_location_reads_and_ticks():
    settings=Settings.from_file(Path(__file__).parents[2]/"config"/"phase1.json").model_copy(update={"mode":"real_radar"})
    system=TarkSystem(settings); system.gnss_simulator.fix=Mock(side_effect=AssertionError("simulator must not run"))
    assert system.ingest_gnss_fix(real_gnss_fix(1_000_000_000))
    assert system.vehicle_location(1_100_000_000)["location"]["source"]=="GNSS"
    # WebSocket publication uses tick(); it must not replace a real fix.
    snapshot=system.tick(1_200_000_000)
    assert snapshot["vehicle_location"]["location"]["source"]=="GNSS"
    assert snapshot["mode"]==snapshot["protocol"]["source_mode"]=="REAL_RADAR"
    # Individual software-only components stay explicitly labelled even while
    # the runtime has a real GNSS location source.
    assert snapshot["protocol"]["transport_source_mode"]=="SIMULATION"
    assert any(sensor["device_id"]=="ld2450" and sensor["source_mode"]=="SIMULATION" for sensor in snapshot["sensors"])
    assert any(sensor["device_id"]=="esp32" and sensor["source_mode"]=="SIMULATION" for sensor in snapshot["sensors"])
    assert snapshot["traction"]=="DISABLED_PHASE_1"
    assert snapshot["command"]["left_command"]==snapshot["command"]["right_command"]==0
    assert snapshot["protocol"]["feedback"]["output_state"]=="DISABLED_PHASE_1"
    system.gnss_simulator.fix.assert_not_called()
