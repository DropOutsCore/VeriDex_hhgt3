"""API route definitions for Phase 13 Full Backend Pipeline, image scanning, face detection, face signature extraction, Google Lens reverse search, candidate verification, evidence scoring, blockchain anchoring, and tamper testing."""

from typing import Optional, List
import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Query

from app.models.face_schemas import FaceDetectionResult, FaceSimilarityResult
from app.models.lens_schemas import LensSearchResponse
from app.models.candidate_schemas import CandidateVerificationResult, VerificationBatchResponse
from app.models.evidence_schemas import (
    EvidenceScoreResult,
    EvidencePackage,
    VeridexFingerprintResult,
    BlockchainAnchoringResult,
    OnChainProofRecord,
    IntegrityVerificationResult,
)
from app.models.pipeline_schemas import FullPipelineResult, PipelineStatus

from app.services.face_service import (
    detect_faces,
    generate_face_embedding,
    calculate_face_similarity,
    load_sface_recognizer,
)
from app.services.lens_service import execute_lens_search_pipeline
from app.services.candidate_verification import verify_candidate_image, verify_candidate_batch
from app.services.evidence_scoring import calculate_overall_score
from app.services.evidence_service import generate_veridex_fingerprint, create_evidence_package
from app.services.blockchain_service import (
    anchor_evidence,
    get_on_chain_proof,
    verify_evidence_integrity,
    simulate_tampering,
    BlockchainError,
    RPCFailureError,
    InsufficientGasError,
    TransactionRejectionError,
    BlockchainTimeoutError,
    InvalidContractError,
    WrongNetworkError,
)
from app.services.pipeline_service import execute_full_pipeline

from app.config import DEFAULT_SIMILARITY_THRESHOLD, SERPAPI_API_KEY

router = APIRouter(prefix="/api", tags=["VERIDEX Engine API"])


@router.get(
    "/health",
    summary="Health check endpoint for VERIDEX API core services",
    description="Returns backend service status, version info, and default pipeline status.",
)
async def health_check():
    """Health check endpoint to verify backend service status."""
    return {
        "status": "ok",
        "service": "VERIDEX Backend API",
        "version": "0.1.0",
        "pipeline_status": PipelineStatus.IDLE.value,
    }


@router.post(
    "/scan",
    response_model=FaceDetectionResult,
    summary="Scan image for faces and generate SFace Face Signatures",
    description=(
        "Accepts a multipart image upload, detects human faces using OpenCV YuNet, "
        "aligns facial landmarks, and computes 128-dimensional SFace Face Signatures "
        "along with SHA-256 fingerprint hashes."
    ),
)
async def scan_image(
    file: UploadFile = File(..., description="Target image file for analysis"),
) -> FaceDetectionResult:
    """Process uploaded image file and execute YuNet face detection & SFace signature generation."""
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded.",
        )

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file stream: {str(e)}",
        )

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    result = detect_faces(contents, generate_signatures=True)

    if result.error and ("Failed to decode" in result.error or "Invalid or corrupted" in result.error or "Unsupported image input" in result.error):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    return result


@router.post(
    "/compare",
    response_model=FaceSimilarityResult,
    summary="Compare two images for face signature correspondence",
    description=(
        "Uploads two image files (file1, file2), detects the primary face in each image, "
        "generates SFace Face Signature embeddings, and computes the Cosine Similarity matching score."
    ),
)
async def compare_faces(
    file1: UploadFile = File(..., description="Primary reference image file"),
    file2: UploadFile = File(..., description="Candidate image file for comparison"),
    threshold: Optional[float] = Query(
        DEFAULT_SIMILARITY_THRESHOLD,
        description="Configurable cosine similarity decision threshold",
    ),
) -> FaceSimilarityResult:
    """Detect faces in two images and compute cosine similarity matching score."""
    if not file1 or not file2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both file1 and file2 must be uploaded for comparison.",
        )

    bytes1 = await file1.read()
    bytes2 = await file2.read()

    if not bytes1 or not bytes2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or both uploaded files are empty (0 bytes).",
        )

    img1 = cv2.imdecode(np.frombuffer(bytes1, np.uint8), cv2.IMREAD_COLOR)
    if img1 is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode primary image (file1). Invalid or corrupt format.",
        )

    res1 = detect_faces(img1, generate_signatures=False)
    if not res1.face_detected or len(res1.faces) == 0:
        return FaceSimilarityResult(
            matching_score=0.0,
            correspondence_match=False,
            threshold_used=threshold or DEFAULT_SIMILARITY_THRESHOLD,
            quality_assessment="No face detected in primary image (file1).",
            error="Primary image does not contain a detectable face.",
        )

    img2 = cv2.imdecode(np.frombuffer(bytes2, np.uint8), cv2.IMREAD_COLOR)
    if img2 is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode candidate image (file2). Invalid or corrupt format.",
        )

    res2 = detect_faces(img2, generate_signatures=False)
    if not res2.face_detected or len(res2.faces) == 0:
        return FaceSimilarityResult(
            matching_score=0.0,
            correspondence_match=False,
            threshold_used=threshold or DEFAULT_SIMILARITY_THRESHOLD,
            quality_assessment="No face detected in candidate image (file2).",
            error="Candidate image does not contain a detectable face.",
        )

    try:
        sface = load_sface_recognizer()
        emb1, hash1, _ = generate_face_embedding(img1, res1.faces[0], sface_recognizer=sface)
        emb2, hash2, _ = generate_face_embedding(img2, res2.faces[0], sface_recognizer=sface)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate face signature embeddings: {str(e)}",
        )

    comparison_threshold = threshold if threshold is not None else DEFAULT_SIMILARITY_THRESHOLD
    similarity_result = calculate_face_similarity(emb1, emb2, threshold=comparison_threshold)
    similarity_result.face1_hash = hash1
    similarity_result.face2_hash = hash2

    return similarity_result


