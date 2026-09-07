"""Pydantic schemas and Enum definitions for Phase 13 Full Backend Pipeline status and execution results."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.models.face_schemas import FaceDetectionResult
from app.models.lens_schemas import LensSearchResponse
from app.models.candidate_schemas import CandidateVerificationResult
from app.models.evidence_schemas import (
    EvidenceScoreResult,
    EvidencePackage,
    VeridexFingerprintResult,
    BlockchainAnchoringResult,
    IntegrityVerificationResult,
)


class PipelineStatus(str, Enum):
    """Pipeline execution status states according to Phase 13 requirements."""
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    ENCODING = "ENCODING"
    SEARCHING = "SEARCHING"
    DISCOVERING = "DISCOVERING"
    VERIFYING = "VERIFYING"
    FINGERPRINTING = "FINGERPRINTING"
    ANCHORING = "ANCHORING"
    CONFIRMING = "CONFIRMING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class PipelineStepLog(BaseModel):
    """Execution log for an individual pipeline state transition."""
    step: PipelineStatus = Field(..., description="Pipeline status state identifier")
    timestamp: str = Field(..., description="ISO 8601 timestamp when step was initiated")
    message: str = Field(..., description="Human-readable description of step execution")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional step-specific metadata")


class FullPipelineResult(BaseModel):
    """Structured response payload for end-to-end VERIDEX pipeline execution."""
    pipeline_id: str = Field(..., description="Unique pipeline execution session identifier")
    status: PipelineStatus = Field(..., description="Final or active pipeline status state")
    input_face_detected: bool = Field(default=False, description="True if target human face was detected in input image")
    
    face_detection: Optional[FaceDetectionResult] = Field(None, description="Phase 1 & 2 Face detection and signature results")
    search_response: Optional[LensSearchResponse] = Field(None, description="Phase 4 Reverse image search results")
    verified_candidate: Optional[CandidateVerificationResult] = Field(None, description="Phase 6 Candidate face correlation results")
    evidence_score: Optional[EvidenceScoreResult] = Field(None, description="Phase 7 Transparent multi-signal evidence score")
    evidence_package: Optional[EvidencePackage] = Field(None, description="Phase 8 Non-PII evidence package payload")
    fingerprint: Optional[VeridexFingerprintResult] = Field(None, description="Phase 8 Evidence DNA SHA-256 fingerprint")
    blockchain_anchoring: Optional[BlockchainAnchoringResult] = Field(None, description="Phase 11 Polygon Amoy smart contract proof anchoring result")
    on_chain_verification: Optional[IntegrityVerificationResult] = Field(None, description="Phase 12 On-chain integrity verification result")
    
    steps: List[PipelineStepLog] = Field(default_factory=list, description="Chronological log of pipeline state transitions")
    error: Optional[str] = Field(None, description="Structured user-friendly error message if pipeline failed")
