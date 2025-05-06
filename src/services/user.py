from src.database.models import User
from src.repositories.user import UserRepository
from src.schemas.user import (
    UserAccountResponse, UserProfileResponse, UserUpdateRequest, 
    UserUpdateStatusRequest, UserUpdateStatusResponse
)
from uuid import UUID

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.db = user_repo.db

    async def get_profile_by_username(self, username: str) -> UserProfileResponse:
        return await self.user_repo.get_user_profile_by_username(username)
    
    async def get_account(self, user_id: UUID) -> UserAccountResponse:
        return await self.user_repo.get_user_account(user_id)
    
    async def update_account(
        self,
        account_id: UUID,
        data: UserUpdateRequest
    ) -> UserAccountResponse:
        return await self.user_repo.update_user(account_id, data)
    
    async def update_account_status(
        self,
        account_id: UUID,
        data: UserUpdateStatusRequest
    ) -> UserUpdateStatusResponse:
        return await self.user_repo.update_user_status(account_id, data)
