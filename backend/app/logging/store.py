from __future__ import annotations
import json, sqlite3
from threading import Lock
from pathlib import Path
from app.domain.models import SystemEvent

class EventStore:
    def __init__(self,path:Path):
        path.parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(path,check_same_thread=False); self._lock=Lock(); self.db.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, ts INTEGER, type TEXT, severity TEXT, reason TEXT, payload TEXT)"); self.db.commit()
    def append(self,event:SystemEvent)->None:
        with self._lock:self.db.execute("INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?)",(event.event_id,event.timestamp_ns,event.event_type,event.severity,event.reason,json.dumps(event.payload,sort_keys=True))); self.db.commit()
    def recent(self,limit:int=100)->list[dict]:
        if not 1<=limit<=1_000:raise ValueError("event query limit must be 1..1000")
        with self._lock:rows=self.db.execute("SELECT id,ts,type,severity,reason,payload FROM events ORDER BY ts DESC LIMIT ?",(limit,)).fetchall()
        return [{"event_id":row[0],"timestamp_ns":row[1],"event_type":row[2],"severity":row[3],"reason":row[4],"payload":json.loads(row[5])} for row in rows]
    def close(self)->None:
        with self._lock:self.db.close()
