from pydantic import BaseModel
from datetime import datetime


class BusCreate(BaseModel):
    plate_number: str
    capacity: int
    operator_id: int | None = None

class BusUpdate(BaseModel):
    plate_number: str | None = None
    capacity: int | None = None
    operator_id: int | None = None    

class BusResponse(BaseModel):
    id: int
    plate_number: str
    capacity: int
    operator_id: int | None
    created_at: datetime

    class Config:
        orm_mode = True
