from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StationTemperature(BaseModel):
    station_id: str
    station_name: str
    county: Optional[str] = None
    town: Optional[str] = None
    lat: float
    lon: float
    altitude_m: Optional[float] = None
    observed_at: datetime
    temperature_c: float
    humidity_percent: Optional[float] = None
    pressure_hpa: Optional[float] = None
    wind_speed_mps: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    precipitation_mm: Optional[float] = None
    weather: Optional[str] = None

class LatestTemperatureResponse(BaseModel):
    source: str
    updated_at: str
    count: int
    stations: List[StationTemperature]
