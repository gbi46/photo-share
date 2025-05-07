from fastapi.testclient import TestClient
from main import app
from src.database.models import User
from src.routes import cloudinary
from unittest.mock import patch
from uuid import uuid4

import pytest
from io import BytesIO
from fastapi import UploadFile
from unittest.mock import MagicMock
from src.services.cloudinary import UploadFileService

client = TestClient(app)
def fake_current_user():
    FakeRole = type("Role", (), {"name": "user"})
    return User(id=uuid4(), username="neo", status="active", roles=[FakeRole()])

app.dependency_overrides[cloudinary.require_role("user")] = lambda: fake_current_user()

@pytest.mark.asyncio
@patch("src.services.cloudinary.cloudinary.uploader.upload")
@patch("src.services.cloudinary.cloudinary.CloudinaryImage")
async def test_upload_file_success(mock_cloud_image, mock_upload):
    # Arrange
    fake_file = UploadFile(filename="test.jpg", file=BytesIO(b"fake image data"))

    mock_upload.return_value = {
        "public_id": "test_image",
        "version": 123456789
    }

    mock_image_instance = MagicMock()
    mock_image_instance.build_url.return_value = "https://res.cloudinary.com/fake-url"
    mock_cloud_image.return_value = mock_image_instance

    # Act
    result = await UploadFileService.upload_file(
        file=fake_file,
        width=500,
        height=500,
        crop="fill",
        effect="sepia"
    )

    # Assert
    assert result == "https://res.cloudinary.com/fake-url"
    mock_upload.assert_called_once()
    mock_image_instance.build_url.assert_called_once()
