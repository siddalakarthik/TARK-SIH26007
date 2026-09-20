from pathlib import Path
from app.config import Settings
from app.sensors.ld2450.parser import LD2450Parser
from app.services.pipeline import Pipeline
from app.replay.engine import replay, compare
from app.communication.esp32.protocol import ESP32Client, decode_frame

SETTINGS=Settings.from_file(Path(__file__).parents[2]/"config"/"phase1.json")
class MemoryTransport:
    def __init__(self): self.frames=[]
    def write(self,frame): self.frames.append(frame)

def test_simulated_radar_to_decision_command_and_replay():
    raw=b'SIM1 {"detections":[{"id":7,"x_m":3.0,"y_m":0.0,"velocity_mps":-1.0,"quality":0.9}]}\n'
    parser=LD2450Parser(); ts=1_000_000_000; p=Pipeline(SETTINGS)
    decision=p.ingest(parser.parse(raw,ts),ts); command=p.command(decision,ts)
    transport=MemoryTransport(); result=ESP32Client(transport).submit(command,ts)
    assert result.accepted and command.left_command==command.right_command==0
    assert decode_frame(transport.frames[0])[1]["payload"]["configuration_hash"]==SETTINGS.configuration_hash
    recorded=replay([raw],Pipeline(SETTINGS),[ts]); assert recorded.result=="MATCH"
    assert compare(recorded.decisions,recorded.decisions).result=="MATCH"

