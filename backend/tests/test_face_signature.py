"""Unit & Integration Test Suite for VERIDEX Phase 2 (Face Signature Generation & Similarity).

Tests all Phase 2 requirements:
1. Same image vs itself (Cosine Similarity = ~1.0)
2. Same person's two images (High matching score > threshold)
3. Different person's images (Low matching score < threshold)
4. Missing face handling in comparison
5. Multiple faces signature generation
6. Face alignment and 128-D embedding extraction
7. SHA-256 fingerprint hash generation
8. REST API POST /api/scan with signature metadata
9. REST API POST /api/compare with two-image multipart upload
"""

import os
import sys
import pytest
import cv2
import numpy as np
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.services.face_service import (
    detect_faces,
    align_face,
    generate_face_embedding,
    calculate_face_similarity,
    normalize_embedding,
    load_sface_recognizer,
)
from app.models.face_schemas import FaceSimilarityResult, FaceSignature
from examples.setup_test_assets import setup_test_assets, EXAMPLES_DIR

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Ensure all test image assets are generated/downloaded prior to test execution."""
    setup_test_assets()


# -------------------------------------------------------------------
# Service Unit Tests
# -------------------------------------------------------------------

def test_same_image_vs_itself():
    """Test 1: Cosine similarity of the same face image against itself (Expect score ~1.0)."""
    single_face_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    assert os.path.exists(single_face_path)

    img = cv2.imread(single_face_path)
    res = detect_faces(img, generate_signatures=True)
    assert res.face_detected is True
    assert len(res.faces) >= 1

    face = res.faces[0]
    assert face.signature is not None
    assert face.signature.embedding_generated is True
    assert face.signature.embedding_dimension == 128
    assert len(face.signature.embedding_hash) == 64  # SHA-256 hex length

    # Extract raw embedding
    sface = load_sface_recognizer()
    emb1, hash1, _ = generate_face_embedding(img, face, sface_recognizer=sface)

    # Compare embedding against itself
    sim_result = calculate_face_similarity(emb1, emb1)
    assert isinstance(sim_result, FaceSimilarityResult)
    assert sim_result.matching_score >= 0.99
    assert sim_result.correspondence_match is True
    assert "High Face Correspondence" in sim_result.quality_assessment


def test_same_person_two_images():
    """Test 2: Cosine similarity of two images of the same person under different conditions (Expect score > threshold)."""
    img1_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    img2_path = os.path.join(EXAMPLES_DIR, "same_person.jpg")
    assert os.path.exists(img1_path) and os.path.exists(img2_path)

    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    res1 = detect_faces(img1)
    res2 = detect_faces(img2)
    assert res1.face_detected and res2.face_detected

    sface = load_sface_recognizer()
    emb1, hash1, _ = generate_face_embedding(img1, res1.faces[0], sface_recognizer=sface)
    emb2, hash2, _ = generate_face_embedding(img2, res2.faces[0], sface_recognizer=sface)

    sim_result = calculate_face_similarity(emb1, emb2)
    assert isinstance(sim_result, FaceSimilarityResult)
    assert sim_result.matching_score >= 0.3633
    assert sim_result.correspondence_match is True


def test_different_person_images():
    """Test 3: Cosine similarity of images of different individuals (Expect score < threshold)."""
    img1_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    img2_path = os.path.join(EXAMPLES_DIR, "different_face.jpg")
    assert os.path.exists(img1_path) and os.path.exists(img2_path)

    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    res1 = detect_faces(img1)
    res2 = detect_faces(img2)
    assert res1.face_detected and res2.face_detected

    sface = load_sface_recognizer()
    emb1, hash1, _ = generate_face_embedding(img1, res1.faces[0], sface_recognizer=sface)
    emb2, hash2, _ = generate_face_embedding(img2, res2.faces[0], sface_recognizer=sface)

    sim_result = calculate_face_similarity(emb1, emb2)
    assert isinstance(sim_result, FaceSimilarityResult)
    # Different individuals should yield low matching scores below decision threshold
    assert sim_result.matching_score < 0.3633
    assert sim_result.correspondence_match is False


def test_missing_face_comparison():
    """Test 4: Comparison handling when one image contains no face."""
    img1_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    no_face_path = os.path.join(EXAMPLES_DIR, "no_face.jpg")

    with open(img1_path, "rb") as f1, open(no_face_path, "rb") as f2:
        response = client.post(
            "/api/compare",
            files={
                "file1": ("single_face.jpg", f1, "image/jpeg"),
                "file2": ("no_face.jpg", f2, "image/jpeg"),
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["correspondence_match"] is False
    assert data["matching_score"] == 0.0
    assert "No face detected" in data["quality_assessment"]


def test_multiple_faces_signature_generation():
    """Test 5: Signature generation on an image containing multiple faces."""
    multi_path = os.path.join(EXAMPLES_DIR, "multi_face.jpg")
    assert os.path.exists(multi_path)

    img = cv2.imread(multi_path)
    res = detect_faces(img, generate_signatures=True)

    assert res.face_detected is True
    assert res.face_count >= 2
    assert len(res.faces) >= 2

    for face in res.faces:
        assert face.signature is not None
        assert face.signature.embedding_generated is True
        assert face.signature.embedding_dimension == 128
        assert len(face.signature.embedding_hash) == 64


def test_facial_alignment_crop():
    """Test align_face output dimensions (Expect 112x112 pixel crop)."""
    single_face_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    img = cv2.imread(single_face_path)
    res = detect_faces(img, generate_signatures=False)

    aligned = align_face(img, res.faces[0])
    assert isinstance(aligned, np.ndarray)
    assert aligned.shape == (112, 112, 3)


def test_normalize_embedding_unit_length():
    """Test normalize_embedding produces L2 unit norm."""
    vec = np.array([3.0, 4.0], dtype=np.float32)
    norm_vec = normalize_embedding(vec)
    assert pytest.approx(np.linalg.norm(norm_vec), 1e-5) == 1.0


# -------------------------------------------------------------------
# REST API Endpoint Integration Tests
# -------------------------------------------------------------------

def test_api_scan_with_signature():
    """Test POST /api/scan returns face signature metadata."""
    single_face_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    with open(single_face_path, "rb") as f:
        response = client.post(
            "/api/scan",
            files={"file": ("single_face.jpg", f, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["face_detected"] is True
    assert len(data["faces"]) >= 1

    signature = data["faces"][0]["signature"]
    assert signature["embedding_generated"] is True
    assert signature["embedding_dimension"] == 128
    assert len(signature["embedding_hash"]) == 64
    # Verify raw vector floats are NOT exposed in public API payload
    assert "embedding" not in signature
    assert "vector" not in signature


def test_api_compare_same_person():
    """Test POST /api/compare endpoint with two images of same person."""
    img1_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    img2_path = os.path.join(EXAMPLES_DIR, "same_person.jpg")

    with open(img1_path, "rb") as f1, open(img2_path, "rb") as f2:
        response = client.post(
            "/api/compare",
            files={
                "file1": ("single_face.jpg", f1, "image/jpeg"),
                "file2": ("same_person.jpg", f2, "image/jpeg"),
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["correspondence_match"] is True
    assert data["matching_score"] >= 0.3633
    assert data["face1_hash"] is not None
    assert data["face2_hash"] is not None
    assert "Correspondence" in data["quality_assessment"]


def test_api_compare_different_persons():
    """Test POST /api/compare endpoint with images of different individuals."""
    img1_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    img2_path = os.path.join(EXAMPLES_DIR, "different_face.jpg")

    with open(img1_path, "rb") as f1, open(img2_path, "rb") as f2:
        response = client.post(
            "/api/compare",
            files={
                "file1": ("single_face.jpg", f1, "image/jpeg"),
                "file2": ("different_face.jpg", f2, "image/jpeg"),
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["correspondence_match"] is False
    assert data["matching_score"] < 0.3633
    assert "Disparate" in data["quality_assessment"] or "Low" in data["quality_assessment"]
