from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict
from typing import Optional
from uuid import UUID

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserShortResponse(BaseModel):
    id: UUID
    username: Optional[str]
    img_link: Optional[str]

    model_config = ConfigDict(from_attributes=True)
