from src.database.db import get_db
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.models.user import UserModel
from src.repositories.auth import AuthRepository
from src.schemas.user import UserCreate
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def signup(user: UserCreate = Body(...), db: AsyncSession = Depends(get_db)):
    user_model = UserModel(db)
    user_exists = await user_model.get_user_by_username(user.username)

    if user_exists:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    first_user_exists = (await db.execute(select(User))).scalars().first()

    if not first_user_exists:
        user_role = 'admin'
    else:
        user_role = 'user'

    user_data = user
    user_data.role = user_role

    service = AuthService(AuthRepository(db))

    return await service.create(user_data)