from typing import Optional, List, Sequence

from pydantic import BaseModel

class AZRequest(BaseModel):
    summit_ref: str
    summit_lat: float
    summit_long: float
    summit_alt: int
    deg_delta: float
    sota_summit_alt_thres: int


class AZResponse(BaseModel):
    az: Optional[str] = None


class AZGPXRequest(BaseModel):
    summit_ref: str
    summit_lat: float
    summit_long: float
    summit_alt: int
    deg_delta: float
    sota_summit_alt_thres: int

class AZGPXResponse(BaseModel):
    az_gpx: Optional[str] = None
