from datetime import datetime
from src.database.models import Comment, User
from uuid import uuid4
from unittest.mock import MagicMock, AsyncMock

import pytest

@pytest.mark.asyncio
async def test_add_comment(fake_comment_repo, async_fake_db, fake_comment):
    async_fake_db.refresh = AsyncMock()
    async_fake_db.add = MagicMock()
    async_fake_db.commit = AsyncMock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_comment
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    comment_data = MagicMock(message="New comment")
    result = await fake_comment_repo.add_comment(fake_comment.post_id, fake_comment.user_id, comment_data)

    assert result.message == "Test comment"
    async_fake_db.add.assert_called()
    async_fake_db.commit.assert_called()
    async_fake_db.refresh.assert_called()

@pytest.mark.asyncio
async def test_get_comments(fake_comment_repo, async_fake_db):
    post_id = uuid4()
    user = User(id=uuid4(), username="tester")

    fake_comment1 = Comment(
        id=uuid4(),
        post_id=post_id,
        user_id=user.id,
        message="First comment",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user=user
    )
    fake_comment2 = Comment(
        id=uuid4(),
        post_id=post_id,
        user_id=user.id,
        message="Second comment",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user=user
    )

    # Mock scalars().all() chain
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [fake_comment1, fake_comment2]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    comments = await fake_comment_repo.get_comments(post_id)

    assert len(comments) == 2
    assert comments[0].message == "First comment"
    assert comments[1].message == "Second comment"
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_comment_found(fake_comment_repo, async_fake_db):
    comment_id = uuid4()
    user = User(id=uuid4(), username="testuser")
    fake_comment = Comment(
        id=comment_id,
        post_id=uuid4(),
        user_id=user.id,
        message="Sample comment",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user=user
    )

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_comment
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    comment = await fake_comment_repo.get_comment(comment_id)

    assert comment is not None
    assert comment.id == comment_id
    assert comment.message == "Sample comment"
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_comment_success(fake_comment_repo, async_fake_db):
    comment_id = uuid4()
    user = User(id=uuid4(), username="testuser")
    updated_comment = Comment(
        id=comment_id,
        post_id=uuid4(),
        user_id=user.id,
        message="Updated message",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user=user
    )

    # Mock get_comment to simulate return of updated comment
    fake_comment_repo.get_comment = AsyncMock(return_value=updated_comment)

    result = await fake_comment_repo.update(comment_id, "Updated message")

    assert result is not None
    assert result.id == comment_id
    assert result.message == "Updated message"
    async_fake_db.execute.assert_called_once()
    async_fake_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_comment_success(fake_comment_repo, async_fake_db):
    comment_id = uuid4()
    user = User(id=uuid4(), username="testuser")
    comment = Comment(
        id=comment_id,
        post_id=uuid4(),
        user_id=user.id,
        message="To be deleted",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user=user
    )

    fake_comment_repo.get_comment = AsyncMock(return_value=comment)

    result = await fake_comment_repo.delete(comment_id)

    assert result is True
    async_fake_db.execute.assert_called_once()
    async_fake_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_comment_not_found(fake_comment_repo, async_fake_db):
    comment_id = uuid4()

    fake_comment_repo.get_comment = AsyncMock(return_value=None)

    result = await fake_comment_repo.delete(comment_id)

    assert result is False
    async_fake_db.execute.assert_not_called()
    async_fake_db.commit.assert_not_called()
