from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database.models import Comment, Post, User
from src.schemas.user import UserProfileResponse

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_profile(self, user_id) -> User:
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
            .where(User.id == user_id)
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
