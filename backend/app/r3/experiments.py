"""Small local experiment registry. No source-control or hardware write authority."""
import json
import sqlite3
from pathlib import Path
from threading import RLock
from pydantic import Field
from app.r3.contracts import Contract, Token


class Experiment(Contract):
    experiment_id: Token
    title: str = Field(min_length=1,max_length=200)
    scenario: Token
    operator: Token
    date: Token
    hardware_profile: Token
    configuration_bundle: Token
    calibration_bundle: list[Token] = Field(max_length=32)
    software_version: Token
    expected_sources: list[Token] = Field(min_length=1,max_length=32)
    visibility_condition: Token
    notes: str = Field(max_length=2000)


class ExperimentStore:
    def __init__(self,path:Path):
        self.db=sqlite3.connect(path,check_same_thread=False); self.lock=RLock(); self.active=None
        self.db.execute('CREATE TABLE IF NOT EXISTS r3_experiments (id TEXT PRIMARY KEY, status TEXT NOT NULL, metadata TEXT NOT NULL, recording_id TEXT, summary TEXT)')
        self.db.execute("UPDATE r3_experiments SET status='INTERRUPTED' WHERE status='ACTIVE'"); self.db.commit()
    def start(self,item:Experiment):
        with self.lock:
            if self.active: raise ValueError('an experiment is already active')
            if self.db.execute('SELECT COUNT(*) FROM r3_experiments').fetchone()[0]>=1000: raise ValueError('experiment catalog full; archive explicitly')
            try:
                self.db.execute('INSERT INTO r3_experiments VALUES (?,?,?,NULL,NULL)',(item.experiment_id,'ACTIVE',item.model_dump_json())); self.db.commit()
            except sqlite3.Error as error:
                self.db.rollback(); raise ValueError('experiment storage failed or ID already exists') from error
            self.active=item.experiment_id
            return self.current()
    def attach(self,recording_id:str):
        with self.lock:
            if self.active:
                self.db.execute('UPDATE r3_experiments SET recording_id=? WHERE id=?',(recording_id,self.active)); self.db.commit()
    def finish(self,summary:dict):
        with self.lock:
            if not self.active: raise ValueError('no active experiment')
            identifier=self.active
            self.db.execute("UPDATE r3_experiments SET status='COMPLETE', summary=? WHERE id=?",(json.dumps(summary,allow_nan=False),identifier)); self.db.commit(); self.active=None
            return next(row for row in self.list() if row['experiment_id']==identifier)
    def list(self):
        with self.lock: rows=self.db.execute('SELECT id,status,metadata,recording_id,summary FROM r3_experiments ORDER BY rowid DESC LIMIT 1000').fetchall()
        return [{'experiment_id':a,'status':b,'metadata':json.loads(c),'recording_id':d,'summary':json.loads(e) if e else None} for a,b,c,d,e in rows]
    def current(self): return next((row for row in self.list() if row['experiment_id']==self.active),None)
    def close(self):
        with self.lock: self.db.close()
