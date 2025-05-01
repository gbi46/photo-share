from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import security
from src.database.models import User, UserStatusEnum
from src.models.user import UserModel
from src.schemas.user import UserCreate

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_user(self, user_data: UserCreate, user_role: str):
        password = security.get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=password,
            status=UserStatusEnum.active
        )

        user_model = UserModel(self.db)
        role = await user_model.add_role(user_role)
        
        new_user.roles.append(role)

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return True
