"""Unit tests for Phase 8 VERIDEX Fingerprint / Evidence DNA Service."""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.models.evidence_schemas import EvidencePackage, VeridexFingerprintResult
from app.utils.canonical_json import canonicalize_json, canonical_sha256
from app.services.evidence_service import (
    create_evidence_package,
    canonicalize_evidence,
    generate_veridex_fingerprint,
    hash_face_embedding,
)

client = TestClient(app)


def test_canonicalize_json_key_sorting():
    """Verify that canonicalize_json sorts keys deterministically and strips formatting whitespace."""
    data_unordered = {
        "z_field": "last",
        "a_field": "first",
        "m_field": 12.34567,
    }
    canonical_str = canonicalize_json(data_unordered)
    assert canonical_str == '{"a_field":"first","m_field":12.3457,"z_field":"last"}'


def test_same_evidence_same_hash():
    """Verify Requirement: Same evidence package always produces the EXACT SAME evidence_hash."""
    pkg1 = create_evidence_package(
        record_id="rec_fixed_001",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding="b" * 64,
        matched_url="https://wikipedia.org/wiki/Test_Subject",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.9100,
        image_similarity=0.9400,
        overall_score=0.9100,
        timestamp="2026-09-05T18:00:00Z",
    )

    pkg2 = create_evidence_package(
        record_id="rec_fixed_001",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding="b" * 64,
        matched_url="https://wikipedia.org/wiki/Test_Subject",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.9100,
        image_similarity=0.9400,
        overall_score=0.9100,
        timestamp="2026-09-05T18:00:00Z",
    )

    fp1 = generate_veridex_fingerprint(pkg1)
    fp2 = generate_veridex_fingerprint(pkg2)

    assert fp1.evidence_hash == fp2.evidence_hash
    assert len(fp1.evidence_hash) == 64


def test_one_changed_field_completely_different_hash():
    """Verify Requirement: Changing even one single field results in a completely different hash."""
    base_params = {
        "record_id": "rec_fixed_001",
        "input_image_sha256": "a" * 64,
        "input_image_phash": "1234567890abcdef",
        "face_embedding": "b" * 64,
        "matched_url": "https://wikipedia.org/wiki/Test_Subject",
        "matched_image_sha256": "c" * 64,
        "matched_image_phash": "fedcba0987654321",
        "reverse_search_rank": 1,
        "face_similarity": 0.9100,
        "image_similarity": 0.9400,
        "overall_score": 0.9100,
        "timestamp": "2026-09-05T18:00:00Z",
    }

    base_fp = generate_veridex_fingerprint(create_evidence_package(**base_params))

    # Test altering face similarity slightly (0.9100 -> 0.9101)
    params_mod_sim = base_params.copy()
    params_mod_sim["face_similarity"] = 0.9101
    fp_mod_sim = generate_veridex_fingerprint(create_evidence_package(**params_mod_sim))
    assert fp_mod_sim.evidence_hash != base_fp.evidence_hash

    # Test altering input sha256 by 1 char
    params_mod_sha = base_params.copy()
    params_mod_sha["input_image_sha256"] = ("a" * 63) + "b"
    fp_mod_sha = generate_veridex_fingerprint(create_evidence_package(**params_mod_sha))
    assert fp_mod_sha.evidence_hash != base_fp.evidence_hash

    # Test altering rank (1 -> 2)
    params_mod_rank = base_params.copy()
    params_mod_rank["reverse_search_rank"] = 2
    fp_mod_rank = generate_veridex_fingerprint(create_evidence_package(**params_mod_rank))
    assert fp_mod_rank.evidence_hash != base_fp.evidence_hash


def test_different_candidate_different_hash():
    """Verify Requirement: Different candidate source produces a completely different hash."""
    params_cand_a = {
        "record_id": "rec_fixed_001",
        "input_image_sha256": "a" * 64,
        "input_image_phash": "1234567890abcdef",
        "face_embedding": "b" * 64,
        "matched_url": "https://wikipedia.org/wiki/Candidate_A",
        "matched_image_sha256": "c" * 64,
        "matched_image_phash": "fedcba0987654321",
        "timestamp": "2026-09-05T18:00:00Z",
    }

    params_cand_b = params_cand_a.copy()
    params_cand_b["matched_url"] = "https://instagram.com/p/Candidate_B"
    params_cand_b["matched_image_sha256"] = "d" * 64

    fp_a = generate_veridex_fingerprint(create_evidence_package(**params_cand_a))
    fp_b = generate_veridex_fingerprint(create_evidence_package(**params_cand_b))

    assert fp_a.evidence_hash != fp_b.evidence_hash


def test_privacy_preservation_no_raw_data():
    """Verify Privacy Guarantee: Raw image bytes, raw 128-D vectors, and PII are absent from package."""
    raw_128d_vector = np.random.randn(128).astype(np.float32)
    emb_hash = hash_face_embedding(raw_128d_vector)

    pkg = create_evidence_package(
        input_image_sha256="1234" * 16,
        input_image_phash="1234567890abcdef",
        face_embedding=raw_128d_vector,
        matched_url="https://example.com/asset.jpg",
        matched_image_sha256="5678" * 16,
        matched_image_phash="abcdef1234567890",
    )

    data_dict = pkg.model_dump()
    canonical_str = canonicalize_evidence(pkg)

    # 1. Verify face embedding vector is hashed to a 64-char string and raw numbers are absent
    assert pkg.face_embedding_hash == emb_hash
    assert len(pkg.face_embedding_hash) == 64
    assert not any(isinstance(val, (np.ndarray, list)) for val in data_dict.values())

    # 2. Verify no raw bytes or binary payloads
    assert "image_bytes" not in data_dict
    assert "raw_image" not in data_dict
    assert "phone" not in canonical_str
    assert "email" not in canonical_str


def test_api_fingerprint_endpoint():
    """Test POST /api/fingerprint API endpoint."""
    package_payload = {
        "record_id": "rec_api_test_01",
        "input_image_sha256": "1111" * 16,
        "input_image_phash": "1234567890abcdef",
        "face_embedding_hash": "2222" * 16,
        "matched_url": "https://bbc.com/news/123",
        "matched_image_sha256": "3333" * 16,
        "matched_image_phash": "fedcba0987654321",
        "reverse_search_rank": 1,
        "face_similarity": 0.95,
        "image_similarity": 0.92,
        "overall_score": 0.94,
        "search_provider": "Google Lens via SerpApi",
        "timestamp": "2026-09-05T18:00:00Z",
    }

    response = client.post("/api/fingerprint", json=package_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["record_id"] == "rec_api_test_01"
    assert "evidence_hash" in data
    assert len(data["evidence_hash"]) == 64
