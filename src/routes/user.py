from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.core.dependencies import can_view_account, can_update_account, require_role
from src.repositories.user import UserRepository
from src.schemas.user import (
    UserAccountResponse, UserProfileResponse, UserUpdateRequest, 
    UserUpdateStatusRequest, UserUpdateStatusResponse
)
from src.services.user import UserService
from typing import List

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/profile/{username}', response_model=UserProfileResponse)
async def get_user_profile(user = require_role('user'), db: AsyncSession = Depends(get_db)):
    service = UserService(UserRepository(db))
    
    return await service.get_profile_by_username(user.username)

@router.get('/account/{account_id}', response_model=UserAccountResponse)
async def get_user_account(
    user = require_role('user'),
    account = can_view_account(), 
    db: AsyncSession = Depends(get_db)
):
    service = UserService(UserRepository(db))
    
    return await service.get_account(account.id)

@router.put("/{account_id}", response_model=UserAccountResponse)
async def update_account(
    user = require_role('user'),
    update_data: UserUpdateRequest = Body(...),
    account = can_update_account(), 
    db: AsyncSession = Depends(get_db)
):
    service = UserService(UserRepository(db))
    account = await service.get_account(account.id)

    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    return await service.update_account(account.id, update_data)

@router.put("/{account_id}/status", response_model=UserUpdateStatusResponse)
async def update_account_status(
    user = require_role('admin'),
    update_data: UserUpdateStatusRequest = Body(...),
    account = can_update_account(), 
    db: AsyncSession = Depends(get_db)
):
    service = UserService(UserRepository(db))
    account = await service.get_account(account.id)

    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    return await service.update_account_status(account.id, update_data)

@router.get('/', response_model=List[UserAccountResponse])
async def get_all_users(
    user = require_role('admin'),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(UserRepository(db))
    
    return await service.get_all_users()
