from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime
from sqlalchemy import DateTime

class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 
    # 👇 ارتباط درست با کاربر (اپراتور)
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    operator = relationship("User", back_populates="buses")
    trips = relationship("Trip", back_populates="bus")
