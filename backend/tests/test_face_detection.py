"""Unit & Integration Test Suite for VERIDEX Phase 1 (Face Detection).

Tests all face detection features and edge cases:
1. Single face image detection
2. No-face image detection
3. Multiple face image detection
4. Blurry face image handling
5. Invalid / corrupt image handling
6. Empty payload handling
7. Face ROI cropping utility
8. Face detection validation utility
9. REST API POST /api/scan endpoint with multipart file upload
"""

import os
import sys
import pytest
import numpy as np
from fastapi.testclient import TestClient

# Ensure backend and project root are in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.services.face_service import (
    detect_faces,
    extract_face,
    validate_face_detection,
)
from app.models.face_schemas import FaceDetectionResult
from examples.setup_test_assets import setup_test_assets, EXAMPLES_DIR

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Ensure test assets exist prior to running test suite."""
    setup_test_assets()


# -------------------------------------------------------------------
# Service Unit Tests
# -------------------------------------------------------------------

def test_detect_no_face():
    """Test face detection on an image containing no faces."""
    no_face_path = os.path.join(EXAMPLES_DIR, "no_face.jpg")
    assert os.path.exists(no_face_path), f"Test asset missing: {no_face_path}"

    with open(no_face_path, "rb") as f:
        result = detect_faces(f.read())

    assert isinstance(result, FaceDetectionResult)
    assert result.face_detected is False
    assert result.face_count == 0
    assert len(result.faces) == 0
    assert result.error is None


def test_detect_single_face():
    """Test face detection on an image containing one face."""
    single_face_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    if not os.path.exists(single_face_path):
        pytest.skip("Test image single_face.jpg not available.")

    with open(single_face_path, "rb") as f:
        result = detect_faces(f.read())

    assert isinstance(result, FaceDetectionResult)
    assert result.face_detected is True
    assert result.face_count >= 1
    assert len(result.faces) >= 1

    face = result.faces[0]
    assert 0.0 <= face.confidence <= 1.0
    assert len(face.bbox) == 4
    # Bounding box values [x, y, w, h] must be non-negative ints
    assert face.bbox[2] > 0 and face.bbox[3] > 0
    assert face.landmarks is not None
    assert len(face.landmarks.right_eye) == 2
    assert len(face.landmarks.left_eye) == 2
    assert len(face.landmarks.nose_tip) == 2
    assert len(face.landmarks.right_mouth) == 2
    assert len(face.landmarks.left_mouth) == 2


def test_detect_multiple_faces():
    """Test face detection on an image containing multiple faces."""
    multi_face_path = os.path.join(EXAMPLES_DIR, "multi_face.jpg")
    if not os.path.exists(multi_face_path):
        pytest.skip("Test image multi_face.jpg not available.")

    with open(multi_face_path, "rb") as f:
        result = detect_faces(f.read())

    assert isinstance(result, FaceDetectionResult)
    assert result.face_detected is True
    assert result.face_count >= 2
    assert len(result.faces) >= 2


def test_detect_blurry_face():
    """Test face detection on a blurred face image does not crash."""
    blurry_path = os.path.join(EXAMPLES_DIR, "blurry_face.jpg")
    if not os.path.exists(blurry_path):
        pytest.skip("Test image blurry_face.jpg not available.")

    with open(blurry_path, "rb") as f:
        result = detect_faces(f.read())

    assert isinstance(result, FaceDetectionResult)
    # Blurry image should either detect lower confidence face or report no face without throwing an exception
    assert isinstance(result.face_detected, bool)


def test_detect_invalid_image_bytes():
    """Test error handling when passing corrupted non-image binary data."""
    invalid_bytes = b"CORRUPTED_NON_IMAGE_BINARY_DATA_12345"
    result = detect_faces(invalid_bytes)

    assert isinstance(result, FaceDetectionResult)
    assert result.face_detected is False
    assert result.face_count == 0
    assert result.error is not None
    assert "Failed to decode" in result.error or "Invalid or corrupted" in result.error


def test_detect_empty_bytes():
    """Test error handling when passing empty bytes (0 length)."""
    result = detect_faces(b"")
    assert isinstance(result, FaceDetectionResult)
    assert result.face_detected is False
    assert result.face_count == 0
    assert result.error == "Received empty image bytes payload."


def test_extract_face_crop():
    """Test extract_face ROI crop function."""
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    bbox = [50, 50, 100, 100]
    crop = extract_face(img, bbox, margin=0.1)

    assert isinstance(crop, np.ndarray)
    assert crop.shape[0] > 0 and crop.shape[1] > 0
    assert crop.shape[2] == 3


def test_validate_face_detection_helper():
    """Test validate_face_detection validation logic."""
    res_valid = FaceDetectionResult(
        face_detected=True,
        face_count=1,
        faces=[
            {
                "confidence": 0.95,
                "bbox": [10, 10, 50, 50],
                "landmarks": {
                    "right_eye": [20.0, 20.0],
                    "left_eye": [35.0, 20.0],
                    "nose_tip": [27.5, 30.0],
                    "right_mouth": [22.0, 40.0],
                    "left_mouth": [33.0, 40.0],
                },
            }
        ],
    )
    assert validate_face_detection(res_valid) is True

    res_empty = FaceDetectionResult(face_detected=False, face_count=0, faces=[])
    assert validate_face_detection(res_empty) is False


# -------------------------------------------------------------------
# REST API Endpoint Integration Tests (POST /api/scan)
# -------------------------------------------------------------------

def test_api_scan_single_face():
    """Test POST /api/scan endpoint with a valid face image."""
    single_face_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    if not os.path.exists(single_face_path):
        pytest.skip("Test image single_face.jpg not available.")

    with open(single_face_path, "rb") as f:
        response = client.post(
            "/api/scan",
            files={"file": ("single_face.jpg", f, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["face_detected"] is True
    assert data["face_count"] >= 1
    assert len(data["faces"]) >= 1
    assert "confidence" in data["faces"][0]
    assert "bbox" in data["faces"][0]
    assert "landmarks" in data["faces"][0]


def test_api_scan_no_face():
    """Test POST /api/scan endpoint with an image containing no face."""
    no_face_path = os.path.join(EXAMPLES_DIR, "no_face.jpg")
    assert os.path.exists(no_face_path)

    with open(no_face_path, "rb") as f:
        response = client.post(
            "/api/scan",
            files={"file": ("no_face.jpg", f, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["face_detected"] is False
    assert data["face_count"] == 0
    assert data["faces"] == []


def test_api_scan_invalid_file():
    """Test POST /api/scan endpoint with non-image file uploads."""
    invalid_path = os.path.join(EXAMPLES_DIR, "invalid_image.dat")
    assert os.path.exists(invalid_path)

    with open(invalid_path, "rb") as f:
        response = client.post(
            "/api/scan",
            files={"file": ("invalid_image.dat", f, "application/octet-stream")},
        )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Failed to decode" in detail or "Invalid or corrupted" in detail
