"""Phase 7 Transparent Evidence Scoring & Multi-Signal Explainability Service.

==================================================
CONCEPTUAL DISTINCTION & ARCHITECTURAL DESIGN
==================================================

1. EVIDENCE CORRESPONDENCE SCORE vs. PROBABILITY OF IDENTITY:
   - VERIDEX does NOT make legal identity claims or compute a "probability of legal identity".
   - The output `overall_score` is a transparent, weighted EVIDENCE CORRESPONDENCE SCORE.
   - It quantifies the degree of multi-signal alignment across independent channels:
     * Reverse Search Engine Relevance (Default Weight: 0.40)
     * Independent SFace Face Correlation (Default Weight: 0.35)
     * Global Scene pHash Image Similarity (Default Weight: 0.10)
     * Domain & Source Relevance (Default Weight: 0.10)
     * Metadata & Contextual Consistency (Default Weight: 0.05)

2. EXPLAINABILITY & TRANSPARENCY:
   - The engine returns explicit individual component scores and explainability signals so downstream users
     and frontend interfaces can inspect WHY the system reached a given evidence correspondence conclusion.

3. TERMINOLOGY & LANGUAGE CONSTRAINTS:
   - NEVER SAY: "Identity proven", "Absolute identity confirmed", or "Legal proof of identity".
   - PERMISSIBLE TERMINOLOGY:
     * "Face correspondence detected."
     * "High face similarity."
     * "Candidate matches the input face."
"""

import logging
from typing import Dict, Any, Union, Optional, List
from urllib.parse import urlparse

from app.config import (
    WEIGHT_REVERSE_SEARCH,
    WEIGHT_FACE_SIMILARITY,
    WEIGHT_IMAGE_SIMILARITY,
    WEIGHT_SOURCE_RELEVANCE,
    WEIGHT_METADATA_CONSISTENCY,
)
from app.models.candidate_schemas import DiscoveredCandidate, CandidateVerificationResult
from app.models.evidence_schemas import EvidenceScoreResult, SignalExplainability

logger = logging.getLogger("veridex.evidence_scoring")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# High reputation media and social platforms for source relevance evaluation
HIGH_REPUTATION_DOMAINS = {
    "wikipedia.org", "wikimedia.org", "bbc.com", "bbc.co.uk", "nytimes.com",
    "reuters.com", "apnews.com", "theguardian.com", "bloomberg.com", "washingtonpost.com",
    "instagram.com", "twitter.com", "x.com", "facebook.com", "linkedin.com",
    "youtube.com", "github.com", "flickr.com", "reddit.com", "pinterest.com"
}


def calculate_reverse_search_score(
    candidate_input: Union[DiscoveredCandidate, CandidateVerificationResult, Dict[str, Any], float, int, None],
) -> float:
    """Calculate normalized reverse-search engine relevance score [0.0 - 1.0].

    Evaluates match rank, candidate relevance score, and match classification ('exact' vs 'visual').

    Args:
        candidate_input: Discovered candidate object, verification result, dictionary, or raw score float.

    Returns:
        Float score bounded in range [0.0, 1.0], rounded to 2 decimal places.
    """
    if candidate_input is None:
        return 0.50

    if isinstance(candidate_input, (float, int)):
        return round(max(0.0, min(1.0, float(candidate_input))), 2)

    rank = 1
    match_type = "visual"
    relevance_score: Optional[float] = None

    if isinstance(candidate_input, DiscoveredCandidate):
        rank = candidate_input.rank
        match_type = candidate_input.match_type
        relevance_score = candidate_input.relevance_score
    elif isinstance(candidate_input, CandidateVerificationResult):
        return round(max(0.0, min(1.0, candidate_input.best_face_similarity)), 2)
    elif isinstance(candidate_input, dict):
        rank = candidate_input.get("rank", 1)
        match_type = candidate_input.get("match_type", "visual")
        relevance_score = candidate_input.get("relevance_score")

    if relevance_score is not None:
        return round(max(0.0, min(1.0, float(relevance_score))), 2)

    # Base score by match classification
    base_score = 0.95 if match_type == "exact" else 0.80

    # Rank decay penalty (1st rank = 1.0 multiplier, 10th rank = 0.73 multiplier)
    rank_multiplier = max(0.5, 1.0 - (max(1, rank) - 1) * 0.03)
    final_score = base_score * rank_multiplier

    return round(max(0.0, min(1.0, final_score)), 2)


