from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str




class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None