from datetime import datetime
from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict
from src.database.models import UserStatusEnum
from src.schemas.role import RoleResponse
from typing import Optional
from uuid import UUID

class UserLogin(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class UserAccountResponse(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    img_link: Optional[str]
    phone: Optional[str]
    status: UserStatusEnum
    created_at: datetime
    roles: list[RoleResponse]

    model_config = ConfigDict(from_attributes=True)

class UserProfileResponse(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    img_link: Optional[str]
    phone: Optional[str]
    status: UserStatusEnum
    created_at: datetime
    posts_count: int
    comments_count: int
    roles: list[RoleResponse]

    model_config = ConfigDict(from_attributes=True)

class UserShortResponse(BaseModel):
    id: UUID
    username: Optional[str]
    img_link: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class UserUpdateRequest(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    img_link: Optional[str]
    phone: Optional[str]

    model_config = ConfigDict(from_attributes=True)
