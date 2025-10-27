from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.db import Base

class RoleEnum(str, enum.Enum):
    passenger = "passenger"
    operator = "operator"
    admin = "admin"
    driver = "driver"

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(Enum(RoleEnum), default=RoleEnum.passenger)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 اینجا هم joined
    user = relationship("User", back_populates="profile", lazy="joined")

    driven_trips = relationship("Trip", back_populates="driver")
