from datetime import datetime
from fastapi import HTTPException
from src.database.models import User, Role
from src.schemas.user import UserProfileResponse
from src.repositories.user import UserRepository
from src.schemas.user import UserUpdateRequest, UserUpdateStatusRequest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

import pytest

@pytest.mark.asyncio
async def test_get_user_account(db_session, test_user):
    repo = UserRepository(db_session)

    result = await repo.get_user_account(test_user.id)

    assert result.username == test_user.username
    assert result.email == test_user.email

@pytest.mark.asyncio
async def test_get_user_account_not_found(async_fake_db):
    user_id = uuid4()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    repo = UserRepository(async_fake_db)

    with pytest.raises(HTTPException) as exc_info:
        await repo.get_user_account(user_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_profile_by_username_success(async_fake_db):
    username = "testuser"

    # Fake User-Objekt
    user = User(
        id=uuid4(),
        username=username,
        first_name="Test",
        last_name="User",
        img_link="http://example.com/image.jpg",
        phone="123456789",
        status="active",
        email="test@example.com",
        password="hashed",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        roles=[Role(id=1, name="user")]
    )

    posts_count = 5
    comments_count = 12

    result_mock = MagicMock()
    result_mock.first.return_value = (user, posts_count, comments_count)
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    repo = UserRepository(async_fake_db)

    profile = await repo.get_user_profile_by_username(username)

    assert isinstance(profile, UserProfileResponse)
    assert profile.username == username
    assert profile.first_name == user.first_name
    assert profile.last_name == user.last_name
    assert profile.img_link == user.img_link
    assert profile.phone == user.phone
    assert profile.status == user.status
    assert [r.id for r in profile.roles] == [r.id for r in user.roles]
    assert [r.name for r in profile.roles] == [r.name for r in user.roles]
    assert profile.posts_count == posts_count
    assert profile.comments_count == comments_count
    assert profile.email == user.email
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_profile_by_username_not_found(async_fake_db):
    username = "ghost_user"

    # Simuliere: result.first() gibt None zurück
    result_mock = MagicMock()
    result_mock.first.return_value = None
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    repo = UserRepository(async_fake_db)

    with pytest.raises(HTTPException) as exc_info:
        await repo.get_user_profile_by_username(username)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_user(db_session, test_user):
    repo = UserRepository(db_session)

    username = f"updated_user{datetime.now().strftime('%Y%m%d%H%M%S')}"
    update = UserUpdateRequest(
        username=username,
        first_name="First",
        last_name="Last",
        email=f"{username}@example.com",
        img_link="http://img.com",
        phone="123456"
    )
    updated_user = await repo.update_user(test_user.id, update)
    assert updated_user.username == f"{username}"
    assert updated_user.first_name == "First"
    assert updated_user.last_name == "Last"
    assert updated_user.email == f"{username}@example.com"

@pytest.mark.asyncio
async def test_update_user_status(db_session, test_user):
    repo = UserRepository(db_session)
    status_update = UserUpdateStatusRequest(status="ban")
    updated_user = await repo.update_user_status(test_user.id, status_update)
    assert updated_user.status == "ban"

@pytest.mark.asyncio
async def test_get_all_users(db_session, test_user):
    repo = UserRepository(db_session)
    users = await repo.get_all_users()
    assert len(users) >= 1
