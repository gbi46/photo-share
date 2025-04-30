from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = None
