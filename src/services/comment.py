from src.repositories.comment import CommentRepository
from uuid import UUID

class CommentService:
    def __init__(self, comment_repo: CommentRepository):
        self.db = comment_repo.db
        self.comment_repo = comment_repo

    async def add_comment(self, post_id: UUID, user_id: UUID, comment):
        return await self.comment_repo.add_comment(post_id, user_id, comment)

    def get_comments(self, post_id: UUID):
        return self.comment_repo.get_comments(post_id)

    def get_comment(self, comment_id):
        return self.comment_repo.get_comment(comment_id)
