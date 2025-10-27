from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    phone_number: str = Field(..., min_length=10)
    password: str = Field(..., min_length=6)

class RegisterRequest(BaseModel):
    full_name: str
    phone_number: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
