from fastapi import APIRouter, Depends
from src.core.dependencies import require_role
from src.database.models import User
from src.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.comment import CommentRepository
from src.schemas.comment import CommentCreateModel, CommentResponse
from src.services.comment import CommentService
from uuid import UUID

router = APIRouter(prefix="/posts", tags=["comments"])

@router.post("/{post_id}/comments", response_model=CommentResponse)
async def add_comment(
    post_id: UUID,
    data: CommentCreateModel,
    user: User = require_role("user"),
    db: AsyncSession = Depends(get_db)   
):
    service = CommentService(CommentRepository(db))
    return await service.add_comment(post_id, user.id, data)

@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    post_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = CommentService(CommentRepository(db))
    return await service.get_comments(post_id)

@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = CommentService(CommentRepository(db))
    return await service.get_comment(comment_id)
