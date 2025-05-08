from src.database.models import Role
from src.repositories.role import RoleRepository
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

import pytest

@pytest.mark.asyncio
async def test_get_role_by_name_found(async_fake_db):
    role = Role(id=uuid4(), name="admin")

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = role
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    repo = RoleRepository(async_fake_db)
    result = await repo.get_role_by_name("admin")

    assert result is role
    assert result.name == "admin"
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_role_by_name_not_found(async_fake_db):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    async_fake_db.execute = AsyncMock(return_value=result_mock)

    repo = RoleRepository(async_fake_db)
    result = await repo.get_role_by_name("ghost-role")

    assert result is None
    async_fake_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_role_new(async_fake_db):
    role_name = "moderator"
    new_role = Role(id=uuid4(), name=role_name)

    # mock .refresh() to simulate assigning an ID
    async_fake_db.refresh = AsyncMock(side_effect=lambda r: setattr(r, "id", new_role.id))

    repo = RoleRepository(async_fake_db)
    repo.get_role_by_name = AsyncMock(return_value=None)
    repo.create_role_permissions = AsyncMock()

    # monkeypatch: simulate DB returning Role instance after insert
    async_fake_db.add = AsyncMock()
    async_fake_db.commit = AsyncMock()

    # execute
    result = await repo.create_role(role_name)

    # verify new role created and returned
    assert result.name == role_name
    assert hasattr(result, "id")

    async_fake_db.add.assert_called_once()
    async_fake_db.commit.assert_called_once()
    async_fake_db.refresh.assert_called_once_with(result)
    repo.create_role_permissions.assert_awaited_once_with(role_name)

@pytest.mark.asyncio
async def test_create_role_existing(async_fake_db):
    existing_role = Role(id=uuid4(), name="admin")

    repo = RoleRepository(async_fake_db)
    repo.get_role_by_name = AsyncMock(return_value=existing_role)
    repo.create_role_permissions = AsyncMock()  # should not be called!

    result = await repo.create_role("admin")

    # Should return the existing role without creating a new one
    assert result is existing_role
    async_fake_db.add.assert_not_called()
    async_fake_db.commit.assert_not_called()
    async_fake_db.refresh.assert_not_called()
    repo.create_role_permissions.assert_not_called()
