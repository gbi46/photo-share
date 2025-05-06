from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.models import Role, User

class UserModel:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_role(self, user_role):
        stmt = select(Role).where(Role.name == user_role)
        result = await self.db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            role = Role(name=user_role)
            self.db.add(role)
            await self.db.flush()

        return role

    async def get_user_by_username(self, username: str):
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()
    
    async def is_active(self, user: User):
        result = await self.db.execute(
            select(User).where(
                and_(User.id == user.id, User.status == 'active')
            )
        )

        user = result.scalars().first()

        print(user)

        if not user:
            return False

        return True
