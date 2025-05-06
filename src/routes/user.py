from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.core.dependencies import require_role
from src.repositories.user import UserRepository
from src.schemas.user import UserProfileResponse
from src.services.user import UserService

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/profile/{username}', response_model=UserProfileResponse)
async def get_user_profile(user = require_role('user'), db: AsyncSession = Depends(get_db)):
    service = UserService(UserRepository(db))
    
    return await service.get_profile_by_username(user.username)
