from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

import pytest

@pytest.mark.asyncio
@patch("src.services.cloudinary.UploadFileService.upload_file", new_callable=AsyncMock)
async def test_upload_image_success(mock_upload, async_client: AsyncClient, auth_user_token: str):
    # Arrange
    mock_upload.return_value = "https://cloudinary.com/fake-image.jpg"

    file_content = b"fake image content"
    files = {
        "file": ("test.jpg", file_content, "image/jpeg"),
    }
    data = {
        "width": "500",
        "height": "500",
        "crop": "fill",
        "effect": "sepia",
    }

    headers = {
        "Authorization": f"Bearer {auth_user_token}"
    }

    # Act
    response = await async_client.post(
        "/cloudinary/upload-image",
        files=files,
        data=data,
        headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "image_url" in response.json()
    assert response.json()["image_url"] == "https://cloudinary.com/fake-image.jpg"
    mock_upload.assert_called_once()
