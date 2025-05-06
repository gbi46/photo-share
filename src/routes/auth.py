from src.core.security import security
from src.database.db import get_db
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.models.user import UserModel
from src.repositories.auth import AuthRepository
from src.schemas.auth import TokenModel
from src.schemas.user import UserCreate, UserLogin
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

    service = AuthService(AuthRepository(db))

    return await service.create(user, user_role)

@router.post("/login", response_model=TokenModel)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user_model = UserModel(db)
    user = await user_model.get_user_by_username(user_data.username)
    if not user or not security.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not await user_model.is_active(user):
        raise HTTPException(status_code=403, detail="User is not active")

    tokens = security.generate_tokens(user.id)
    return tokens
