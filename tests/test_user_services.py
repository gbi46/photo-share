import pytest
from src.schemas.user import (
    UserAccountResponse, UserProfileResponse, UserUpdateRequest,
    UserUpdateStatusRequest, UserUpdateStatusResponse
)
from uuid import uuid4

@pytest.mark.asyncio
async def test_get_profile_by_username(user_service, mock_user_repo):
    username = "testuser"
    expected_profile = UserProfileResponse(
        username=username, first_name="John", last_name="Doe", img_link=None,
        email="john@gmail.com", phone=None, status="active",
        created_at="2023-10-01T00:00:00Z", posts_count=5, comments_count=10,
        roles=[{"id": 1, "name": "admin"}]
    )
    mock_user_repo.get_user_profile_by_username.return_value = expected_profile

    result = await user_service.get_profile_by_username(username)

    assert result == expected_profile
    mock_user_repo.get_user_profile_by_username.assert_awaited_once_with(username)

@pytest.mark.asyncio
async def test_get_account(user_service, mock_user_repo):
    user_id = uuid4()
    expected_account = UserAccountResponse(
        id=user_id, username="testuser", email="test@example.com", phone=None,
        status="active", created_at="2023-10-01T00:00:00Z", roles=[],
        first_name="John", last_name="Doe", img_link=None
    )
    mock_user_repo.get_user_account.return_value = expected_account

    result = await user_service.get_account(user_id)

    assert result == expected_account
    mock_user_repo.get_user_account.assert_awaited_once_with(user_id)

@pytest.mark.asyncio
async def test_update_account(user_service, mock_user_repo):
    account_id = uuid4()
    update_data = UserUpdateRequest(
        first_name="Jane", last_name="Smith", phone="123456789",
        username="testuser", email="test@example.com", img_link=None
    )
    expected_response = UserAccountResponse(
        id=account_id, username="testuser", email="test@example.com", phone=None,
        status="active", created_at="2023-10-01T00:00:00Z", roles=[],
        first_name="John", last_name="Doe", img_link=None
    )
    mock_user_repo.update_user.return_value = expected_response

    result = await user_service.update_account(account_id, update_data)

    assert result == expected_response
    mock_user_repo.update_user.assert_awaited_once_with(account_id, update_data)

@pytest.mark.asyncio
async def test_update_account_status(user_service, mock_user_repo):
    account_id = uuid4()
    status_data = UserUpdateStatusRequest(status="ban")
    expected_response = UserUpdateStatusResponse(id=account_id, status="ban")

    mock_user_repo.update_user_status.return_value = expected_response

    result = await user_service.update_account_status(account_id, status_data)

    assert result == expected_response
    mock_user_repo.update_user_status.assert_awaited_once_with(account_id, status_data)

@pytest.mark.asyncio
async def test_get_all_users(user_service, mock_user_repo):
    expected_users = [
        UserProfileResponse(
            username="user1", first_name="A", last_name="B", img_link=None,
            email="user1@gmail.com", phone=None, status="active",
            created_at="2023-10-01T00:00:00Z", posts_count=5, comments_count=10,
            roles=[{"id": 1, "name": "admin"}]
        ),
        UserProfileResponse(
            username="user2", first_name="C", last_name="D", img_link=None,
            email="user2@gmail.com", phone=None, status="active",
            created_at="2023-10-01T00:00:00Z", posts_count=5, comments_count=10,
            roles=[{"id": 1, "name": "admin"}]
        ),
    ]
    mock_user_repo.get_all_users.return_value = expected_users

    result = await user_service.get_all_users()

    assert result == expected_users
    mock_user_repo.get_all_users.assert_awaited_once()
