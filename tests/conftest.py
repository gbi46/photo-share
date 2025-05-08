
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.security import security
from src.database.models import Base, Comment, User
from src.database.db import get_db
from src.repositories.comment import CommentRepository
from src.services.auth import AuthService
from src.services.user import UserService
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import asyncio, pytest, time

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

@pytest.fixture
def auth_repo(mock_db):
    repo = MagicMock()
    repo.db = mock_db
    repo.create_user = AsyncMock(return_value={"id": 1, "email": "test@example.com"})
    return repo

@pytest.fixture
def auth_service(auth_repo):
    return AuthService(auth_repo)

@pytest.mark.asyncio
async def test_create_user(auth_service, user_payload):
    result = await auth_service.create(user_payload, "user")
    assert result["email"] == "test@example.com"
    auth_service.auth_repo.create_user.assert_awaited_once_with(user_payload, "user")

@pytest.fixture(scope="module")
async def db_engine():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(db_engine):
    async_session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
def fake_comment():
    return Comment(
        id=uuid4(),
        post_id=uuid4(),
        user_id=uuid4(),
        message="Test comment",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user=User(id=uuid4(), username="testuser")
    )

@pytest.fixture
def fake_comment_repo(async_fake_db):
    return CommentRepository(async_fake_db)

@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()

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
def async_fake_db():
    return AsyncMock()

@pytest.fixture
def fake_current_user():
    return User(id=uuid4(), username="username", status="active")

@pytest.fixture
def get_token(session):
    result = session.execute(select(User).limit(1))
    user = result.scalar_one_or_none()

    token = security.create_token('access', user.id)

    print(f"token from get token: {token}")

    return token

@pytest.fixture
async def test_user(db_session):
    time.sleep(1)  # Ensure unique timestamp for username and email
    user = User(
        id=uuid4(),
        username=f"tester{datetime.now().strftime('%Y%m%d%H%M%S')}",
        email=f"tester{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        password="hashedpw",
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def mock_upload():
    with patch("src.services.cloudinary.UploadFileService.upload_file", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
def user_payload():
    return {
        "email": "test@example.com",
        "password": "securepassword"
    }

@pytest.fixture
def user_service(mock_user_repo):
    return UserService(user_repo=mock_user_repo)

@pytest.fixture(scope="session")
async def tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
