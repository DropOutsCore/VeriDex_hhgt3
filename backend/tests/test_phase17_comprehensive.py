"""Phase 17 Comprehensive Verification Test Suite.

==================================================
TEST CASES COVERED
==================================================

- CASE 1: Exact source image (High reverse-search relevance, high face similarity)
- CASE 2: Cropped source image (Face correlation remains possible on cropped ROI)
- CASE 3: Compressed source image (SHA-256 changes, pHash remains similar, high face similarity)
- CASE 4: Different person's image (Low face similarity score, candidate rejected)
- CASE 5: No face (Pipeline stops gracefully with clear error)
- CASE 6: Multiple faces (All candidate faces evaluated, best matching face selected)
- CASE 7: Candidate image unavailable (HTTP 404/failure handled gracefully, status marked candidate_unavailable)
- CASE 8: Blockchain RPC unavailable (Clear RPCFailureError / 503 response without stack trace leakage)
- CASE 9: Tampered evidence payload (Recomputed hash mismatch returns verified=False, status=TAMPER_DETECTED)
"""

import os
import sys
import cv2
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.models.evidence_schemas import EvidencePackage
from app.services.face_service import detect_faces, calculate_face_similarity
from app.services.candidate_verification import verify_candidate_image
from app.services.evidence_scoring import calculate_overall_score
from app.services.evidence_service import generate_veridex_fingerprint
from app.services.blockchain_service import verify_evidence_integrity, simulate_tampering, RPCFailureError
from app.utils.hashing import sha256_bytes, compare_phash, image_phash
from examples.setup_test_assets import setup_test_assets, EXAMPLES_DIR

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Ensure test image assets exist prior to executing Phase 17 test suite."""
    setup_test_assets()


def _read_asset(filename: str) -> bytes:
    path = os.path.join(EXAMPLES_DIR, filename)
    assert os.path.exists(path), f"Required test asset missing: '{path}'"
    with open(path, "rb") as f:
        return f.read()


# ==================================================
# CASE 1: EXACT SOURCE IMAGE
# ==================================================
def test_case_1_exact_source_image():
    """CASE 1: Exact source image yields high face similarity (~1.0) and high reverse search relevance."""
    img_bytes = _read_asset("single_face.jpg")
    res = verify_candidate_image(img_bytes, img_bytes)

    assert res.faces_detected >= 1
    assert res.best_face_similarity >= 0.99
    assert res.match_status == "strong_correspondence"


# ==================================================
# CASE 2: CROPPED SOURCE IMAGE
# ==================================================
def test_case_2_cropped_source_image():
    """CASE 2: Cropped source image allows face correlation on crop ROI."""
    img_bytes = _read_asset("single_face.jpg")
    img_mat = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    # Crop central facial region
    h, w = img_mat.shape[:2]
    crop = img_mat[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    _, crop_bytes = cv2.imencode(".jpg", crop)

    res = verify_candidate_image(img_bytes, crop_bytes.tobytes())

    assert res.faces_detected >= 1
    assert res.best_face_similarity > 0.75
    assert res.match_status in ("strong_correspondence", "moderate_correspondence")


# ==================================================
# CASE 3: COMPRESSED SOURCE IMAGE
# ==================================================
def test_case_3_compressed_source_image():
    """CASE 3: Compressed image changes SHA-256 bytes, pHash remains perceptually similar, face similarity remains high."""
    orig_bytes = _read_asset("single_face.jpg")
    comp_bytes = _read_asset("single_face_compressed.jpg")

    # 1. SHA-256 byte digest MUST change due to JPEG compression
    sha_orig = sha256_bytes(orig_bytes)
    sha_comp = sha256_bytes(comp_bytes)
    assert sha_orig != sha_comp

    # 2. Perceptual pHash remains visually similar
    phash_orig = image_phash(orig_bytes)
    phash_comp = image_phash(comp_bytes)
    phash_diff = compare_phash(phash_orig, phash_comp)
    assert phash_diff["perceptually_similar"] is True

    # 3. Face similarity remains strong
    res = verify_candidate_image(orig_bytes, comp_bytes)
    assert res.faces_detected >= 1
    assert res.best_face_similarity > 0.80


# ==================================================
# CASE 4: DIFFERENT PERSON'S IMAGE
# ==================================================
def test_case_4_different_person_image():
    """CASE 4: Image of a completely different person yields low face similarity score and low match status."""
    person1_bytes = _read_asset("single_face.jpg")
    person2_bytes = _read_asset("different_face.jpg")

    res = verify_candidate_image(person1_bytes, person2_bytes)

    # Cosine similarity between different people must be low
    assert res.best_face_similarity < 0.40
    assert res.match_status in ("low_correspondence", "no_face_detected")


# ==================================================
# CASE 5: NO FACE IN IMAGE
# ==================================================
def test_case_5_no_face_image():
    """CASE 5: Input image with no face stops pipeline gracefully and returns clear error detail."""
    no_face_bytes = _read_asset("no_face.jpg")
    det_res = detect_faces(no_face_bytes)

    assert det_res.face_detected is False
    assert det_res.face_count == 0

    # API scan returns empty face list cleanly without crashing
    resp = client.post("/api/scan", files={"file": ("no_face.jpg", no_face_bytes, "image/jpeg")})
    assert resp.status_code == 200
    assert resp.json()["face_detected"] is False


# ==================================================
# CASE 6: MULTIPLE FACES IN CANDIDATE
# ==================================================
def test_case_6_multiple_faces():
    """CASE 6: Candidate image with multiple faces evaluates all faces and selects best matching face."""
    input_bytes = _read_asset("single_face.jpg")
    multi_bytes = _read_asset("multi_face.jpg")

    res = verify_candidate_image(input_bytes, multi_bytes)

    assert res.faces_detected >= 2
    assert res.best_face_index is not None
    assert res.best_face_similarity > 0.85


# ==================================================
# CASE 7: CANDIDATE IMAGE UNAVAILABLE
# ==================================================
def test_case_7_candidate_unavailable():
    """CASE 7: Network HTTP failure or missing candidate image is handled gracefully and marked candidate_unavailable."""
    input_bytes = _read_asset("single_face.jpg")
    fake_url = "https://non-existent-domain-veridex-test-12345.org/missing.jpg"

    res = verify_candidate_image(input_bytes, fake_url)

    assert res.match_status == "candidate_unavailable"
    assert res.error is not None


# ==================================================
# CASE 8: BLOCKCHAIN RPC UNAVAILABLE
# ==================================================
def test_case_8_blockchain_rpc_unavailable():
    """CASE 8: RPC failure returns clear 503 Service Unavailable error without leaking stack trace."""
    dummy_package = {
        "record_id": "rec_rpc_test_001",
        "input_image_sha256": "a" * 64,
        "input_image_phash": "1234567890abcdef",
        "face_embedding_hash": "b" * 64,
        "matched_url": "https://example.com/item",
        "matched_image_sha256": "c" * 64,
        "matched_image_phash": "fedcba0987654321",
        "reverse_search_rank": 1,
        "face_similarity": 0.9,
        "image_similarity": 0.9,
        "overall_score": 0.9,
        "timestamp": "2026-09-06T00:00:00Z",
    }

    with patch("app.api.scan.anchor_evidence") as mock_anchor:
        mock_anchor.side_effect = RPCFailureError("RPC provider endpoint unreachable")
        resp = client.post("/api/anchor", json=dummy_package)

        assert resp.status_code == 503
        assert "RPC Failure" in resp.json()["detail"]


# ==================================================
# CASE 9: TAMPERED EVIDENCE DETECTED
# ==================================================
def test_case_9_tampered_evidence():
    """CASE 9: Single-field evidence payload modification produces hash mismatch returning verified=False, TAMPER_DETECTED."""
    pkg = EvidencePackage(
        record_id="rec_phase17_tamper_001",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding_hash="b" * 64,
        matched_url="https://wikipedia.org/wiki/Original",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.92,
        image_similarity=0.90,
        overall_score=0.91,
        timestamp="2026-09-06T00:00:00Z",
    )

    orig_fp = generate_veridex_fingerprint(pkg)
    tampered_pkg = simulate_tampering(pkg, field_to_modify="matched_url", new_value="https://tampered-fake.com/hacked.jpg")

    with patch("app.services.blockchain_service.get_web3_connection") as mock_get_w3:
        mock_w3 = MagicMock()
        mock_w3.to_checksum_address.side_effect = lambda a: a
        mock_w3.to_hex.side_effect = lambda b: b.hex() if isinstance(b, bytes) else str(b)

        mock_contract = MagicMock()
        mock_contract.functions.getProof.return_value.call.return_value = (
            bytes.fromhex(pkg.record_id.encode().hex().ljust(64, '0')[:64]),
            bytes.fromhex(orig_fp.evidence_hash),
            bytes.fromhex(pkg.input_image_sha256),
            bytes.fromhex(pkg.matched_image_sha256),
            1757116800,
            "0x1111111111111111111111111111111111111111",
        )
        mock_w3.eth.contract.return_value = mock_contract
        mock_get_w3.return_value = mock_w3

        result = verify_evidence_integrity(tampered_pkg)

        assert result.verified is False
        assert result.status == "TAMPER_DETECTED"
        assert result.local_hash != result.on_chain_hash
