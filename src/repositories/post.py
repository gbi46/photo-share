from datetime import datetime
from src.database.models import Post, PostTag, Tag, User
from src.schemas.post import PostCreateModel, PostCreateResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
            self, 
            post_data: PostCreateModel,
            user: User
        ) -> Post:

        post = Post(
            user_id=user.id, 
            title=post_data.title, 
            description=post_data.description,
            image_url=post_data.image_url,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )

        self.db.add(post)
        await self.db.flush()

        tag_names = post_data.tags

        for tag_model in tag_names:
            stmt = select(Tag).where(Tag.name == tag_model.name)
            result = await self.db.execute(stmt)
            tag = result.scalar_one_or_none()

            if not tag:
                tag = Tag(name=tag_model.name)
                self.db.add(tag)
                await self.db.flush()

            stmt = select(PostTag).where(
                PostTag.post_id == post.id, 
                PostTag.tag_name == tag_model.name
            )
            result = await self.db.execute(stmt)
            post_tag_exists = result.scalar_one_or_none()

            if not post_tag_exists:
                post_tag = PostTag(post_id=post.id, tag_name=tag_model.name)
                self.db.add(post_tag)
                
            await self.db.commit()
            await self.db.refresh(post)
        post_response = PostCreateResponse.model_validate(post)

        return post_response