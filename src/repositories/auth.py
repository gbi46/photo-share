from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import security
from src.database.models import User, UserStatusEnum
from src.models.user import UserModel
from src.repositories.role import RoleRepository
from src.schemas.user import UserCreate

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user_roles(self, user: User, role: str):
        user_model = UserModel(self.db)

        if not role == 'user':
            default_role = await user_model.add_role('user')
            default_role_name = default_role.name

            user.roles.append(default_role)

            role_repo = RoleRepository(self.db)
            await role_repo.create_role(default_role_name)
            await role_repo.create_role_permissions(default_role_name)

        await role_repo.create_role(role)
        await role_repo.create_role_permissions(role)

        inp_role = await user_model.add_role(role)
        user.roles.append(inp_role)

        return user.roles
        
    async def create_user(self, user_data: UserCreate, user_role: str):
        password = security.get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=password,
            status=UserStatusEnum.active
        )
        
        new_user.roles = await self.create_user_roles(new_user, user_role)

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return True
