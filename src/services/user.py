from src.repositories.user import UserRepository
from src.schemas.user import UserProfileResponse
from uuid import UUID

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.db = user_repo.db

    async def get_profile_by_id(self, user_id: UUID) -> UserProfileResponse:
        return await self.user_repo.get_user_profile(user_id)