@router.post(
    "/search",
    response_model=LensSearchResponse,
    summary="Execute genuine Google Lens reverse image search via SerpApi",
    description=(
        "Performs a live reverse image search using SerpApi Google Lens engine. "
        "Accepts either a multipart image file upload or an image_url query parameter, "
        "and returns normalized web and social media candidate results."
    ),
)
async def search_image(
    file: Optional[UploadFile] = File(None, description="Image file to upload for reverse search"),
    image_url: Optional[str] = Query(None, description="Public image URL to query"),
) -> LensSearchResponse:
    """Execute live Google Lens reverse search query."""
    if not file and not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either an uploaded image 'file' or an 'image_url' parameter.",
        )

    if not SERPAPI_API_KEY:
        return LensSearchResponse(
            search_executed=False,
            total_results_found=0,
            error="SERPAPI_API_KEY environment variable is not configured. Please set SERPAPI_API_KEY in your .env file.",
        )

    if file:
        try:
            contents = await file.read()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read image file stream: {str(e)}",
            )
        if not contents or len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image file is empty (0 bytes).",
            )
        return execute_lens_search_pipeline(contents)

    return execute_lens_search_pipeline(image_url)  # type: ignore[arg-type]


@router.post(
    "/verify",
    response_model=CandidateVerificationResult,
    summary="Independently verify candidate face correlation against input evidence image",
    description=(
        "Independently downloads candidate image asset, detects all faces present in candidate image, "
        "generates 128-D SFace embeddings, computes cosine similarity against primary evidence input face, "
        "and calculates pHash image scene similarity."
    ),
)
async def verify_candidate(
    input_file: UploadFile = File(..., description="Primary evidence image containing target face"),
    candidate_file: Optional[UploadFile] = File(None, description="Discovered candidate image file"),
    candidate_url: Optional[str] = Query(None, description="Discovered candidate image URL"),
    threshold: Optional[float] = Query(
        DEFAULT_SIMILARITY_THRESHOLD,
        description="Cosine similarity decision threshold",
    ),
) -> CandidateVerificationResult:
    """Independently verify candidate image face correlation."""
    if not input_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must upload primary evidence 'input_file'.",
        )
    if not candidate_file and not candidate_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either candidate_file upload or candidate_url parameter.",
        )

    try:
        input_bytes = await input_file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read input_file stream: {str(e)}",
        )

    if candidate_file:
        try:
            cand_bytes = await candidate_file.read()
            return verify_candidate_image(input_bytes, cand_bytes, threshold=threshold or DEFAULT_SIMILARITY_THRESHOLD)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read candidate_file stream: {str(e)}",
            )

    return verify_candidate_image(input_bytes, candidate_url, threshold=threshold or DEFAULT_SIMILARITY_THRESHOLD)  # type: ignore[arg-type]


@router.post(
    "/score-evidence",
    response_model=EvidenceScoreResult,
    summary="Compute transparent multi-signal evidence correspondence score",
    description=(
        "Combines independent evidence signals (reverse search relevance, SFace face similarity, "
        "pHash image scene similarity, source domain relevance, metadata consistency) into a transparent "
        "evidence correspondence score with full signal breakdown for UI explainability."
    ),
)
async def score_evidence(
    reverse_search_score: float = Query(0.96, ge=0.0, le=1.0, description="Reverse search match relevance score"),
    face_similarity: float = Query(0.91, ge=-1.0, le=1.0, description="SFace face embedding cosine similarity score"),
    image_similarity: float = Query(0.94, ge=0.0, le=1.0, description="Perceptual pHash scene image similarity score"),
    source_score: float = Query(0.80, ge=0.0, le=1.0, description="Publisher platform & domain relevance score"),
    metadata_score: float = Query(0.90, ge=0.0, le=1.0, description="EXIF & context metadata consistency score"),
    candidate_id: Optional[str] = Query(None, description="Unique candidate identifier string"),
) -> EvidenceScoreResult:
    """Compute weighted evidence score and return component explainability."""
    return calculate_overall_score(
        reverse_search=reverse_search_score,
        face_similarity=face_similarity,
        image_similarity=image_similarity,
        source=source_score,
        metadata=metadata_score,
        candidate_id=candidate_id,
    )


