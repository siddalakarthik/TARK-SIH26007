"""Read-only LC29H(AA) bring-up diagnostics; never enables TARK traction."""
from __future__ import annotations
import argparse,time
from app.gnss import GnssConfig,GnssLocationService
from app.gnss_driver import GnssReader,discover_candidates,pyserial_opener
def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument('--device');parser.add_argument('--seconds',type=float,default=20);args=parser.parse_args();config=GnssConfig.from_environment();path=args.device or config.device_path
    print({'candidates':discover_candidates(path),'traction':'DISABLED_PHASE_1','mode':'READ_ONLY'})
    if not path: return
    service=GnssLocationService(config);reader=GnssReader(pyserial_opener(path,config.baud,config.serial_timeout_s),service.accept,config.reconnect_interval_s,config.max_line_bytes,raw_log_path=config.raw_log_path if config.raw_log_enabled else None)
    reader.start();end=time.monotonic()+args.seconds
    try:
        while time.monotonic()<end: print({'reader':reader.diag.__dict__,'location':service.response()});time.sleep(1)
    finally: reader.close()
if __name__=='__main__':main()
