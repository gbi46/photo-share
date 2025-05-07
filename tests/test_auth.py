from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from src.database.models import User

import asyncio, pytest

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

def test_login_user(client):
    payload = {
        "username": f"new_user",
        "password": "securepassword"
    }

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == 'bearer'
