from fastapi import APIRouter, Body, Depends, HTTPException, status
from src.core.dependencies import user_has_access, require_role
from src.database.db import get_db
from src.database.models import Post, User
from src.repositories.post import PostRepository
from src.services.post import PostService
from src.services.qr import QrCodeService
from src.schemas.post import PostCreateModel, PostCreateResponse, PostResponse, PostUpdateRequest
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

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

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post: Post = user_has_access('update'), 
    update_data: PostUpdateRequest = Body(...),
    user: User = require_role('user'),
    db: AsyncSession = Depends(get_db)
):
    service = PostService(PostRepository(db))
    post = await service.get_post_by_id(post.id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if not await service.update_post(post.id, update_data.description):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return await service.update_post(post.id, update_data.description)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = PostService(PostRepository(db))
    
    return await service.get_post_by_id(post_id)

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    db: AsyncSession = Depends(get_db), 
):
    service = PostService(PostRepository(db))
    
    return await service.get_all_posts()

@router.post("/generate-qr-code")
async def generate_qr_code_from_url(
    url: str = Body(..., embed=True),
    user: User = require_role('user'),
):
    try:
        qr_code_data = QrCodeService.generate_qr_code(url)
        return qr_code_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"QR generation failed: {str(e)}")
