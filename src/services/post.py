from src.database.models import User
from src.repositories.post import PostRepository

class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo
        self.db = post_repo.db

    async def create_post(
        self,
        post_data: dict,
        user: User
    ):
        return await self.post_repo.create(post_data=post_data, user=user)