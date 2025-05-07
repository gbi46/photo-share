import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.services.post import PostService
from src.database.models import User

@pytest.mark.asyncio
async def test_create_post():
    mock_repo = MagicMock()
    mock_repo.create = AsyncMock(return_value={"id": uuid4(), "description": "test"})
    service = PostService(mock_repo)

    user = User(id=uuid4())
    post_data = {"description": "test"}
    result = await service.create_post(post_data, user)

    assert result["description"] == "test"
    mock_repo.create.assert_awaited_once_with(post_data=post_data, user=user)

@pytest.mark.asyncio
async def test_get_post_by_id():
    mock_repo = MagicMock()
    mock_post_id = uuid4()
    mock_repo.get_post = AsyncMock(return_value={"id": mock_post_id})
    service = PostService(mock_repo)

    result = await service.get_post_by_id(mock_post_id)
    assert result["id"] == mock_post_id
    mock_repo.get_post.assert_awaited_once_with(mock_post_id)

@pytest.mark.asyncio
async def test_delete_post():
    mock_repo = MagicMock()
    mock_repo.delete_post = AsyncMock(return_value=True)
    service = PostService(mock_repo)

    result = await service.delete_post(uuid4())
    assert result is True
    mock_repo.delete_post.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_post():
    mock_repo = MagicMock()
    mock_post_id = uuid4()
    mock_repo.update_post = AsyncMock(return_value={"id": mock_post_id, "description": "updated"})
    service = PostService(mock_repo)

    result = await service.update_post(mock_post_id, "updated")
    assert result["description"] == "updated"
    mock_repo.update_post.assert_awaited_once_with(mock_post_id, "updated")

@pytest.mark.asyncio
async def test_get_all_posts():
    mock_repo = MagicMock()
    mock_repo.get_posts = AsyncMock(return_value=[{"id": uuid4()}, {"id": uuid4()}])
    service = PostService(mock_repo)

    result = await service.get_all_posts()
    assert len(result) == 2
    mock_repo.get_posts.assert_awaited_once()
