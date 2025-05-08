import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException

from src.services.comment import CommentService
from src.schemas.comment import CommentUpdateRequest
from src.database.models import User


@pytest.fixture
def mock_repo():
    mock = MagicMock()
    mock.get_comment = AsyncMock()
    mock.add_comment = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    mock.get_comments = MagicMock()
    return mock


@pytest.fixture
def comment_service(mock_repo):
    return CommentService(comment_repo=mock_repo)


@pytest.mark.asyncio
async def test_add_comment(comment_service, mock_repo):
    post_id = uuid4()
    user_id = uuid4()
    comment = MagicMock()
    mock_repo.add_comment.return_value = "added_comment"

    result = await comment_service.add_comment(post_id, user_id, comment)
    
    assert result == "added_comment"
    mock_repo.add_comment.assert_awaited_once_with(post_id, user_id, comment)


def test_get_comments(comment_service, mock_repo):
    post_id = uuid4()
    mock_repo.get_comments.return_value = ["comment1", "comment2"]

    result = comment_service.get_comments(post_id)

    assert result == ["comment1", "comment2"]
    mock_repo.get_comments.assert_called_once_with(post_id)


def test_get_comment_success():
    mock_repo = MagicMock()
    mock_repo.get_comment.return_value = "comment1"
    service = CommentService(mock_repo)

    result = service.get_comment(uuid4())
    assert result == "comment1"

@pytest.mark.asyncio
async def test_update_comment(comment_service, mock_repo):
    comment_id = uuid4()
    update_data = CommentUpdateRequest(message="Updated message")
    mock_repo.update.return_value = "updated_comment"

    result = await comment_service.update_comment(comment_id, update_data)

    assert result == "updated_comment"
    mock_repo.update.assert_awaited_once_with(comment_id, "Updated message")

@pytest.mark.asyncio
async def test_delete_comment_success(comment_service, mock_repo):
    comment_id = uuid4()
    user = User(id=uuid4())
    
    mock_repo.get_comment.return_value = "some_comment"
    mock_repo.delete.return_value = True

    result = await comment_service.delete_comment(comment_id, user)

    assert result is True
    mock_repo.get_comment.assert_awaited_once_with(comment_id)
    mock_repo.delete.assert_awaited_once_with(comment_id)

@pytest.mark.asyncio
async def test_delete_comment_not_found(comment_service, mock_repo):
    comment_id = uuid4()
    user = User(id=uuid4())

    mock_repo.get_comment.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await comment_service.delete_comment(comment_id, user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Comment not found"
