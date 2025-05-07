import pytest
import base64

from src.services.qr import QrCodeService  # Adjust the import path if needed

def test_generate_qr_code():
    # Given
    test_url = "https://example.com"

    # When
    result = QrCodeService.generate_qr_code(test_url)

    # Then
    assert "qr_code" in result
    assert "qr_code_url" in result
    assert result["qr_code_url"] == test_url
    assert result["qr_code"].startswith("data:image/png;base64,")

    # Check if the remaining part is valid base64
    base64_part = result["qr_code"].split(",")[1]
    try:
        base64.b64decode(base64_part)
    except Exception:
        pytest.fail("QR code base64 decoding failed")
