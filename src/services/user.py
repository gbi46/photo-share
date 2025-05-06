from src.repositories.user import UserRepository
from src.schemas.user import UserProfileResponse

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.db = user_repo.db

    async def get_profile_by_username(self, username: str) -> UserProfileResponse:
        return await self.user_repo.get_user_profile_by_username(username)
