import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_signup_success(async_client: AsyncClient, test_db: AsyncSession):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "StrongP@ssw0rd!"
    }

    response = await async_client.post("/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_signup_duplicate(async_client: AsyncClient, test_db: AsyncSession):
    # Create user first
    payload = {
        "username": "existinguser",
        "email": "existing@example.com",
        "password": "123456"
    }

    await async_client.post("/auth/signup", json=payload)

    # Try again
    response = await async_client.post("/auth/signup", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_db: AsyncSession):
    signup_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "secret123"
    }
    await async_client.post("/auth/signup", json=signup_data)

    login_data = {
        "username": "loginuser",
        "password": "secret123"
    }
    response = await async_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_password(async_client: AsyncClient, test_db: AsyncSession):
    signup_data = {
        "username": "wrongpassuser",
        "email": "wrong@example.com",
        "password": "rightpass"
    }
    await async_client.post("/auth/signup", json=signup_data)

    response = await async_client.post("/auth/login", json={
        "username": "wrongpassuser",
        "password": "wrongpass"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_login_user_not_found(async_client: AsyncClient):
    response = await async_client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "nopass"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"
