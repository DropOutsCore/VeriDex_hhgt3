"""Unit tests for Phase 16 Security & Privacy Safeguards."""

import pytest
from app.utils.security_utils import is_ssrf_safe_url, validate_image_payload, MAX_ALLOWED_IMAGE_SIZE_BYTES


def test_ssrf_protection_loopback_urls():
    """Verify SSRF protection blocks loopback, private, and internal URLs."""
    # Loopback IP
    safe, reason = is_ssrf_safe_url("http://127.0.0.1/admin")
    assert safe is False
    assert "loopback" in reason.lower() or "ssrf" in reason.lower()

    # Localhost domain
    safe, reason = is_ssrf_safe_url("http://localhost:8000/internal")
    assert safe is False

    # Metadata service
    safe, reason = is_ssrf_safe_url("http://169.254.169.254/latest/meta-data/")
    assert safe is False

    # Prohibited scheme
    safe, reason = is_ssrf_safe_url("file:///etc/passwd")
    assert safe is False
    assert "scheme" in reason.lower()


def test_ssrf_protection_valid_public_urls():
    """Verify SSRF protection allows valid public HTTPS URLs."""
    safe, reason = is_ssrf_safe_url("https://wikipedia.org/wiki/Test")
    assert safe is True
    assert reason is None


def test_validate_image_payload_valid_jpeg():
    """Verify image validation succeeds for valid JPEG magic bytes."""
    jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF" + (b"\x00" * 100)
    valid, msg = validate_image_payload(jpeg_bytes)
    assert valid is True
    assert msg is None


def test_validate_image_payload_empty_bytes():
    """Verify image validation fails for empty byte payload."""
    valid, msg = validate_image_payload(b"")
    assert valid is False
    assert "empty" in msg.lower()


def test_validate_image_payload_oversized():
    """Verify image validation fails for payloads exceeding 10MB limit."""
    huge_data = b"\xff\xd8\xff" + (b"\x00" * (MAX_ALLOWED_IMAGE_SIZE_BYTES + 1024))
    valid, msg = validate_image_payload(huge_data)
    assert valid is False
    assert "exceeds" in msg.lower()
