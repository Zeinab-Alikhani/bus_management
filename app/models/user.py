from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 اصلاح lazy برای جلوگیری از MissingGreenlet
    profile = relationship(
        "Profile", back_populates="user", uselist=False,
        lazy="joined", cascade="all, delete-orphan"
    )

    wallet = relationship("Wallet", back_populates="user", uselist=False, lazy="select")
    bookings = relationship("Booking", back_populates="user")
    buses = relationship("Bus", back_populates="operator")
