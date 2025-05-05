from pydantic import BaseModel
from src.schemas.user import UserShortResponse
from uuid import UUID
from datetime import datetime

class CommentCreateModel(BaseModel):
    message: str

    model_config = {
        "from_attributes": True 
    }

class CommentResponse(BaseModel):
    id: UUID
    user_id: UUID
    post_id: UUID
    message: str
    created_at: datetime
    updated_at: datetime
    user: UserShortResponse

    model_config = {
        "from_attributes": True 
    }
