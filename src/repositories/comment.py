from datetime import datetime
from src.database.models import Comment
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import Delete, Update

class CommentRepository:
    def __init__(self, db):
        self.db = db

    async def add_comment(self, post_id, user_id, comment):
        new_comment = Comment(
            post_id=post_id, 
            user_id=user_id, 
            message=comment.message,
            created_at=datetime.now(),
            updated_at=datetime.now()   
        )
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)

        result = await self.db.execute(
            select(Comment)
            .where(Comment.id == new_comment.id)
            .options(joinedload(Comment.user))
        )

        return result.scalar_one_or_none()

    async def get_comments(self, post_id) -> list[Comment]:
        stmt = (select(Comment).join(Comment.post)
            .where(Comment.post_id == post_id).order_by(Comment.created_at.desc())
            .options(joinedload(Comment.user))
        )
        result = await self.db.execute(stmt)

        return result.scalars().all()
    
    async def get_comment(self, comment_id: UUID) -> Comment | None:
        result = await self.db.execute(
            select(Comment)
            .where(Comment.id == comment_id)
            .options(joinedload(Comment.user))
        )
        return result.scalar_one_or_none()
    
    async def update(self, comment_id: UUID, message: str) -> Comment | None:
        stmt = Update(Comment).where(Comment.id == comment_id).values(
            message = message,
            updated_at = datetime.now()
        )
        await self.db.execute(stmt)
        await self.db.commit()

        comment = await self.get_comment(comment_id)

        return comment
    
    async def delete(self, comment_id: UUID) -> bool:
        comment = await self.get_comment(comment_id)
        if comment is None:
            return False
        
        stmt = Delete(Comment).where(Comment.id == comment_id)
        
        await self.db.execute(stmt)
        await self.db.commit()
        
        return True
