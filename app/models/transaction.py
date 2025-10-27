from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base
import enum

class TransactionType(str, enum.Enum):
    deposit = "deposit"
    withdraw = "withdraw"
    payment = "payment"
    refund = "refund"
    adjustment = "adjustment"

class AppTransaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"))
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)  # ✅ نام ستون اصلاح شد
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    wallet = relationship("Wallet", back_populates="transactions")
