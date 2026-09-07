"""Pydantic schemas for Phase 7 Evidence Scoring & Explainability."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SignalExplainability(BaseModel):
    """Detailed explainability representation for an individual evidence signal."""
    signal: str = Field(..., description="Key identifier of evidence signal (e.g. reverse_search, face_similarity)")
    label: str = Field(..., description="Human-readable label for UI display (e.g. Reverse image evidence, Face correspondence)")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized score achieved for this signal [0.0 - 1.0]")
    weight: float = Field(..., ge=0.0, le=1.0, description="Configured weight contribution of this signal")
    weighted_score: float = Field(..., ge=0.0, le=1.0, description="Product of score * weight")
    status: str = Field("pass", description="Signal status ('pass', 'warning', 'fail')")
    details: str = Field(..., description="Qualitative explanation of how this component score was calculated")


class EvidenceScoreResult(BaseModel):
    """Structured response output for Phase 7 Evidence Scoring.

    ==================================================
    IMPORTANT CONCEPTUAL DISTINCTION
    ==================================================
    The `overall_score` is NOT a probability of legal identity or legal proof of identity.
    It is a transparent, multi-factor EVIDENCE CORRESPONDENCE SCORE measuring independent signal correlation
    between the input image evidence and discovered web candidates.
    """
    candidate_id: Optional[str] = Field(None, description="Unique candidate identifier being evaluated")
    reverse_search_score: float = Field(..., ge=0.0, le=1.0, description="Reverse search match relevance score")
    face_similarity: float = Field(..., ge=-1.0, le=1.0, description="Independent OpenCV SFace cosine similarity score")
    image_similarity: float = Field(..., ge=0.0, le=1.0, description="Perceptual pHash scene image similarity score")
    source_score: float = Field(..., ge=0.0, le=1.0, description="Publisher domain & source platform relevance score")
    metadata_score: float = Field(..., ge=0.0, le=1.0, description="Metadata consistency score")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Weighted evidence correspondence score [0.0 - 1.0]")
    status: str = Field(..., description="Match status ('HIGH_CORRESPONDENCE', 'MODERATE_CORRESPONDENCE', 'LOW_CORRESPONDENCE', 'INSUFFICIENT_CORRESPONDENCE')")
    explainability: List[SignalExplainability] = Field(default_factory=list, description="Component breakdowns for UI explainability")
    weights_used: Dict[str, float] = Field(default_factory=dict, description="Active signal weights used in score computation")
    assessment_summary: str = Field(..., description="Qualitative explanation of the evidence verification outcome")
    disclaimer: str = Field(
        default="This score represents an evidence correspondence score based on multi-signal visual and metadata correlation. It does NOT represent a probability of legal identity.",
        description="Mandatory conceptual disclaimer distinguishing evidence correspondence from identity proof"
    )


class EvidencePackage(BaseModel):
    """Deterministic Evidence Package containing cryptographic hashes and non-PII verification metadata.

    ==================================================
    PRIVACY & ON-CHAIN SAFETY GUARANTEES
    ==================================================
    - NO raw binary image data
    - NO 128-dimensional raw face feature vectors
    - NO personal identifiable information (PII)
    Only cryptographic hashes, pHashes, similarity metrics, and public web source metadata.
    """
    record_id: str = Field(..., description="Unique deterministic verification event identifier")
    input_image_sha256: str = Field(..., description="SHA-256 hash digest of primary evidence input image file")
    input_image_phash: str = Field(..., description="Perceptual pHash hex string of primary evidence image scene")
    face_embedding_hash: str = Field(..., description="SHA-256 hash digest of normalized SFace 128-D embedding vector")
    matched_url: str = Field(..., description="Web URL of discovered matching candidate source")
    matched_image_sha256: str = Field(..., description="SHA-256 hash digest of candidate image asset")
    matched_image_phash: str = Field(..., description="Perceptual pHash hex string of candidate image asset")
    reverse_search_rank: int = Field(..., ge=1, description="Rank position of candidate in reverse search results")
    face_similarity: float = Field(..., description="Cosine similarity score between input face and best candidate face")
    image_similarity: float = Field(..., description="pHash scene image similarity score")
    overall_score: float = Field(..., description="Weighted multi-signal evidence correspondence score")
    search_provider: str = Field(default="Google Lens via SerpApi", description="Reverse search engine provider name")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of verification event execution")


class VeridexFingerprintResult(BaseModel):
    """Output result containing record_id and cryptographic evidence fingerprint hash (EVIDENCE DNA)."""
    record_id: str = Field(..., description="Unique verification record identifier")
    evidence_hash: str = Field(..., description="64-character SHA-256 cryptographic fingerprint over canonical evidence package")
    evidence_package: Optional[EvidencePackage] = Field(None, description="Complete underlying non-PII evidence package payload")
    canonical_json: Optional[str] = Field(None, description="Deterministic canonical JSON string representation")


class BlockchainAnchoringResult(BaseModel):
    """Structured response output for Phase 11 Blockchain Evidence Anchoring."""
    proof_id: str = Field(..., description="Unique proof identifier string")
    evidence_hash: str = Field(..., description="64-character SHA-256 Evidence DNA fingerprint string")
    transaction_hash: str = Field(..., description="On-chain transaction hash digest hex string")
    block_number: str = Field(..., description="Block number where transaction was confirmed on-chain")
    network: str = Field(default="Polygon Amoy", description="Target blockchain network name")


class OnChainProofRecord(BaseModel):
    """Retrieved proof record directly read from the VeridexRegistry smart contract on-chain."""
    proof_id: str = Field(..., description="Unique proof identifier hex string")
    evidence_hash: str = Field(..., description="Canonical Evidence DNA SHA-256 fingerprint hex string")
    input_image_hash: str = Field(..., description="Primary evidence image SHA-256 hash hex string")
    matched_image_hash: str = Field(..., description="Discovered candidate image SHA-256 hash hex string")
    timestamp: int = Field(..., description="Block timestamp integer when proof was anchored on-chain")
    submitter: str = Field(..., description="Ethereum wallet address of submitter")
    network: str = Field(default="Polygon Amoy", description="Target blockchain network name")


class IntegrityVerificationResult(BaseModel):
    """Structured response output for Phase 12 On-Chain Integrity & Tamper Detection."""
    local_hash: str = Field(..., description="Recomputed local canonical SHA-256 fingerprint hex string")
    on_chain_hash: str = Field(..., description="Evidence fingerprint hash retrieved directly from Polygon Amoy smart contract")
    verified: bool = Field(..., description="True if local_hash matches on_chain_hash, false if tampered")
    status: str = Field(..., description="Integrity status ('VERIFIED' or 'TAMPER_DETECTED')")
    proof_id: Optional[str] = Field(None, description="Unique proof record identifier being verified")
    details: Optional[str] = Field(None, description="Qualitative summary explanation of integrity check outcome")



