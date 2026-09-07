"""Unit & Integration Test Suite for VERIDEX Phase 6 (Independent Candidate Face Correlation).

Test Coverage Required:
1. Multiple faces in candidate image (compares Face A, Face B, Face C -> selects best face index and similarity)
2. Strong face correspondence match
3. Low similarity face match
4. No face detected in candidate image
5. Candidate image unavailable / network failure handling
6. Dual-signal evaluation (Face Cosine Similarity + pHash Image Scene Similarity)
7. Language compliance (Never says "Identity proven"; uses "Face correspondence detected")
8. REST API POST /api/verify endpoint integration
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
from app.models.candidate_schemas import CandidateVerificationResult, DiscoveredCandidate
from app.services.candidate_verification import (
    download_candidate_image,
    select_best_face,
    verify_candidate_image,
    verify_candidate_batch,
    compare_candidate_faces,
)
from app.services.face_service import detect_faces, generate_face_embedding, load_sface_recognizer
from examples.setup_test_assets import setup_test_assets, EXAMPLES_DIR

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Ensure test image assets exist prior to running verification test suite."""
    setup_test_assets()


# -------------------------------------------------------------------
# Service Unit Tests
# -------------------------------------------------------------------

def test_verify_candidate_multiple_faces():
    """Verify independent correlation on a candidate image containing multiple faces (Face A, Face B, Face C)."""
    input_path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    multi_path = os.path.join(EXAMPLES_DIR, "multi_face.jpg")
    assert os.path.exists(input_path) and os.path.exists(multi_path)

    img_in = cv2.imread(input_path)
    img_cand = cv2.imread(multi_path)

    res = verify_candidate_image(img_in, img_cand)
    assert isinstance(res, CandidateVerificationResult)
    assert res.faces_detected >= 2
    assert res.best_face_index is not None
    assert 0 <= res.best_face_index < res.faces_detected
    assert res.best_face_similarity >= 0.70
    assert res.match_status == "strong_correspondence"
    assert "Identity proven" not in res.assessment_notes


def test_verify_candidate_strong_correspondence():
    """Verify strong face correspondence for same person image."""
    path1 = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path2 = os.path.join(EXAMPLES_DIR, "same_person.jpg")

    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)

    res = verify_candidate_image(img1, img2)
    assert res.faces_detected >= 1
    assert res.best_face_similarity >= 0.70
    assert res.match_status == "strong_correspondence"
    assert res.image_similarity > 0.80
    assert "Identity proven" not in res.assessment_notes
    assert "Strong face correspondence" in res.assessment_notes or "matches" in res.assessment_notes


def test_verify_candidate_low_similarity():
    """Verify low face similarity classification for different person image."""
    path1 = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_diff = os.path.join(EXAMPLES_DIR, "different_face.jpg")

    img1 = cv2.imread(path1)
    img_diff = cv2.imread(path_diff)

    res = verify_candidate_image(img1, img_diff)
    assert res.faces_detected >= 1
    assert res.best_face_similarity < 0.3633
    assert res.match_status == "low_correspondence"
    assert "Identity proven" not in res.assessment_notes


def test_verify_candidate_no_face_detected():
    """Verify handling when candidate image contains no face."""
    path1 = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_no_face = os.path.join(EXAMPLES_DIR, "no_face.jpg")

    img1 = cv2.imread(path1)
    img_no_face = cv2.imread(path_no_face)

    res = verify_candidate_image(img1, img_no_face)
    assert res.faces_detected == 0
    assert res.best_face_index is None
    assert res.best_face_similarity == 0.0
    assert res.match_status == "no_face_detected"
    assert "No face detected" in res.assessment_notes


def test_verify_candidate_unavailable_network_failure():
    """Verify candidate_unavailable match_status when candidate URL is unreachable."""
    path1 = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    img1 = cv2.imread(path1)

    unreachable_candidate = DiscoveredCandidate(
        candidate_id="cand_unreachable_999",
        rank=1,
        title="Unreachable Web Candidate",
        source="invalid-domain-xyz987.org",
        url="https://invalid-domain-xyz987.org/non_existent.jpg",
        image_url="https://invalid-domain-xyz987.org/non_existent.jpg",
        match_type="visual",
        source_type="web",
    )

    res = verify_candidate_image(img1, unreachable_candidate)
    assert res.candidate_id == "cand_unreachable_999"
    assert res.match_status == "candidate_unavailable"
    assert res.faces_detected == 0
    assert res.error is not None
    assert "could not be downloaded" in res.error or "unavailable" in res.assessment_notes


def test_dual_signal_evaluation():
    """Verify dual signal calculation (Face Similarity + pHash Image Scene Similarity)."""
    path1 = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_comp = os.path.join(EXAMPLES_DIR, "single_face_compressed.jpg")

    img1 = cv2.imread(path1)
    img_comp = cv2.imread(path_comp)

    res = verify_candidate_image(img1, img_comp)
    assert res.best_face_similarity >= 0.70  # Face similarity high
    assert res.image_similarity >= 0.90      # pHash scene similarity high


# -------------------------------------------------------------------
# REST API Integration Tests (POST /api/verify)
# -------------------------------------------------------------------

def test_api_verify_endpoint_success():
    """Test POST /api/verify endpoint with two uploaded files."""
    path1 = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path2 = os.path.join(EXAMPLES_DIR, "same_person.jpg")

    with open(path1, "rb") as f1, open(path2, "rb") as f2:
        response = client.post(
            "/api/verify",
            files={
                "input_file": ("single_face.jpg", f1, "image/jpeg"),
                "candidate_file": ("same_person.jpg", f2, "image/jpeg"),
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["match_status"] == "strong_correspondence"
    assert data["best_face_similarity"] >= 0.70
    assert data["image_similarity"] > 0.80
    assert "Identity proven" not in data["assessment_notes"]