def calculate_source_score(
    candidate_input: Union[DiscoveredCandidate, CandidateVerificationResult, Dict[str, Any], str, float, int, None],
) -> float:
    """Calculate source domain and publisher platform relevance score [0.0 - 1.0].

    Args:
        candidate_input: Candidate object, dictionary, URL/domain string, or numeric score.

    Returns:
        Float score bounded in range [0.0, 1.0], rounded to 2 decimal places.
    """
    if candidate_input is None:
        return 0.50

    if isinstance(candidate_input, (float, int)):
        return round(max(0.0, min(1.0, float(candidate_input))), 2)

    domain = ""
    source_type = "web"

    if isinstance(candidate_input, str):
        raw_str = candidate_input.strip()
        if raw_str.startswith(("http://", "https://")):
            try:
                domain = urlparse(raw_str).netloc.lower()
            except Exception:
                domain = raw_str.lower()
        else:
            domain = raw_str.lower()
    elif isinstance(candidate_input, DiscoveredCandidate):
        domain = candidate_input.source.lower()
        source_type = candidate_input.source_type
        if not domain and candidate_input.url:
            domain = urlparse(candidate_input.url).netloc.lower()
    elif isinstance(candidate_input, CandidateVerificationResult):
        if candidate_input.candidate_url:
            domain = urlparse(candidate_input.candidate_url).netloc.lower()
    elif isinstance(candidate_input, dict):
        domain = candidate_input.get("source", "").lower()
        source_type = candidate_input.get("source_type", "web")
        if not domain and candidate_input.get("url"):
            domain = urlparse(candidate_input["url"]).netloc.lower()

    # Clean domain string
    if domain.startswith("www."):
        domain = domain[4:]

    if not domain:
        return 0.50

    # Tier 1: High-reputation publishers or major platforms
    if any(high_dom in domain for high_dom in HIGH_REPUTATION_DOMAINS) or source_type == "social":
        return 0.80

    # Tier 2: Valid domain string
    if "." in domain and len(domain) > 4:
        return 0.70

    return 0.50


def calculate_metadata_score(
    metadata_input: Optional[Union[Dict[str, Any], float, int]] = None,
) -> float:
    """Calculate EXIF and contextual metadata consistency score [0.0 - 1.0].

    Evaluates consistency of metadata attributes (creation timestamp, location, camera tags, resolution).

    Args:
        metadata_input: Dictionary of metadata attributes or pre-computed numeric score.

    Returns:
        Float score bounded in range [0.0, 1.0], rounded to 2 decimal places.
    """
    if metadata_input is None:
        # Default neutral baseline for web-scraped images lacking EXIF headers
        return 0.90

    if isinstance(metadata_input, (float, int)):
        return round(max(0.0, min(1.0, float(metadata_input))), 2)

    if not isinstance(metadata_input, dict) or not metadata_input:
        return 0.90

    # Evaluate explicit metadata checks if dict provided
    total_checks = 0
    passed_checks = 0

    if "timestamp_match" in metadata_input:
        total_checks += 1
        if metadata_input["timestamp_match"]:
            passed_checks += 1

    if "location_match" in metadata_input:
        total_checks += 1
        if metadata_input["location_match"]:
            passed_checks += 1

    if "camera_make_match" in metadata_input:
        total_checks += 1
        if metadata_input["camera_make_match"]:
            passed_checks += 1

    if "resolution_aspect_match" in metadata_input:
        total_checks += 1
        if metadata_input["resolution_aspect_match"]:
            passed_checks += 1

    if "conflict_detected" in metadata_input and metadata_input["conflict_detected"]:
        return 0.20

    if total_checks == 0:
        return 0.90

    score = passed_checks / total_checks
    return round(max(0.0, min(1.0, score)), 2)