@router.post(
    "/fingerprint",
    response_model=VeridexFingerprintResult,
    summary="Generate reproducible cryptographic evidence fingerprint (EVIDENCE DNA)",
    description=(
        "Accepts a deterministic Evidence Package payload and generates a canonical SHA-256 evidence_hash "
        "cryptographic fingerprint ready for blockchain anchoring."
    ),
)
async def generate_fingerprint(
    package: EvidencePackage,
) -> VeridexFingerprintResult:
    """Generate canonical SHA-256 fingerprint for an evidence package."""
    return generate_veridex_fingerprint(package)


@router.post(
    "/anchor",
    response_model=BlockchainAnchoringResult,
    summary="Anchor Evidence DNA fingerprint onto Polygon Amoy Testnet via Web3",
    description=(
        "Submits a real Web3 transaction to anchor a deterministic evidence fingerprint onto the deployed "
        "VeridexRegistry smart contract on Polygon Amoy Testnet."
    ),
)
async def anchor_evidence_to_blockchain(
    package: EvidencePackage,
) -> BlockchainAnchoringResult:
    """Anchor evidence package onto Polygon Amoy smart contract via Web3.py."""
    try:
        return anchor_evidence(package)
    except RPCFailureError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Blockchain RPC Failure: {str(e)}")
    except WrongNetworkError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Wrong Network Configuration: {str(e)}")
    except InvalidContractError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid Smart Contract: {str(e)}")
    except InsufficientGasError as e:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"Insufficient Gas Fees: {str(e)}")
    except TransactionRejectionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Transaction Rejected / Reverted: {str(e)}")
    except BlockchainTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"Transaction Timeout: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Blockchain Anchoring Error: {str(e)}")


@router.get(
    "/proof/{proof_id}",
    response_model=OnChainProofRecord,
    summary="Retrieve anchored proof record directly from Polygon Amoy smart contract",
    description=(
        "Queries the deployed VeridexRegistry smart contract on Polygon Amoy to retrieve the on-chain "
        "proof record details for a given proof_id."
    ),
)
async def get_proof_from_blockchain(
    proof_id: str,
) -> OnChainProofRecord:
    """Query on-chain proof record from VeridexRegistry contract."""
    try:
        return get_on_chain_proof(proof_id)
    except TransactionRejectionError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch on-chain proof: {str(e)}")


@router.post(
    "/verify-integrity",
    response_model=IntegrityVerificationResult,
    summary="Verify evidence integrity by reading on-chain smart contract record",
    description=(
        "Reads the actual anchored record from VeridexRegistry contract on Polygon Amoy, "
        "recomputes the local canonical SHA-256 evidence fingerprint, and compares hashes for tamper detection."
    ),
)
@router.post(
    "/verify-chain",
    response_model=IntegrityVerificationResult,
    summary="Verify evidence integrity on-chain (Alias for /verify-integrity)",
)
async def verify_integrity_endpoint(
    package: EvidencePackage,
) -> IntegrityVerificationResult:
    """Verify evidence package against on-chain smart contract record."""
    try:
        return verify_evidence_integrity(package)
    except TransactionRejectionError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Integrity check failed: {str(e)}")


@router.post(
    "/simulate-tampering",
    response_model=EvidencePackage,
    summary="Simulate evidence payload tampering",
    description=(
        "Alters a single field (e.g. matched_url, face_similarity) of an Evidence Package "
        "while preserving record_id to test on-chain tamper detection."
    ),
)
@router.post(
    "/tamper-test",
    response_model=EvidencePackage,
    summary="Simulate evidence payload tampering (Alias for /simulate-tampering)",
)
async def simulate_tampering_endpoint(
    package: EvidencePackage,
    field_to_modify: str = Query("matched_url", description="Field attribute to tamper"),
    new_value: str = Query("https://tampered-malicious-site.com/fake.jpg", description="Tampered replacement value"),
) -> EvidencePackage:
    """Simulate single-field evidence payload tampering."""
    try:
        return simulate_tampering(package, field_to_modify=field_to_modify, new_value=new_value)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tamper simulation error: {str(e)}")


@router.post(
    "/pipeline",
    response_model=FullPipelineResult,
    summary="Run full end-to-end VERIDEX verification pipeline",
    description=(
        "Uploads a primary image and executes the complete pipeline: "
        "Face Detection -> Face Signature Encoding -> Reverse Image Search -> Candidate Discovery -> "
        "Candidate Verification -> Evidence Scoring -> Evidence DNA Fingerprinting -> (Optional) Blockchain Anchoring."
    ),
)
async def run_full_pipeline_endpoint(
    file: UploadFile = File(..., description="Target primary evidence image file"),
    auto_anchor: bool = Query(False, description="If True, attempts on-chain Polygon Amoy anchoring"),
) -> FullPipelineResult:
    """Execute end-to-end VERIDEX pipeline for an uploaded image file."""
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded for pipeline execution.",
        )

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read image file stream: {str(e)}",
        )

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    result = execute_full_pipeline(contents, auto_anchor=auto_anchor)
    return result
