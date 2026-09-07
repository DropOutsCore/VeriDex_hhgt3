"""Phase 13 Integration Tests for Full Backend Pipeline & API Endpoints."""

import os
import sys
import io
import cv2
import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.models.pipeline_schemas import PipelineStatus, FullPipelineResult
from app.models.evidence_schemas import (
    EvidencePackage,
    VeridexFingerprintResult,
    BlockchainAnchoringResult,
    IntegrityVerificationResult,
)
from app.services.pipeline_service import execute_full_pipeline
from app.services.evidence_service import generate_veridex_fingerprint
from examples.setup_test_assets import setup_test_assets, EXAMPLES_DIR

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Ensure test image assets exist prior to running test suite."""
    setup_test_assets()


def _get_single_face_bytes() -> bytes:
    """Read binary bytes of test image containing a real human face."""
    path = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    assert os.path.exists(path), f"Test asset missing: {path}"
    with open(path, "rb") as f:
        return f.read()


# ==================================================
# 1. END-TO-END PIPELINE INTEGRATION TEST
# ==================================================

def test_full_pipeline_execution():
    """Verify Phase 13 Requirement: End-to-end pipeline execution from image -> face -> search -> candidate -> verification -> fingerprint."""
    image_bytes = _get_single_face_bytes()

    # Mock reverse search so test does not rely on external API network calls
    mock_lens_response = MagicMock()
    mock_lens_response.search_executed = True
    mock_lens_response.total_results_found = 2
    mock_lens_response.exact_matches = []
    mock_lens_response.visual_matches = [
        {
            "position": 1,
            "title": "Sample Verified Source Profile",
            "link": "https://example.com/profile/123",
            "source": "example.com",
            "thumbnail": "https://example.com/thumb.jpg",
            "image_url": "https://example.com/full.jpg",
            "domain": "example.com",
            "is_social_source": False,
        }
    ]

    with patch("app.services.pipeline_service.execute_lens_search_pipeline") as mock_lens_search, \
         patch("app.services.pipeline_service.verify_candidate_image") as mock_verify_cand:

        mock_lens_search.return_value = mock_lens_response

        # Mock candidate verification response
        mock_cand_ver = MagicMock()
        mock_cand_ver.faces_detected = 1
        mock_cand_ver.best_face_similarity = 0.9450
        mock_cand_ver.image_similarity = 0.9200
        mock_cand_ver.candidate_image_url = "https://example.com/full.jpg"
        mock_verify_cand.return_value = mock_cand_ver

        result = execute_full_pipeline(image_bytes, auto_anchor=False)

        assert isinstance(result, FullPipelineResult)
        assert result.input_face_detected is True
        assert result.face_detection is not None
        assert result.face_detection.face_detected is True
        assert len(result.face_detection.faces) > 0

        # Check search response
        assert result.search_response is not None
        assert result.search_response.search_executed is True

        # Check candidate verification & evidence score
        assert result.verified_candidate is not None
        assert result.evidence_score is not None
        assert result.evidence_score.overall_score > 0.0

        # Check evidence package and fingerprint (EVIDENCE DNA)
        assert result.evidence_package is not None
        assert len(result.evidence_package.input_image_sha256) == 64
        assert result.fingerprint is not None
        assert len(result.fingerprint.evidence_hash) == 64

        # Check pipeline steps transition progression
        step_names = [s.step.value for s in result.steps]
        assert "IDLE" in step_names
        assert "SCANNING" in step_names
        assert "ENCODING" in step_names
        assert "SEARCHING" in step_names
        assert "DISCOVERING" in step_names
        assert "VERIFYING" in step_names
        assert "FINGERPRINTING" in step_names
        assert result.status == PipelineStatus.FINGERPRINTING


def test_full_pipeline_with_mocked_blockchain():
    """Verify End-to-End Pipeline including Phase 11 Anchoring & Phase 12 On-Chain Verification."""
    image_bytes = _get_single_face_bytes()

    mock_lens_response = MagicMock()
    mock_lens_response.search_executed = True
    mock_lens_response.total_results_found = 1
    mock_lens_response.exact_matches = []
    mock_lens_response.visual_matches = [
        {
            "position": 1,
            "title": "OnChain Verified Match",
            "link": "https://wikipedia.org/wiki/Test",
            "source": "wikipedia.org",
            "thumbnail": "https://wikipedia.org/thumb.jpg",
            "image_url": "https://wikipedia.org/full.jpg",
            "domain": "wikipedia.org",
            "is_social_source": False,
        }
    ]

    with patch("app.services.pipeline_service.execute_lens_search_pipeline") as mock_lens_search, \
         patch("app.services.pipeline_service.verify_candidate_image") as mock_verify_cand, \
         patch("app.services.pipeline_service.anchor_evidence") as mock_anchor, \
         patch("app.services.pipeline_service.verify_evidence_integrity") as mock_integrity:

        mock_lens_search.return_value = mock_lens_response

        mock_cand_ver = MagicMock()
        mock_cand_ver.faces_detected = 1
        mock_cand_ver.best_face_similarity = 0.95
        mock_cand_ver.image_similarity = 0.90
        mock_cand_ver.candidate_image_url = "https://wikipedia.org/full.jpg"
        mock_verify_cand.return_value = mock_cand_ver

        mock_anchor.return_value = BlockchainAnchoringResult(
            proof_id="rec_pip_test_001",
            evidence_hash="a" * 64,
            transaction_hash="0x" + "f" * 64,
            block_number="46814950",
            network="Polygon Amoy",
        )

        mock_integrity.return_value = IntegrityVerificationResult(
            local_hash="a" * 64,
            on_chain_hash="a" * 64,
            verified=True,
            status="VERIFIED",
            proof_id="rec_pip_test_001",
            details="Verified on-chain",
        )

        result = execute_full_pipeline(image_bytes, auto_anchor=True)

        assert result.status == PipelineStatus.VERIFIED
        assert result.blockchain_anchoring is not None
        assert result.blockchain_anchoring.network == "Polygon Amoy"
        assert result.on_chain_verification is not None
        assert result.on_chain_verification.verified is True
        assert result.on_chain_verification.status == "VERIFIED"


# ==================================================
# 2. REQUIRED ENDPOINT API ROUTE TESTS
# ==================================================

def test_api_health_endpoint():
    """Verify GET /api/health endpoint."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "pipeline_status" in data
    assert data["pipeline_status"] == "IDLE"


