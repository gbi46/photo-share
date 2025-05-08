from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime
from src.database.models import Base, User
from src.repositories.post import PostRepository
from src.schemas.post import PostCreateModel
from src.schemas.tag import TagsShortResponse
from unittest.mock import AsyncMock, MagicMock

import pytest, time

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="module")
async def db_engine():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(db_engine):
    async_session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
async def test_user(db_session):
    time.sleep(1)  # Ensure unique timestamp for username and email
    user = User(
        id=uuid4(),
        username=f"tester{datetime.now().strftime('%Y%m%d%H%M%S')}",
        email=f"tester{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        password="hashedpw",
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_create_post(db_session: AsyncSession, test_user: User):
    repo = PostRepository(db_session)

    post_data = PostCreateModel(
        title="My Post",
        description="Hello world!",
        image_url="http://example.com/image.jpg",
        tags=[TagsShortResponse(name="nature"), TagsShortResponse(name="sunset")]
    )

    post = await repo.create(post_data=post_data, user=test_user)

    assert post.image_url == "http://example.com/image.jpg"

@pytest.mark.asyncio
async def test_get_post(db_session: AsyncSession, test_user: User):
    repo = PostRepository(db_session)

    post_data = PostCreateModel(
        title="Another Post",
        description="Nice view",
        image_url="http://img.com/x.jpg",
        tags=[TagsShortResponse(name="view")]
    )
    created = await repo.create(post_data, test_user)

    result = await repo.get_post(created.id)

    assert result.title == "Another Post"
    assert result.tags[0].name == "view"

@pytest.mark.asyncio
async def test_get_post_not_found(async_fake_db):
    post_id = uuid4()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    repo = PostRepository(async_fake_db)

    with pytest.raises(HTTPException) as exc_info:
        await repo.get_post(post_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Post not found"
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_posts(db_session: AsyncSession, test_user: User):
    repo = PostRepository(db_session)

    result = await repo.get_posts()

    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_update_post(db_session: AsyncSession, test_user: User):
    repo = PostRepository(db_session)

    post_data = PostCreateModel(
        title="Initial",
        description="Initial description",
        image_url="http://x.jpg",
        tags=[]
    )
    post = await repo.create(post_data, test_user)

    updated = await repo.update_post(post.id, "Updated description")

    assert updated.description == "Updated description"

@pytest.mark.asyncio
async def test_delete_post(db_session: AsyncSession, test_user: User):
    repo = PostRepository(db_session)

    post_data = PostCreateModel(
        title="To delete",
        description="to be deleted",
        image_url="http://del.jpg",
        tags=[]
    )
    post = await repo.create(post_data, test_user)

    deleted = await repo.delete_post(post.id)

    assert deleted is True
