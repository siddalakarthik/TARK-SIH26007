import time
from app.gnss_driver import GnssReader, NmeaAggregator, discover_candidates
from app.gnss import GnssConfig, GnssFix, GnssLocationService

def sentence(body): return f"${body}*{__import__('functools').reduce(lambda a,b:a^ord(b),body,0):02X}\r\n".encode()

def test_partial_multiple_corrupt_and_no_duplicate_reader():
    fixes=[]; reader=GnssReader(lambda: (_ for _ in ()).throw(OSError()),fixes.append,max_line_bytes=80)
    rmc=sentence('GPRMC,123519,A,1723.100,N,07829.202,E,001.0,045.0,230394,,,A')
    reader.feed(rmc[:12]);assert not fixes
    reader.feed(rmc[12:]+b'$BAD*00\n'+rmc);assert len(fixes)==2 and reader.diag.rmc_count==2 and reader.diag.checksum_failures==1
    assert fixes[0].measurement_time_utc == '1994-03-23T12:35:19Z' and fixes[0].received_monotonic_ns is not None
    reader.feed(b'x'*81);assert 'OVERSIZED' in reader.diag.reason
    assert reader.start() is True;assert reader.start() is False;reader.close()

def test_aggregation_and_discovery_override():
    a=GnssFix('v',1,'GNSS',1,2,speed_mps=1,fix_type='2D_FIX',status='2D_FIX');b=GnssFix('v',2,'GNSS',1,2,altitude_m=3,satellites=8,fix_type='3D_FIX',status='3D_FIX')
    aggregator=NmeaAggregator();aggregator.add(a);combined=aggregator.add(b)
    assert combined.speed_mps==1 and combined.altitude_m==3 and combined.satellites==8
    assert discover_candidates('/dev/ttyACM0')[0]['identity']=='UNVERIFIED'

def test_mismatched_epoch_is_not_combined_raw_log_is_bounded_and_reconnects(tmp_path):
    a=GnssFix('v',1,'GNSS',1,2,speed_mps=1,fix_type='2D_FIX',status='2D_FIX');b=GnssFix('v',9_000_000_000,'GNSS',1,2,altitude_m=3,fix_type='3D_FIX',status='3D_FIX')
    aggregate=NmeaAggregator();aggregate.add(a);assert aggregate.add(b).speed_mps is None
    log=tmp_path/'raw.log';reader=GnssReader(lambda: (_ for _ in ()).throw(OSError()),lambda _fix:None,reconnect_s=.1,raw_limit=1,raw_log_path=str(log));reader.feed(sentence('GPRMC,123519,A,1723.100,N,07829.202,E,001.0,045.0,230394,,,A'))
    assert len(reader.raw)==1 and log.exists() and len(log.read_bytes())>0
    reader.start();time.sleep(.15);reader.close();assert reader.diag.reconnect_count>=1


def test_reader_applies_standard_gsa_dimension_and_transport_lifecycle():
    class IdlePort:
        def read(self, size=1):
            time.sleep(.01)
            return b""
        def close(self): pass

    service=GnssLocationService(GnssConfig(freshness_ms=1_000))
    states=[]
    reader=GnssReader(lambda:IdlePort(),service.accept,on_state=lambda state,reason:states.append((state,reason)))
    reader.feed(sentence('GPGSA,A,3,,,,,,,,,,,,,1.8,1.0,1.5'),now_ns=100)
    reader.feed(sentence('GPRMC,123519,A,1723.100,N,07829.202,E,001.0,045.0,230394,,,A'),now_ns=101)
    assert service.response(102)["state"] == "3D_FIX"
    assert service.response(102)["location"]["source"] == "GNSS"
    assert reader.start() is True
    time.sleep(.03)
    assert reader.diag.transport_connected and reader.diag.state == "NO_FIX"
    assert any(state == "NO_FIX" for state,_ in states)
    reader.close()
    assert not reader.diag.transport_connected and reader.diag.state == "NO_RECEIVER"


def test_discovery_without_configured_receiver_is_not_a_random_port_selection():
    service=GnssLocationService(GnssConfig(device_path=""))
    assert service.discover() == {"state":"NO_RECEIVER","candidates":[]}