def test_api_scan_endpoint():
    """Verify POST /api/scan endpoint."""
    image_bytes = _get_single_face_bytes()
    resp = client.post("/api/scan", files={"file": ("test.png", image_bytes, "image/png")})
    assert resp.status_code == 200
    data = resp.json()
    assert "face_detected" in data
    assert data["face_detected"] is True
    assert len(data["faces"]) > 0


def test_api_search_endpoint():
    """Verify POST /api/search endpoint."""
    resp = client.post("/api/search", params={"image_url": "https://httpbin.org/image/jpeg"})
    assert resp.status_code == 200
    data = resp.json()
    assert "search_executed" in data


def test_api_verify_endpoint():
    """Verify POST /api/verify endpoint."""
    image_bytes = _get_single_face_bytes()
    cand_bytes = _get_single_face_bytes()
    resp = client.post(
        "/api/verify",
        files={
            "input_file": ("input.png", image_bytes, "image/png"),
            "candidate_file": ("candidate.png", cand_bytes, "image/png"),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "candidate_id" in data
    assert "match_status" in data


def test_api_anchor_endpoint_validation():
    """Verify POST /api/anchor endpoint handling."""
    dummy_pkg = {
        "record_id": "rec_anchor_test_001",
        "input_image_sha256": "1" * 64,
        "input_image_phash": "1234567890abcdef",
        "face_embedding_hash": "2" * 64,
        "matched_url": "https://example.com/item",
        "matched_image_sha256": "3" * 64,
        "matched_image_phash": "fedcba0987654321",
        "reverse_search_rank": 1,
        "face_similarity": 0.9,
        "image_similarity": 0.9,
        "overall_score": 0.9,
        "timestamp": "2026-09-06T00:00:00Z",
    }
    with patch("app.api.scan.anchor_evidence") as mock_anchor_fn:
        mock_anchor_fn.return_value = BlockchainAnchoringResult(
            proof_id="rec_anchor_test_001",
            evidence_hash="a" * 64,
            transaction_hash="0x" + "e" * 64,
            block_number="12345",
            network="Polygon Amoy",
        )
        resp = client.post("/api/anchor", json=dummy_pkg)
        assert resp.status_code == 200
        assert resp.json()["proof_id"] == "rec_anchor_test_001"


def test_api_verify_chain_endpoint():
    """Verify POST /api/verify-chain endpoint (alias for verify-integrity)."""
    dummy_pkg = {
        "record_id": "rec_chain_test_001",
        "input_image_sha256": "1" * 64,
        "input_image_phash": "1234567890abcdef",
        "face_embedding_hash": "2" * 64,
        "matched_url": "https://example.com/item",
        "matched_image_sha256": "3" * 64,
        "matched_image_phash": "fedcba0987654321",
        "reverse_search_rank": 1,
        "face_similarity": 0.9,
        "image_similarity": 0.9,
        "overall_score": 0.9,
        "timestamp": "2026-09-06T00:00:00Z",
    }
    with patch("app.api.scan.verify_evidence_integrity") as mock_integrity_fn:
        mock_integrity_fn.return_value = IntegrityVerificationResult(
            local_hash="a" * 64,
            on_chain_hash="a" * 64,
            verified=True,
            status="VERIFIED",
            proof_id="rec_chain_test_001",
        )
        resp = client.post("/api/verify-chain", json=dummy_pkg)
        assert resp.status_code == 200
        assert resp.json()["verified"] is True
        assert resp.json()["status"] == "VERIFIED"


def test_api_tamper_test_endpoint():
    """Verify POST /api/tamper-test endpoint (alias for simulate-tampering)."""
    dummy_pkg = {
        "record_id": "rec_tamper_test_001",
        "input_image_sha256": "1" * 64,
        "input_image_phash": "1234567890abcdef",
        "face_embedding_hash": "2" * 64,
        "matched_url": "https://example.com/original.jpg",
        "matched_image_sha256": "3" * 64,
        "matched_image_phash": "fedcba0987654321",
        "reverse_search_rank": 1,
        "face_similarity": 0.9,
        "image_similarity": 0.9,
        "overall_score": 0.9,
        "timestamp": "2026-09-06T00:00:00Z",
    }
    resp = client.post(
        "/api/tamper-test",
        json=dummy_pkg,
        params={"field_to_modify": "matched_url", "new_value": "https://tampered-fake-site.com/fake.jpg"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["matched_url"] == "https://tampered-fake-site.com/fake.jpg"


def test_api_pipeline_endpoint():
    """Verify POST /api/pipeline endpoint."""
    image_bytes = _get_single_face_bytes()
    resp = client.post(
        "/api/pipeline",
        files={"file": ("test.png", image_bytes, "image/png")},
        params={"auto_anchor": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "pipeline_id" in data
    assert "status" in data
    assert "steps" in data
