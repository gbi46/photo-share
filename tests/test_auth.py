from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.future import select
from src.core.security import security
from src.database.db import get_db
from src.database.models import User, UserStatusEnum
from src.repositories.auth import AuthRepository
from src.schemas.user import UserCreate
from src.services.auth import get_current_user
from src.services.utils import logger
from unittest.mock import ANY, AsyncMock, patch, MagicMock
from uuid import UUID, uuid4

import pytest

@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c

@pytest.mark.asyncio
async def test_signup_user(client, db_session):
    username = f"user_{datetime.now().strftime('%H%M%S')}"

    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "securepassword"
    }

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 200

    result = await db_session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    data = response.json()
    assert data == True
    logger.info(f"Saved user password (hashed): {user.password}, username: {user.username}")

@pytest.mark.asyncio
@patch("src.routes.auth.UserModel")
async def test_signup_user_already_exists(mock_user_model_class, client):
    mock_user_model = mock_user_model_class.return_value
    mock_user_model.get_user_by_username = AsyncMock(return_value=True)

    payload = {
        "username": "existing_user",
        "email": "test@example.com",
        "password": "securepassword"
    }

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already exists"
    mock_user_model.get_user_by_username.assert_awaited_once_with("existing_user")

@patch("src.routes.auth.UserModel")
@patch("src.routes.auth.AuthService")
async def test_signup_first_user_becomes_admin(mock_auth_service_class, mock_user_model_class, client):
    result_mock = MagicMock()
    
    # Setup
    mock_user_model = mock_user_model_class.return_value
    mock_user_model.get_user_by_username = AsyncMock(return_value=None)

    result_mock.scalars.return_value.first.return_value = None

    async def fake_get_db():
        db = AsyncMock()
        db.execute = AsyncMock(return_value=result_mock)
        yield db

    app.dependency_overrides[get_db] = fake_get_db

    mock_auth_service = mock_auth_service_class.return_value
    mock_auth_service.create = AsyncMock(return_value=True)

    payload = {
        "username": "admin_candidate",
        "email": "admin@example.com",
        "password": "strongpassword"
    }

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 200
    mock_auth_service.create.assert_awaited_once_with(ANY, "admin")

@pytest.mark.asyncio
@patch("src.repositories.auth.security.get_password_hash", return_value="hashed_pass")
@patch.object(AuthRepository, "create_user_roles", new_callable=AsyncMock)
async def test_create_user(mock_create_roles, mock_hash, async_fake_db):
    user_data = UserCreate(
        username=f"testuser{datetime.now().strftime('%Y%m%d%H%M%S')}",
        email=f"test{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        password="123456"
    )

    fake_role = MagicMock(name="role")
    mock_create_roles.return_value = [fake_role]

    repo = AuthRepository(async_fake_db)

    async_fake_db.add = AsyncMock()
    async_fake_db.commit = AsyncMock()
    async_fake_db.refresh = AsyncMock()

    result = await repo.create_user(user_data, "user")

    # Assertions
    mock_hash.assert_called_once_with("123456")
    mock_create_roles.assert_awaited_once()
    async_fake_db.add.assert_called_once()
    async_fake_db.commit.assert_called_once()
    async_fake_db.refresh.assert_called_once()

    assert result is True

def test_login_user(client, test_user):
    payload = {
        "username": "tester20250508172259",
        "password": "123456"
    }

    response = client.post("/auth/login", json=payload)

    print("Rersponse:", response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == 'bearer'

def test_login_wrong_password(client):
    payload = {"username": "user_170058", "password": "wrongpass"}

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_login_inactive_user(client, test_user):
    payload = {"username": "tester20250508172848", "password": "123456"}
    
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not active"

def test_login_user_not_found(client, test_user):

    response = client.post("/auth/login", json={"username": "ghost", "password": "123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

class FakeResult:
    async def scalar_one_or_none(self):
        return User(id=1, email="test@example.com")

class FakeDB:
    async def execute(self, stmt):
        return FakeResult()

@pytest.mark.asyncio
async def test_get_current_user_success():
    user = User(id=uuid4(), email="test@example.com")
    
    # Mock the result of db.execute().scalar_one_or_none() chain
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user

    # Mock the db session
    fake_db = AsyncMock()
    fake_db.execute.return_value = result_mock

    # Create token with user.id
    token = security.create_token('access', user.id)

    result = await get_current_user(token, fake_db)

    print("Result type:", type(result))
    print("Is coroutine?", callable(result))
    print("Result repr:", repr(result))

    assert result.email == "test@example.com"

@pytest.mark.asyncio
@patch("src.repositories.auth.RoleRepository", autospec=True)
@patch("src.repositories.auth.UserModel", autospec=True)
async def test_create_user_roles(mock_user_model_class, mock_role_repo_class):
    # Setup Mock DB und User
    fake_db = AsyncMock()
    user = User(
        id=uuid4(),
        username="tester",
        email="test@example.com",
        password="hashed",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        roles=[]
    )

    mock_role_repo = mock_role_repo_class.return_value
    mock_role_repo.create_role = AsyncMock()
    mock_role_repo.create_role_permissions = AsyncMock()

    mock_user_model = mock_user_model_class.return_value
    fake_role = MagicMock(name="mocked-role")
    mock_user_model.add_role = AsyncMock(return_value=fake_role)

    auth_repo = AuthRepository(fake_db)
    result = await auth_repo.create_user_roles(user, "admin")

    assert mock_user_model.add_role.await_count == 2
    mock_user_model.add_role.assert_any_await("admin")
    mock_user_model.add_role.assert_any_await("user")

    assert fake_role in result
    assert len(result) == 2
