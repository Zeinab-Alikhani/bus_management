from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base
import enum

class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"))
    seat_number = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatus, name="booking_status_enum"), default=BookingStatus.pending)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")
