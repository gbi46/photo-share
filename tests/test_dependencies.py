from fastapi import HTTPException
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies import can_update_account, user_has_access_to_comment
from src.database.models import Comment, Post, Role, User
from src.core.dependencies import user_has_access

import pytest

@pytest.mark.asyncio
async def test_user_has_access_as_author():
    post_id = uuid4()
    user_id = uuid4()
    post = Post(id=post_id, user_id=user_id)

    user = User(id=user_id, roles=[])

    db = AsyncMock(spec=AsyncSession)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = post
    db.execute.return_value = result_mock

    checker_dep = user_has_access("update").dependency
    result = await checker_dep(post_id=post_id, db=db, user=user)

    assert result == post

@pytest.mark.asyncio
async def test_user_has_access_forbidden():
    post_id = uuid4()
    post = Post(id=post_id, user_id=uuid4())
    user = User(id=uuid4(), roles=[])

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = post
    db.execute.return_value = result_mock

    checker = user_has_access("delete").dependency

    with pytest.raises(HTTPException) as exc_info:
        await checker(post_id=post_id, db=db, user=user)

    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_user_has_access_to_comment_as_author():
    # Setup
    comment_id = uuid4()
    user_id = uuid4()
    comment = Comment(id=comment_id, user_id=user_id)

    user = User(id=user_id, roles=[])

    db = AsyncMock(spec=AsyncSession)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = comment
    db.execute.return_value = result_mock

    checker = user_has_access_to_comment("update").dependency

    result = await checker(comment_id=comment_id, db=db, user=user)

    assert result == comment

@pytest.mark.asyncio
async def test_can_update_own_account():
    user_id = uuid4()
    user = User(id=user_id, roles=[])
    account = User(id=user_id)

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = account
    db.execute.return_value = result_mock

    checker = can_update_account().dependency

    result = await checker(account_id=user_id, db=db, user=user)

    assert result == account

@pytest.mark.asyncio
async def test_can_update_account_as_admin():
    account_id = uuid4()
    user = User(id=uuid4(), roles=[Role(name="admin")])
    account = User(id=account_id)

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = account
    db.execute.return_value = result_mock

    checker = can_update_account().dependency

    result = await checker(account_id=account_id, db=db, user=user)

    assert result == account

@pytest.mark.asyncio
async def test_can_update_account_not_found():
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    user = User(id=uuid4(), roles=[])

    checker = can_update_account().dependency

    with pytest.raises(HTTPException) as exc_info:
        await checker(account_id=uuid4(), db=db, user=user)

    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_can_update_account_forbidden():
    account_id = uuid4()
    user = User(id=uuid4(), roles=[])
    account = User(id=account_id)

    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = account
    db.execute.return_value = result_mock

    checker = can_update_account().dependency

    with pytest.raises(HTTPException) as exc_info:
        await checker(account_id=account_id, db=db, user=user)

    assert exc_info.value.status_code == 403
