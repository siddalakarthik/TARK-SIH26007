"""Evidence-backed device identity. Device path/bus/address is a candidate, not proof."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DeviceIdentity:
    transport:str; location:str; manufacturer:str|None=None; product:str|None=None; chip_id:str|None=None; revision:str|None=None; serial_number:str|None=None; vendor_id:str|None=None; product_id:str|None=None; state:str="UNVERIFIED"; evidence_source:str="NONE"
    def verified(self, evidence_source:str)->"DeviceIdentity":
        if not evidence_source:raise ValueError("identity verification requires recorded evidence")
        return DeviceIdentity(**{**self.__dict__,"state":"VERIFIED","evidence_source":evidence_source})
