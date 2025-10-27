from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Union

class WalletBase(BaseModel):
    balance: Union[float, Decimal] = 0.00  # 👈 هم float قبول می‌کنه هم Decimal

class WalletCreate(WalletBase):
    user_id: int

class WalletUpdate(BaseModel):
    balance: Union[float, Decimal]  # 👈 همین‌جا هم این‌طوری بهتره

class WalletRead(WalletBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        orm_mode = True
