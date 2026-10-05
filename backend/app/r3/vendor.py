"""Documented payload decoders, not guessed board transports.

References and intentional unsupported profiles: docs/R3_VENDOR_FORMATS.md.
"""
import struct
from app.r3.adapters import TiRadarFrame, RadarPoint, Bno085Sample, Lg290pFix
from app.gnss import parse_nmea


def ti_cartesian_points(payload:bytes,*,count:int,frame_number:int,firmware_profile:str,cpu_cycles:int|None=None)->TiRadarFrame:
    """Only reviewed OOB Cartesian point TLV payload (four little-endian floats).

    This is not the AreaScanner polar format, a tracker TLV, or a universal TI
    packet parser. Exact delivered packet header/profile remains G04.
    """
    if type(count) is not int or not 0<=count<=256 or len(payload)!=count*16:
        raise ValueError('TI Cartesian TLV count/length mismatch')
    points=[RadarPoint(x_m=x,y_m=y,z_m=z,radial_velocity_mps=v) for x,y,z,v in struct.iter_unpack('<ffff',payload)]
    return TiRadarFrame(firmware_profile=firmware_profile,frame_number=frame_number,cpu_cycles=cpu_cycles,points=points)


def sh2_sensor_report(report:bytes,*,timestamp_us:int|None=None)->Bno085Sample:
    """Complete SH-2 sensor-report payload, after documented SHTP reassembly.

    Timestamp must come from the vendor SH-2 time processing boundary. A report
    alone is insufficient to reconstruct its epoch/base/delay, so None stays None.
    """
    if not report: raise ValueError('empty SH2 report')
    identifier=report[0]
    if identifier not in {1,2,4,5}: raise ValueError('unsupported SH2 report')
    if len(report)!=(14 if identifier==5 else 10): raise ValueError('truncated/oversized SH2 report')
    values=struct.unpack_from('<hhhh' if identifier==5 else '<hhh',report,4)
    key,scale={1:('acceleration_m_s2',256),2:('angular_velocity_rad_s',512),4:('acceleration_m_s2',256),5:('quaternion_xyzw',16384)}[identifier]
    return Bno085Sample(report_id=identifier,sh2_timestamp_us=timestamp_us,accuracy_status=report[2]&3,**{key:[x/scale for x in values]})


def lg290p_nmea(sentence:str,arrival_ns:int)->Lg290pFix:
    """Reuse existing checksum-validating NMEA parser; never establishes identity.

    Proprietary receiver configuration, RTCM and PPS are separate boundaries.
    Standard NMEA HDOP is deliberately not turned into metre accuracy.
    """
    fix=parse_nmea(sentence,arrival_ns)
    if fix is None: raise ValueError('invalid or unsupported NMEA sentence')
    names={'RTK_FIXED':'RTK_FIXED','RTK_FLOAT':'RTK_FLOAT','DGPS':'DGPS','2D_FIX':'STANDALONE','3D_FIX':'STANDALONE','GNSS_FIX':'STANDALONE','GPS':'STANDALONE'}
    kind=names.get(fix.fix_type,'UNKNOWN')
    if fix.quality.startswith('GGA_QUALITY_'):
        kind={'1':'STANDALONE','2':'DGPS','4':'RTK_FIXED','5':'RTK_FLOAT'}.get(fix.quality.rsplit('_',1)[-1],'NO_FIX')
    valid=kind not in {'UNKNOWN','NO_FIX'}
    return Lg290pFix(fix_type=kind,latitude_deg=fix.latitude_deg if valid else None,longitude_deg=fix.longitude_deg if valid else None,
                    altitude_m=fix.altitude_m if valid else None,satellites=fix.satellites,
                    speed_mps=fix.speed_mps if valid else None,course_deg=fix.heading_deg if valid and fix.speed_mps is not None and fix.speed_mps>0 else None,
                    horizontal_uncertainty_m=fix.horizontal_accuracy_m,receiver_utc=fix.measurement_time_utc)
