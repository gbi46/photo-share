from src.database.models import User
from src.repositories.post import PostRepository
from src.schemas.post import PostResponse
from typing import List
from uuid import UUID

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
    
    async def get_post_by_id(self, post_id: UUID) -> PostResponse:
        return await self.post_repo.get_post(post_id)
    
    async def delete_post(self, post_id: UUID) -> bool:
        return await self.post_repo.delete_post(post_id)
    
    async def update_post(
        self,
        post_id: UUID,
        description: str = None
    ) -> PostResponse:
        return await self.post_repo.update_post(post_id, description)
    
    async def get_all_posts(self) -> List[PostResponse]:
        return await self.post_repo.get_posts()
