import io
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from src.database.models import User, Role

client = TestClient(app)

@pytest.fixture
def fake_user():
    return User(
        id="fake-id",
        username="tester",
        roles=[Role(id=1, name="user")],
        email="tester@example.com",
        password="hashed",
        status="active"
    )

@pytest.fixture(autouse=True)
def override_get_current_user(fake_user):
    from src.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield
    app.dependency_overrides.clear()

@patch("src.services.cloudinary.UploadFileService.upload_file", return_value="https://cloudinary.com/test_image.jpg")
def test_upload_image_success(mock_upload_file):
    file = io.BytesIO(b"dummy image data")
    files = {
        "file": ("image.jpg", file, "image/jpeg")
    }
    data = {
        "width": "500",
        "height": "500",
        "crop": "fill",
        "effect": "sepia"
    }

    response = client.post("/cloudinary/upload-image", files=files, data=data)

    assert response.status_code == 200
    assert response.json()["image_url"] == "https://cloudinary.com/test_image.jpg"
    mock_upload_file.assert_called_once()
