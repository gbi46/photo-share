from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import Update
from src.database.models import Comment, Post, User
from src.schemas.user import UserAccountResponse, UserProfileResponse, UserUpdateRequest
from uuid import UUID

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_profile_by_username(self, username) -> User:
        post_count_subq = (
            select(func.count(Post.id))
            .where(Post.user_id == User.id)
            .scalar_subquery()
        )

        comment_count_subq = (
            select(func.count(Comment.id))
            .where(Comment.user_id == User.id)
            .scalar_subquery()
        )

        stmt = (
            select(
                User,
                post_count_subq.label("posts_count"),
                comment_count_subq.label("comments_count")
            )
            .options(selectinload(User.roles))
            .where(User.username == username)
        )

        result = await self.db.execute(stmt)

        row = result.first()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        user, posts_count, comments_count = row

        data = {
            **user.__dict__,
            "posts_count": posts_count,
            "comments_count": comments_count,
        }

        return UserProfileResponse(**data)
    
    async def get_user_account(self, user_id: UUID) -> UserAccountResponse:
        stmt = (select(User).where(User.id == user_id))

        result = await self.db.execute(stmt)

        user = result.scalar_one_or_none()

        if not user:
           raise HTTPException(status_code=404, detail="User not found") 
        
        return user
    
    async def update_user(self, account_id: UUID, data: UserUpdateRequest) -> User:
        stmt = Update(User).where(User.id == account_id).values(
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            img_link=data.img_link,
            phone=data.phone,
            updated_at = datetime.now()
        )

        await self.db.execute(stmt)
        await self.db.commit()

        account = await self.get_user_account(account_id)

        return account
