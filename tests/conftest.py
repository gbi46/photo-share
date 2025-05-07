
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.core.security import security
from src.database.models import Base, User
from src.database.db import get_db
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import pytest

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

@pytest.fixture
def fake_db():
    return MagicMock()

@pytest.fixture
def fake_current_user():
    return User(id=uuid4(), username="username", status="active")

@pytest.fixture(scope="module", autouse=True)
def setup_user(session):
    user = User(
        username="neo",
        email="neo@example.com",
        password="hashed_password_here",
        status="active"
    )
    session.add(user)
    session.commit()

@pytest.fixture
def get_token(session):
    result = session.execute(select(User).limit(1))
    user = result.scalar_one_or_none()

    token = security.create_token('access', user.id)

    print(f"token from get token: {token}")

    return token

@pytest.fixture
def mock_upload():
    with patch("src.services.cloudinary.UploadFileService.upload_file", new_callable=AsyncMock) as mock:
        yield mock
