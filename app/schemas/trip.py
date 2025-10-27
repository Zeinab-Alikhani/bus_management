from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TripCreate(BaseModel):
    bus_id: int
    driver_id: Optional[int] = None
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float


class TripUpdate(BaseModel):
    bus_id: Optional[int] = None
    driver_id: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[float] = None


class TripResponse(BaseModel):
    id: int
    bus_id: int
    driver_id: Optional[int]
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    created_at: datetime

    class Config:
        orm_mode = True
TripRead = TripResponse
