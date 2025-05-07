from datetime import datetime
from src.repositories.user import UserRepository
from src.schemas.user import UserUpdateRequest, UserUpdateStatusRequest

import pytest

@pytest.mark.asyncio
async def test_get_user_account(db_session, test_user):
    repo = UserRepository(db_session)
    result = await repo.get_user_account(test_user.id)
    assert result.username == f"tester{datetime.now().strftime('%Y%m%d%H%M%S')}"
    assert result.email == f"tester{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

@pytest.mark.asyncio
async def test_update_user(db_session, test_user):
    repo = UserRepository(db_session)
    update = UserUpdateRequest(
        username="updated",
        first_name="First",
        last_name="Last",
        email="updated@example.com",
        img_link="http://img.com",
        phone="123456"
    )
    updated_user = await repo.update_user(test_user.id, update)
    assert updated_user.username == "updated"
    assert updated_user.first_name == "First"
    assert updated_user.email == "updated@example.com"

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
