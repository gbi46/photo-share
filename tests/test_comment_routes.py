import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from src.database.models import Comment, User, Role
from src.routes.comment import require_role, update_access_dep
from src.schemas.comment import CommentCreateModel, CommentUpdateRequest

client = TestClient(app)

@pytest.fixture
def fake_comment():
    return Comment(
        id=uuid4(),
        post_id=uuid4(),
        user_id=uuid4(),
        message="Old message"
    )

@pytest.fixture
def fake_user():
    return User(
        id=uuid4(),
        username="test_user",
        roles=[Role(id=1, name="user")],
        email="test@example.com",
        password="hashed",
        status="active"
    )

@pytest.fixture(autouse=True)
def override_comment_dependencies(fake_user, fake_comment):
    from src.core.dependencies import get_current_user
    from src.routes.comment import update_access_dep, require_role

    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[require_role("user")] = lambda: fake_user
    app.dependency_overrides[update_access_dep] = lambda: fake_comment

    yield
    app.dependency_overrides.clear()

@patch("src.routes.comment.CommentService")
def test_add_comment(mock_service_class, fake_user, fake_comment):
    post_id = uuid4()
    payload = {"message": "Nice post!"}

    mock_service = mock_service_class.return_value
    expected_response = {
        "id": str(uuid4()),
        "post_id": str(post_id),
        "user_id": str(fake_user.id),
        "message": "Nice post!",
        "created_at": "2025-05-08T12:00:00",
        "updated_at": "2025-05-08T12:00:00",
        "user": {
            "id": str(fake_user.id),
            "username": fake_user.username,
            "img_link": "http://example.com/image.jpg",
        }
    }
    mock_service.add_comment = AsyncMock(return_value=expected_response)

    # Call route
    response = client.post(f"/posts/{post_id}/comments", json=payload)

    # Validate
    assert response.status_code == 200
    assert response.json()["message"] == "Nice post!"
    mock_service.add_comment.assert_awaited_once_with(post_id, fake_user.id, CommentCreateModel(**payload))

@patch("src.routes.comment.CommentService")
def test_get_comments(mock_service_class):
    post_id = uuid4()

    expected_comments = [
        {
            "id": str(uuid4()),
            "post_id": str(post_id),
            "user_id": str(uuid4()),
            "message": "Test comment",
            "created_at": "2025-05-08T12:00:00",
            "updated_at": "2025-05-08T12:00:00",
            "user": {
                "id": str(uuid4()),
                "username": "commenter_user",
                "img_link": "http://example.com/commenter_image.jpg",
            }
        }
    ]

    mock_service = mock_service_class.return_value
    mock_service.get_comments = AsyncMock(return_value=expected_comments)

    response = client.get(f"/posts/{post_id}/comments")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["message"] == "Test comment"
    mock_service.get_comments.assert_awaited_once_with(post_id)

@patch("src.routes.comment.CommentService")
def test_get_comment(mock_service_class):
    comment_id = uuid4()

    expected_comment = {
        "id": str(comment_id),
        "post_id": str(uuid4()),
        "user_id": str(uuid4()),
        "message": "Test comment detail",
        "created_at": "2025-05-08T12:00:00",
        "updated_at": "2025-05-08T12:00:00",
        "user": {
            "id": str(uuid4()),
            "username": "commenter",
            "img_link": "http://example.com/commenter_image.jpg",
        }
    }

    mock_service = mock_service_class.return_value
    mock_service.get_comment = AsyncMock(return_value=expected_comment)

    response = client.get(f"/posts/comments/{comment_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(comment_id)
    assert response.json()["message"] == "Test comment detail"
    mock_service.get_comment.assert_awaited_once_with(comment_id)
