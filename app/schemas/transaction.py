from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from enum import Enum

class TransactionType(str, Enum):
    deposit = "deposit"
    payment = "payment"
    refund = "refund"
    adjustment = "adjustment"

class TransactionBase(BaseModel):
    amount: Decimal
    type: TransactionType
    description: str | None = None

class TransactionCreate(TransactionBase):
    wallet_id: int

class TransactionRead(TransactionBase):
    id: int
    wallet_id: int
    created_at: datetime

    class Config:
        orm_mode = True
