from datetime import datetime
from pydantic import BaseModel, field_validator
from pydantic.config import ConfigDict
from src.conf.config import settings
from src.schemas.tag import TagsShortResponse
from src.schemas.user import UserShortResponse
from typing import List, Optional
from uuid import UUID

class TagModel(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class PostCreateModel(BaseModel):
    title: str
    image_url: str
    description: str
    tags: Optional[List[TagModel]]

    @field_validator('tags', mode='after')
    def max_tags(cls, v):
        if len(v) > settings.MAX_POST_TAGS:
            raise ValueError(f"You can only add up to {settings.MAX_POST_TAGS} tags.")
        return v

    model_config = ConfigDict(from_attributes=True)

class PostCreateResponse(BaseModel):
    id: UUID
    image_url: str

    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    id: UUID
    title: str
    user_id: UUID
    description: Optional[str] = None
    image_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None
    user: Optional[UserShortResponse] = None
    tags: List[TagsShortResponse] = []

    model_config = ConfigDict(from_attributes=True)

class PostUpdateRequest(BaseModel):
    description: Optional[str] = None
