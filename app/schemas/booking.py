from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from enum import Enum


class BookingStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class BookingBase(BaseModel):
    trip_id: int
    seat_number: int
    total_price: Decimal


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    status: BookingStatus | None = None
    seat_number: int | None = None


class BookingRead(BaseModel):
    id: int
    trip_id: int
    user_id: int
    seat_number: int
    total_price: Decimal
    status: BookingStatus
    created_at: datetime

    class Config:
        orm_mode = True
