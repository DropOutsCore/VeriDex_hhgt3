"""Pydantic schemas for candidate discovery, filtering, ranking, and independent face correlation verification."""

from typing import List, Optional
from pydantic import BaseModel, Field


class DiscoveredCandidate(BaseModel):
    """Normalized candidate source selected for downstream face verification."""
    candidate_id: str = Field(..., description="Unique deterministic identifier for candidate (e.g. cand_a1b2c3d4)")
    rank: int = Field(..., ge=1, description="Rank position of candidate after scoring")
    title: str = Field(..., description="Discovered page title or snippet description")
    source: str = Field(..., description="Publisher domain or platform name (e.g. instagram.com, wikipedia.org)")
    url: str = Field(..., description="Canonical web URL of candidate page")
    image_url: Optional[str] = Field(None, description="Direct URL of candidate visual asset")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail preview URL")
    match_type: str = Field("visual", description="Classification of search match ('exact' or 'visual')")
    source_type: str = Field("web", description="Category of candidate source ('social' or 'web')")
    relevance_score: Optional[float] = Field(None, description="Computed candidate evaluation score")


class CandidateDiscoveryResponse(BaseModel):
    """Structured response output for candidate discovery and ranking pipeline."""
    total_raw_candidates: int = Field(0, ge=0, description="Count of raw candidates received from search engine")
    filtered_candidates_count: int = Field(0, ge=0, description="Count of valid candidates remaining after filtering")
    social_candidates_count: int = Field(0, ge=0, description="Count of candidates originating from social media platforms")
    web_candidates_count: int = Field(0, ge=0, description="Count of candidates originating from general web pages")
    candidates: List[DiscoveredCandidate] = Field(default_factory=list, description="Ranked candidate list")
    error: Optional[str] = Field(None, description="Error message if candidate discovery pipeline failed")


from app.models.evidence_schemas import EvidenceScoreResult


class CandidateVerificationResult(BaseModel):
    """Result of independent face correlation and image similarity verification for a candidate."""
    candidate_id: str = Field(..., description="Unique candidate identifier")
    faces_detected: int = Field(0, ge=0, description="Total faces detected in candidate image")
    best_face_index: Optional[int] = Field(None, description="Index of candidate face yielding highest similarity score")
    best_face_similarity: float = Field(0.0, description="Highest cosine similarity score among candidate faces")
    image_similarity: float = Field(0.0, description="pHash image similarity between input image and candidate image")
    match_status: str = Field(..., description="Match status classification ('strong_correspondence', 'moderate_correspondence', 'low_correspondence', 'no_face_detected', 'candidate_unavailable')")
    assessment_notes: str = Field(..., description="Qualitative summary (e.g. Candidate face matches input face)")
    evidence_score: Optional[EvidenceScoreResult] = Field(None, description="Transparent multi-signal evidence correspondence score breakdown")
    candidate_url: Optional[str] = Field(None, description="Candidate web page URL")
    candidate_image_url: Optional[str] = Field(None, description="Candidate image URL")
    error: Optional[str] = Field(None, description="Error details if candidate download or processing failed")



class VerificationBatchResponse(BaseModel):
    """Structured response for verifying multiple candidates against an input image face."""
    total_candidates_evaluated: int = Field(0, ge=0, description="Total candidates processed")
    verified_matches_count: int = Field(0, ge=0, description="Count of candidates showing face correspondence")
    results: List[CandidateVerificationResult] = Field(default_factory=list, description="Verification results per candidate")
    error: Optional[str] = Field(None, description="Error message if batch verification failed")
