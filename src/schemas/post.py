from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import List
from uuid import UUID

class TagModel(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class PostCreateModel(BaseModel):
    title: str
    image_url: str
    description: str
    tags: List[TagModel]

    model_config = ConfigDict(from_attributes=True)

class PostCreateResponse(BaseModel):
    id: UUID
    image_url: str

    model_config = ConfigDict(from_attributes=True)