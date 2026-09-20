from app.gnss import GnssConfig, GnssFix, GnssLocationService, GnssSimulator, parse_nmea


def sentence(body: str) -> str:
    checksum = __import__('functools').reduce(lambda value, char: value ^ ord(char), body, 0)
    return f"${body}*{checksum:02X}"


def valid(now=1_000_000_000, **changes):
    values=dict(vehicle_id="TARK-001",timestamp_ns=now,source="SIMULATION",latitude_deg=17.385,longitude_deg=78.4867,speed_mps=1.0,heading_deg=45.0,horizontal_accuracy_m=4.0,fix_type="3D_FIX",satellites=12,quality="SIMULATION",status="ONLINE")
    values.update(changes); return GnssFix(**values)

def test_gnss_valid_stale_jump_speed_and_bounded_trail():
    service=GnssLocationService(GnssConfig(freshness_ms=10,maximum_jump_m=20,maximum_speed_mps=5,breadcrumb_limit=2))
    assert service.accept(valid())
    assert service.response(1_000_000_005)["state"] == "ONLINE"
    assert service.response(1_020_000_000)["state"] == "STALE"
    assert service.state == "STALE"
    assert service.accept(valid(now=1_030_000_000, latitude_deg=17.38501)) and service.response(1_030_000_001)["state"] == "ONLINE"
    assert not service.accept(valid(now=2_000_000_000,latitude_deg=18.0))
    assert not GnssLocationService().accept(valid(speed_mps=99))
    bounded=GnssLocationService(GnssConfig(breadcrumb_limit=2))
    for step in range(3): assert bounded.accept(valid(now=(step+1)*1_000_000_000,latitude_deg=17.385+step*.00001))
    assert len(bounded.response(4_000_000_000)["breadcrumbs"]) == 2

def test_nmea_parser_rejects_bad_data_and_simulation_is_explicit():
    assert parse_nmea("not nmea") is None
    assert parse_nmea("$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4*00") is None
    simulated=GnssSimulator().fix(1,now_ns=2)
    assert simulated.source == "SIMULATION" and simulated.status == "ONLINE"
    later=GnssSimulator().fix(25,now_ns=3)
    assert later.speed_mps != simulated.speed_mps and later.fix_type == "2D_FIX"


def test_nmea_no_fix_invalid_coordinate_and_optional_fields_are_truthful():
    no_fix = parse_nmea(sentence("GPRMC,123519,V,,,,,,,230394,,,N"), now_ns=10)
    assert no_fix is not None and no_fix.status == "NO_FIX" and no_fix.latitude_deg is None
    service = GnssLocationService()
    assert not service.accept(no_fix)
    assert service.response(11)["state"] == "NO_FIX" and service.response(11)["location"] is None
    assert parse_nmea(sentence("GPRMC,123519,A,9160.000,N,07829.202,E,001.0,045.0,230394,,,A")) is None
    optional = parse_nmea(sentence("GPRMC,123519,A,1723.100,N,07829.202,E,,,230394,,,A"), now_ns=12)
    assert optional is not None and optional.speed_mps is None and optional.heading_deg is None


def test_standard_gsa_exposes_fix_dimension_without_inventing_coordinates():
    two_d = parse_nmea(sentence("GPGSA,A,2,,,,,,,,,,,,,1.8,1.0,1.5"), now_ns=20)
    three_d = parse_nmea(sentence("GPGSA,A,3,,,,,,,,,,,,,1.8,1.0,1.5"), now_ns=21)
    assert two_d is not None and two_d.status == "2D_FIX" and two_d.latitude_deg is None
    assert three_d is not None and three_d.status == "3D_FIX" and three_d.latitude_deg is None
    service = GnssLocationService()
    assert not service.accept(two_d)
    assert service.response(22)["state"] == "2D_FIX" and service.response(22)["location"] is None

def test_receive_time_is_not_measurement_time_and_is_reported_for_freshness():
    fix=valid(now=100, measurement_time_utc="1994-03-23T12:35:19Z", received_monotonic_ns=100)
    payload=fix.payload(1_000_100)
    assert payload["measurement_time_utc"] == "1994-03-23T12:35:19Z"
    assert payload["received_monotonic_ns"] == 100 and payload["freshness_ms"] == 1.0
