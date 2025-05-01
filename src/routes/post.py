from src.core.dependencies import require_role
from src.database.db import get_db
from src.database.models import User
from src.repositories.post import PostRepository
from src.services.post import PostService
from fastapi import APIRouter, Body, Depends
from src.schemas.post import PostCreateModel, PostCreateResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/posts', tags=['posts'])

@router.post("/", response_model=PostCreateResponse)
async def create_post(
    post_data: PostCreateModel = Body(...),
    user: User = require_role('user'),
    db: AsyncSession = Depends((get_db))
): 

    service = PostService(PostRepository(db))
    return await service.create_post(post_data=post_data, user=user)
