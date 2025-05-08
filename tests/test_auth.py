from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from src.core.security import security
from src.database.models import User
from src.repositories.auth import AuthRepository
from src.schemas.user import UserCreate
from src.services.auth import get_current_user
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID, uuid4

import pytest

@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c

@pytest.mark.asyncio
async def test_signup_user(client):
    payload = {
        "username": f"new_user{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"new_email{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password": "securepassword"
    }

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data == True

@pytest.mark.asyncio
async def test_signup_user_exists(client, db_session):
    existing_user = User(
        username="user2",
        email="user2@example.com",
        password=security.get_password_hash("securepassword"),
        status="active",
    )
    db_session.add(existing_user)
    await db_session.commit()

    payload = {
        "username": "user2",
        "email": "user2@example.com",
        "password": "securepassword"
    }

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

@pytest.mark.asyncio
@patch("src.repositories.auth.security.get_password_hash", return_value="hashed_pass")
@patch.object(AuthRepository, "create_user_roles", new_callable=AsyncMock)
async def test_create_user(mock_create_roles, mock_hash, async_fake_db):
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="supersecret"
    )

    fake_role = MagicMock(name="role")
    mock_create_roles.return_value = [fake_role]

    repo = AuthRepository(async_fake_db)

    async_fake_db.add = AsyncMock()
    async_fake_db.commit = AsyncMock()
    async_fake_db.refresh = AsyncMock()

    result = await repo.create_user(user_data, "user")

    # Assertions
    mock_hash.assert_called_once_with("supersecret")
    mock_create_roles.assert_awaited_once()
    async_fake_db.add.assert_called_once()
    async_fake_db.commit.assert_called_once()
    async_fake_db.refresh.assert_called_once()

    assert result is True

def test_login_user(client):
    payload = {
        "username": f"neo",
        "password": "123456"
    }

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == 'bearer'

def test_login_wrong_password(client):
    payload = {"username": "neo", "password": "wrongpass"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_login_inactive_user(client):
    payload = {"username": "new_user20250507200635", "password": "securepassword"}
    
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not active"

class FakeResult:
    async def scalar_one_or_none(self):
        return User(id=1, email="test@example.com")

class FakeDB:
    async def execute(self, stmt):
        return FakeResult()

@pytest.mark.asyncio
async def test_get_current_user_success():
    user = User(id=UUID, email="test@example.com")
    fake_db = FakeDB()
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

    mock_role_repo.create_role.assert_awaited_once_with("admin")
    mock_role_repo.create_role_permissions.assert_awaited_once_with("admin")
    mock_user_model.add_role.assert_awaited_once_with("admin")
    assert fake_role in result
    assert len(result) == 1
