"""Unit tests for Phase 7 Evidence Scoring & Transparent Explainability Service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import (
    WEIGHT_REVERSE_SEARCH,
    WEIGHT_FACE_SIMILARITY,
    WEIGHT_IMAGE_SIMILARITY,
    WEIGHT_SOURCE_RELEVANCE,
    WEIGHT_METADATA_CONSISTENCY,
)
from app.models.candidate_schemas import DiscoveredCandidate
from app.models.evidence_schemas import EvidenceScoreResult, SignalExplainability
from app.services.evidence_scoring import (
    calculate_reverse_search_score,
    calculate_source_score,
    calculate_metadata_score,
    calculate_overall_score,
)

client = TestClient(app)


def test_default_weights_sum_to_one():
    """Verify that default signal weights in config sum to 1.0."""
    total_weight = (
        WEIGHT_REVERSE_SEARCH +
        WEIGHT_FACE_SIMILARITY +
        WEIGHT_IMAGE_SIMILARITY +
        WEIGHT_SOURCE_RELEVANCE +
        WEIGHT_METADATA_CONSISTENCY
    )
    assert pytest.approx(total_weight, abs=1e-4) == 1.00


def test_calculate_reverse_search_score():
    """Test reverse search relevance scoring across primitives and candidate objects."""
    # Direct numeric input
    assert calculate_reverse_search_score(0.96) == 0.96
    assert calculate_reverse_search_score(1.5) == 1.0
    assert calculate_reverse_search_score(-0.2) == 0.0

    # None fallback
    assert calculate_reverse_search_score(None) == 0.50

    # DiscoveredCandidate object evaluation
    cand_exact = DiscoveredCandidate(
        candidate_id="cand_01",
        rank=1,
        title="Exact Match Candidate",
        source="wikipedia.org",
        url="https://en.wikipedia.org/wiki/Test",
        match_type="exact",
    )
    score_exact = calculate_reverse_search_score(cand_exact)
    assert score_exact >= 0.90

    cand_visual_rank10 = DiscoveredCandidate(
        candidate_id="cand_02",
        rank=10,
        title="Visual Match Candidate",
        source="example.com",
        url="https://example.com/page",
        match_type="visual",
    )
    score_visual = calculate_reverse_search_score(cand_visual_rank10)
    assert score_visual < score_exact


def test_calculate_source_score():
    """Test source platform & publisher domain relevance scoring."""
    # High-reputation domains
    assert calculate_source_score("https://en.wikipedia.org/wiki/Article") == 0.80
    assert calculate_source_score("https://www.bbc.com/news/12345") == 0.80
    assert calculate_source_score("https://instagram.com/p/123") == 0.80

    # General web domain
    assert calculate_source_score("https://someblogsite.org/post") == 0.70

    # Direct float input
    assert calculate_source_score(0.80) == 0.80

    # None/Empty domain fallback
    assert calculate_source_score(None) == 0.50
    assert calculate_source_score("") == 0.50


def test_calculate_metadata_score():
    """Test EXIF and context metadata consistency scoring."""
    # Direct numeric input
    assert calculate_metadata_score(0.90) == 0.90
    assert calculate_metadata_score(None) == 0.90

    # Dictionary checks
    matching_metadata = {
        "timestamp_match": True,
        "location_match": True,
        "resolution_aspect_match": True,
    }
    assert calculate_metadata_score(matching_metadata) == 1.0

    conflicting_metadata = {
        "conflict_detected": True,
    }
    assert calculate_metadata_score(conflicting_metadata) == 0.20


def test_calculate_overall_score_sample_values():
    """Test calculate_overall_score using the exact values from Phase 7 prompt requirements."""
    res = calculate_overall_score(
        reverse_search=0.96,
        face_similarity=0.91,
        image_similarity=0.94,
        source=0.80,
        metadata=0.90,
        candidate_id="cand_test_sample",
    )

    assert isinstance(res, EvidenceScoreResult)
    assert res.candidate_id == "cand_test_sample"
    assert res.reverse_search_score == 0.96
    assert res.face_similarity == 0.91
    assert res.image_similarity == 0.94
    assert res.source_score == 0.80
    assert res.metadata_score == 0.90
    assert res.overall_score in (0.91, 0.92)
    assert res.status == "HIGH_CORRESPONDENCE"


    # Verify explainability signals
    assert len(res.explainability) == 5
    signal_labels = [item.label for item in res.explainability]
    assert "✓ Reverse image evidence" in signal_labels
    assert "✓ Face correspondence" in signal_labels
    assert "✓ Perceptual similarity" in signal_labels
    assert "✓ Source relevance" in signal_labels
    assert "✓ Metadata consistency" in signal_labels

    # Verify terminology and disclaimer
    assert "probability of legal identity" in res.disclaimer
    assert "Identity proven" not in res.assessment_summary


def test_calculate_overall_score_status_classifications():
    """Test status classification boundaries (HIGH, MODERATE, LOW, INSUFFICIENT)."""
    # High correspondence
    res_high = calculate_overall_score(
        reverse_search=0.9, face_similarity=0.9, image_similarity=0.9, source=0.9, metadata=0.9
    )
    assert res_high.status == "HIGH_CORRESPONDENCE"

    # Moderate correspondence
    res_mod = calculate_overall_score(
        reverse_search=0.7, face_similarity=0.7, image_similarity=0.7, source=0.7, metadata=0.7
    )
    assert res_mod.status == "MODERATE_CORRESPONDENCE"

    # Low correspondence
    res_low = calculate_overall_score(
        reverse_search=0.5, face_similarity=0.5, image_similarity=0.5, source=0.5, metadata=0.5
    )
    assert res_low.status == "LOW_CORRESPONDENCE"

    # Insufficient correspondence
    res_insuff = calculate_overall_score(
        reverse_search=0.2, face_similarity=0.1, image_similarity=0.2, source=0.3, metadata=0.2
    )
    assert res_insuff.status == "INSUFFICIENT_CORRESPONDENCE"


def test_calculate_overall_score_custom_weights():
    """Test calculate_overall_score with custom signal weight overrides."""
    custom_weights = {
        "reverse_search": 0.20,
        "face_similarity": 0.50,
        "image_similarity": 0.10,
        "source_relevance": 0.10,
        "metadata_consistency": 0.10,
    }
    res = calculate_overall_score(
        reverse_search=0.50,
        face_similarity=1.00,
        image_similarity=0.50,
        source=0.50,
        metadata=0.50,
        weights=custom_weights,
    )
    # Weighted calculation: 0.50*0.20 + 1.00*0.50 + 0.50*0.10 + 0.50*0.10 + 0.50*0.10 = 0.10 + 0.50 + 0.05 + 0.05 + 0.05 = 0.75
    assert pytest.approx(res.overall_score, abs=0.02) == 0.75
    assert res.weights_used["face_similarity"] == 0.50


def test_api_score_evidence_endpoint():
    """Test the POST /api/score-evidence FastAPI route."""
    response = client.post(
        "/api/score-evidence",
        params={
            "reverse_search_score": 0.96,
            "face_similarity": 0.91,
            "image_similarity": 0.94,
            "source_score": 0.80,
            "metadata_score": 0.90,
            "candidate_id": "cand_endpoint_test",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["candidate_id"] == "cand_endpoint_test"
    assert data["reverse_search_score"] == 0.96
    assert data["face_similarity"] == 0.91
    assert data["image_similarity"] == 0.94
    assert data["source_score"] == 0.80
    assert data["metadata_score"] == 0.90
    assert data["overall_score"] in (0.91, 0.92)
    assert data["status"] == "HIGH_CORRESPONDENCE"

    assert len(data["explainability"]) == 5
