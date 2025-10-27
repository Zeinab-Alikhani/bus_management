from datetime import datetime
from pydantic import BaseModel

class ProfileBase(BaseModel):
    role: str

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileRead(ProfileBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