def calculate_overall_score(
    reverse_search: Union[DiscoveredCandidate, CandidateVerificationResult, Dict[str, Any], float, int, None] = 0.96,
    face_similarity: float = 0.91,
    image_similarity: float = 0.94,
    source: Union[DiscoveredCandidate, CandidateVerificationResult, Dict[str, Any], str, float, int, None] = 0.80,
    metadata: Optional[Union[Dict[str, Any], float, int]] = 0.90,
    candidate_id: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None,
) -> EvidenceScoreResult:
    """Calculate transparent weighted overall evidence correspondence score and component explainability.

    ==================================================
    IMPORTANT CONCEPTUAL DISTINCTION
    ==================================================
    The returned `overall_score` is NOT a probability of legal identity or legal identity proof.
    It is a multi-factor EVIDENCE CORRESPONDENCE SCORE combining independent visual and web signals.

    Args:
        reverse_search: Reverse search relevance score or candidate object.
        face_similarity: Cosine similarity score between input face and candidate face.
        image_similarity: pHash scene image similarity score.
        source: Source domain score, URL, or candidate object.
        metadata: Metadata consistency score or metadata dict.
        candidate_id: Optional candidate identifier string.
        weights: Optional dictionary overriding default signal weights.

    Returns:
        EvidenceScoreResult schema containing overall score, status, explainability, and weights.
    """
    # 1. Resolve Configured Signal Weights
    w_rev = weights.get("reverse_search", WEIGHT_REVERSE_SEARCH) if weights else WEIGHT_REVERSE_SEARCH
    w_face = weights.get("face_similarity", WEIGHT_FACE_SIMILARITY) if weights else WEIGHT_FACE_SIMILARITY
    w_img = weights.get("image_similarity", WEIGHT_IMAGE_SIMILARITY) if weights else WEIGHT_IMAGE_SIMILARITY
    w_src = weights.get("source_relevance", WEIGHT_SOURCE_RELEVANCE) if weights else WEIGHT_SOURCE_RELEVANCE
    w_meta = weights.get("metadata_consistency", WEIGHT_METADATA_CONSISTENCY) if weights else WEIGHT_METADATA_CONSISTENCY

    # Normalize weights so sum = 1.0 if custom weights provided
    total_w = w_rev + w_face + w_img + w_src + w_meta
    if total_w > 0 and abs(total_w - 1.0) > 1e-4:
        w_rev /= total_w
        w_face /= total_w
        w_img /= total_w
        w_src /= total_w
        w_meta /= total_w

    # 2. Compute Individual Component Scores
    s_rev = calculate_reverse_search_score(reverse_search)
    s_face = round(max(0.0, min(1.0, float(face_similarity))), 2)
    s_img = round(max(0.0, min(1.0, float(image_similarity))), 2)
    s_src = calculate_source_score(source)
    s_meta = calculate_metadata_score(metadata)

    # Resolve candidate_id if present in input objects
    if not candidate_id:
        if isinstance(reverse_search, (DiscoveredCandidate, CandidateVerificationResult)):
            candidate_id = reverse_search.candidate_id
        elif isinstance(reverse_search, dict):
            candidate_id = reverse_search.get("candidate_id")

    # 3. Compute Weighted Overall Evidence Correspondence Score
    raw_overall = (
        (s_rev * w_rev) +
        (s_face * w_face) +
        (s_img * w_img) +
        (s_src * w_src) +
        (s_meta * w_meta)
    )
    overall_score = round(max(0.0, min(1.0, raw_overall)), 2)

    # 4. Formulate Match Status Classification
    if overall_score >= 0.85:
        status = "HIGH_CORRESPONDENCE"
        assessment = f"High overall evidence correspondence ({overall_score:.2f}). Strong multi-signal alignment between input image and candidate source."
    elif overall_score >= 0.65:
        status = "MODERATE_CORRESPONDENCE"
        assessment = f"Moderate evidence correspondence ({overall_score:.2f}). Candidate matches the input face with moderate scene alignment."
    elif overall_score >= 0.45:
        status = "LOW_CORRESPONDENCE"
        assessment = f"Low evidence correspondence ({overall_score:.2f}). Partial signal alignment observed below confidence threshold."
    else:
        status = "INSUFFICIENT_CORRESPONDENCE"
        assessment = f"Insufficient evidence correspondence ({overall_score:.2f}). Signals do not support correspondence with candidate source."

    # 5. Build Component Explainability Breakdown for UI Display
    explainability: List[SignalExplainability] = [
        SignalExplainability(
            signal="reverse_search",
            label="✓ Reverse image evidence",
            score=s_rev,
            weight=round(w_rev, 2),
            weighted_score=round(s_rev * w_rev, 4),
            status="pass" if s_rev >= 0.70 else ("warning" if s_rev >= 0.50 else "fail"),
            details=f"Reverse search engine match relevance score: {s_rev:.2f} (Weight: {w_rev:.2f}).",
        ),
        SignalExplainability(
            signal="face_similarity",
            label="✓ Face correspondence",
            score=s_face,
            weight=round(w_face, 2),
            weighted_score=round(s_face * w_face, 4),
            status="pass" if s_face >= 0.70 else ("warning" if s_face >= 0.36 else "fail"),
            details=f"Face correspondence detected (SFace cosine similarity: {s_face:.2f}, Weight: {w_face:.2f}). Candidate matches the input face.",
        ),
        SignalExplainability(
            signal="image_similarity",
            label="✓ Perceptual similarity",
            score=s_img,
            weight=round(w_img, 2),
            weighted_score=round(s_img * w_img, 4),
            status="pass" if s_img >= 0.70 else ("warning" if s_img >= 0.50 else "fail"),
            details=f"Perceptual pHash scene image similarity: {s_img:.2f} (Weight: {w_img:.2f}).",
        ),
        SignalExplainability(
            signal="source_relevance",
            label="✓ Source relevance",
            score=s_src,
            weight=round(w_src, 2),
            weighted_score=round(s_src * w_src, 4),
            status="pass" if s_src >= 0.70 else ("warning" if s_src >= 0.50 else "fail"),
            details=f"Source domain and publisher platform score: {s_src:.2f} (Weight: {w_src:.2f}).",
        ),
        SignalExplainability(
            signal="metadata_consistency",
            label="✓ Metadata consistency",
            score=s_meta,
            weight=round(w_meta, 2),
            weighted_score=round(s_meta * w_meta, 4),
            status="pass" if s_meta >= 0.70 else ("warning" if s_meta >= 0.50 else "fail"),
            details=f"EXIF and contextual metadata consistency score: {s_meta:.2f} (Weight: {w_meta:.2f}).",
        ),
    ]

    active_weights = {
        "reverse_search": round(w_rev, 2),
        "face_similarity": round(w_face, 2),
        "image_similarity": round(w_img, 2),
        "source_relevance": round(w_src, 2),
        "metadata_consistency": round(w_meta, 2),
    }

    logger.info("Evidence score calculated | Candidate: %s | Overall: %.2f | Status: %s",
                candidate_id or "unknown", overall_score, status)

    return EvidenceScoreResult(
        candidate_id=candidate_id,
        reverse_search_score=s_rev,
        face_similarity=s_face,
        image_similarity=s_img,
        source_score=s_src,
        metadata_score=s_meta,
        overall_score=overall_score,
        status=status,
        explainability=explainability,
        weights_used=active_weights,
        assessment_summary=assessment,
        disclaimer=(
            "This score represents an evidence correspondence score based on multi-signal visual and metadata correlation. "
            "It does NOT represent a probability of legal identity."
        ),
    )
