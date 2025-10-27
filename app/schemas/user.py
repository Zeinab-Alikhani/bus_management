from pydantic import BaseModel
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    phone_number: str

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None

class UserResponse(UserRead):
    message: Optional[str] = None
