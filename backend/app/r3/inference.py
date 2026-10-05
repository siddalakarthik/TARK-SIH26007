"""Bounded inference providers. No accelerator imports or device opens at startup."""
from collections import deque
import hashlib
from pathlib import Path
import time
from threading import Lock
from typing import Callable, Literal
from pydantic import Field, model_validator
from app.r3.contracts import Contract, Count, Nonnegative, Token

class Detection(Contract):
    label: Token
    confidence: float = Field(ge=0,le=1)
    xyxy_normalized: list[float] = Field(min_length=4,max_length=4)

class InferenceResult(Contract):
    input_frame_id: Token
    source_mode: Literal['REAL','SIMULATION','REPLAY']
    capture_time_ns: Count | None
    capture_uncertainty_ns: Count | None
    model_name: Token
    model_version: Token
    model_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    provider: Token
    inference_start_ns: Count
    inference_end_ns: Count
    latency_ns: Count
    postprocessing_version: Token
    detections: list[Detection] = Field(max_length=256)
    @model_validator(mode='after')
    def times(self):
        if self.inference_end_ns<self.inference_start_ns or self.latency_ns!=self.inference_end_ns-self.inference_start_ns:
            raise ValueError('invalid inference timing')
        if (self.capture_time_ns is None)!=(self.capture_uncertainty_ns is None): raise ValueError('incomplete capture relationship')
        if self.capture_time_ns is not None and self.capture_time_ns>self.inference_start_ns: raise ValueError('capture after inference start')
        return self

class InferenceProvider:
    """One call at a time; caller supplies a selected, versioned model pipeline."""
    def __init__(self,name,model_name,model_version,model_sha256,postprocessing_version,runner:Callable,*,clock=time.monotonic_ns,fixture=False):
        self.name=name;self.model_name=model_name;self.model_version=model_version;self.model_hash=model_sha256
        self.postprocessing=postprocessing_version;self.runner=runner;self.clock=clock;self.fixture=fixture
        self.latencies=deque(maxlen=256);self.frames=0;self.failures=0;self.first=None;self.last=None
        self.busy=Lock();self.dropped_frames=0
    def infer(self,frame_id,frame,*,source_mode,capture_time_ns=None,capture_uncertainty_ns=None):
        if not self.busy.acquire(blocking=False):
            self.dropped_frames+=1;raise RuntimeError('INFERENCE_BUSY_FRAME_DROPPED')
        try:return self._infer(frame_id,frame,source_mode=source_mode,capture_time_ns=capture_time_ns,capture_uncertainty_ns=capture_uncertainty_ns)
        finally:self.busy.release()
    def _infer(self,frame_id,frame,*,source_mode,capture_time_ns=None,capture_uncertainty_ns=None):
        if self.fixture and source_mode=='REAL': raise ValueError('fixture inference cannot become physical evidence')
        start=self.clock()
        try:
            detections=[Detection.model_validate(x) for x in self.runner(frame)]
            for d in detections:
                x1,y1,x2,y2=d.xyxy_normalized
                if not 0<=x1<x2<=1 or not 0<=y1<y2<=1: raise ValueError('invalid normalized box')
            end=self.clock()
            if end<start: raise ValueError('inference clock reset')
            result=InferenceResult(input_frame_id=frame_id,source_mode=source_mode,capture_time_ns=capture_time_ns,capture_uncertainty_ns=capture_uncertainty_ns,
                model_name=self.model_name,model_version=self.model_version,model_sha256=self.model_hash,provider=self.name,
                inference_start_ns=start,inference_end_ns=end,latency_ns=end-start,postprocessing_version=self.postprocessing,detections=detections)
        except Exception:
            self.failures+=1;raise
        self.frames+=1;self.latencies.append(end-start);self.first=start if self.first is None else self.first;self.last=end
        return result
    def metrics(self):
        samples=sorted(self.latencies)
        def percentile(p): return samples[min(len(samples)-1,max(0,__import__('math').ceil(len(samples)*p)-1))] if samples else None
        return {'provider':self.name,'frames':self.frames,'failures':self.failures,'dropped_frames':self.dropped_frames,'queue_depth':int(self.busy.locked()),'window':len(samples),
                'p50_latency_ns':percentile(.5),'p95_latency_ns':percentile(.95),
                'fps':self.frames*1e9/(self.last-self.first) if self.last is not None and self.last>self.first else None,
                'hailo_load':None,'temperature':None,'throttling':None,'hardware_verified':False}

class HailoProvider(InferenceProvider):
    """Binds a caller-owned HailoRT InferVStreams context; no automatic PCIe access.

    Model preprocessing and output decoding are model-specific and mandatory.
    The reviewed commissioning owner opens/closes the real SDK context later.
    """
    @classmethod
    def bind(cls,hef_path:Path,expected_sha256:str,*,model_name,model_version,postprocessing_version,
             infer_vstreams,input_name,preprocess,postprocess,**kwargs):
        if hashlib.sha256(hef_path.read_bytes()).hexdigest()!=expected_sha256: raise ValueError('HEF model hash mismatch')
        def run(frame): return postprocess(infer_vstreams.infer({input_name:preprocess(frame)}))
        return cls('HAILORT',model_name,model_version,expected_sha256,postprocessing_version,run,**kwargs)

class CpuReferenceProvider(InferenceProvider):
    """Reference callable is explicitly supplied, not a guessed neural model."""

class FixtureInferenceProvider(InferenceProvider):
    def __init__(self,results_by_frame:dict,**kwargs):
        super().__init__('RECORDED_FIXTURE',runner=lambda frame_id:results_by_frame[frame_id],fixture=True,**kwargs)

class UnavailableInferenceProvider:
    def infer(self,*args,**kwargs): raise RuntimeError('NO_RELEASED_MODEL_OR_RUNTIME')
    def metrics(self): return {'state':'UNAVAILABLE','reason':'NO_RELEASED_MODEL_OR_RUNTIME','hardware_verified':False}
