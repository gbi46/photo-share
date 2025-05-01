from fastapi import APIRouter, Body, Depends, HTTPException, status
from src.core.dependencies import user_has_access, require_role
from src.database.db import get_db
from src.database.models import Post, User
from src.repositories.post import PostRepository
from src.services.post import PostService
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

@router.delete("/{post_id}", response_model=bool)
async def delete_post(
    post: Post = user_has_access('delete'),
    user: User = require_role('user'),
    db: AsyncSession = Depends(get_db),
):
    service = PostService(PostRepository(db))
    post = await service.get_post_by_id(post.id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if not await service.delete_post(post.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )
    
    return True
