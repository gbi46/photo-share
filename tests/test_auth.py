from src.core.security import security
from src.database.models import User
from src.services.auth import get_current_user
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from uuid import UUID

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
