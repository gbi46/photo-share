from datetime import datetime
from fastapi import HTTPException
from src.database.models import Post, PostTag, Tag, User
from src.schemas.post import PostCreateModel, PostCreateResponse, PostResponse
from src.schemas.tag import TagsShortResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.expression import Delete, Update
from uuid import UUID

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
    
    async def delete_post(self, post_id: UUID) -> bool:
        stmt = Delete(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
    
    async def get_post(self, post_id: UUID) -> Post:
        stmt = (
            select(Post)
            .options(
                joinedload(Post.user),
                selectinload(Post.tags).selectinload(PostTag.tag),
                selectinload(Post.ratings)
            )
            .where(Post.id == post_id)
        )

        result = await self.db.execute(stmt)

        post = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post_response = PostResponse.model_validate(post)
        
        post_response.avg_rating = (
            round(sum(r.rating for r in post.ratings) / len(post.ratings), 2)
            if post.ratings else None
        )
        post_response.rating_count = len(post.ratings)

        post_response.tags = []
        post_response.tags = [
            TagsShortResponse.model_validate(tag_rel.tag)
            for tag_rel in post.tags
            if tag_rel.tag is not None
        ]

        return post_response
    
    async def update_post(self, post_id: UUID, description: str) -> Post:
        stmt = Update(Post).where(Post.id == post_id).values(
            description=description,
            updated_at = datetime.now()
        )
        await self.db.execute(stmt)
        await self.db.commit()

        post = await self.get_post(post_id)

        return post
    
    async def get_posts(self) -> list[Post]:
        stmt = (select(
            Post
        ).join(Post.user)
        .options(
            joinedload(Post.user),
            selectinload(Post.tags).selectinload(PostTag.tag),
            selectinload(Post.ratings)
        ).order_by(Post.created_at.desc())
        )

        result = await self.db.execute(stmt)

        posts = result.scalars().all()
    
        posts_response = []

        for post in posts:
            avg = round(sum(r.rating for r in post.ratings) / len(post.ratings), 2) if post.ratings else None
            count = len(post.ratings)

            post_response = PostResponse.model_validate(post)
            post_response.avg_rating = avg
            post_response.rating_count = count

            post_response.tags = [
            TagsShortResponse.model_validate(tag_rel.tag)
                for tag_rel in post.tags
                if tag_rel.tag is not None
            ]

            posts_response.append(post_response)

        return posts_response
