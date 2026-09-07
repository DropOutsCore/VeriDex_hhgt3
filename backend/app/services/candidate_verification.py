"""Independent Candidate Face Correlation & Verification Service.

==================================================
EDUCATIONAL OVERVIEW & DESIGN PRINCIPLES
==================================================

1. INDEPENDENT CORRELATION vs. SEARCH DISCOVERY:
   - Google Lens (Phase 4) is purely a DISCOVERY mechanism used to discover candidate images across the web.
   - YuNet + SFace (this module) is the INDEPENDENT CORRELATION mechanism.
   - WE DO NOT BLINDLY TRUST SEARCH ENGINE DISCOVERY. Every candidate image is independently downloaded,
     analyzed for human faces, converted into 128-D SFace embeddings, and compared against the input face.

2. MULTIPLE CANDIDATE FACES (Face A, Face B, Face C...):
   - Candidate web images often contain group photos or crowded scenes.
   - Every detected candidate face is independently embedded and compared against the target input face signature.
   - The face yielding the highest cosine similarity score is selected as the primary candidate face match.

3. DUAL-SIGNAL VERIFICATION:
   - Signal A (Biometric Visual Correlation): SFace Cosine Similarity between face embeddings.
   - Signal B (Global Scene Similarity): pHash Hamming Distance & Normalized Image Similarity.
   - Note: pHash evaluates global background/scene similarity and DOES NOT replace face signature matching.

4. TERMINOLOGY & LANGUAGE CONSTRAINTS:
   - NEVER CLAIM: "Identity proven", "Absolute identity proof", or "Legal identity confirmed".
   - PERMISSIBLE TERMINOLOGY:
     - "Face correspondence detected."
     - "High face similarity."
     - "Candidate matches the input face."
"""

import logging
import os
import hashlib
from typing import List, Dict, Any, Union, Optional, Tuple
import cv2
import numpy as np
import httpx

from app.config import DEFAULT_SIMILARITY_THRESHOLD, SFACE_MODEL_PATH
from app.models.face_schemas import FaceDetectionResult, FaceDetection, FaceSignature
from app.models.candidate_schemas import (
    DiscoveredCandidate,
    CandidateVerificationResult,
    VerificationBatchResponse,
)
from app.services.face_service import (
    detect_faces,
    generate_face_embedding,
    calculate_face_similarity,
    load_sface_recognizer,
)
from app.services.evidence_scoring import calculate_overall_score
from app.utils.hashing import compare_image_hashes


logger = logging.getLogger("veridex.candidate_verification")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def download_candidate_image(
    image_input: Union[str, bytes, bytearray, np.ndarray],
    timeout_seconds: float = 15.0,
) -> Optional[np.ndarray]:
    """Download or decode candidate image asset into an OpenCV BGR NumPy matrix.

    Handles edge cases gracefully without crashing:
    - Candidate server unavailable / HTTP 404 / HTTP 500
    - Network timeout / Connection drop
    - Invalid or corrupted binary bytes

    Args:
        image_input: Candidate image URL, local file path, raw binary bytes, or NumPy array.
        timeout_seconds: Network request timeout limit in seconds.

    Returns:
        OpenCV BGR numpy image matrix or None if image could not be acquired.
    """
    if isinstance(image_input, np.ndarray):
        if image_input.size == 0 or len(image_input.shape) < 2:
            return None
        return image_input

    if isinstance(image_input, (bytes, bytearray)):
        if not image_input or len(image_input) == 0:
            return None
        try:
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img if (img is not None and img.size > 0) else None
        except Exception as e:
            logger.warning("Failed to decode candidate image bytes: %s", str(e))
            return None

    if isinstance(image_input, str):
        clean_input = image_input.strip()
        if not clean_input:
            return None

        # Handle local disk file
        if os.path.exists(clean_input):
            try:
                img = cv2.imread(clean_input)
                return img if (img is not None and img.size > 0) else None
            except Exception as e:
                logger.warning("Failed to read local candidate image '%s': %s", clean_input, str(e))
                return None

        # Handle HTTP / HTTPS network URL
        if clean_input.startswith(("http://", "https://")):
            from app.utils.security_utils import is_ssrf_safe_url
            is_safe, reason = is_ssrf_safe_url(clean_input)
            if not is_safe:
                logger.warning("SSRF Protection blocked URL '%s': %s", clean_input, reason)
                return None

            logger.info("Downloading candidate image from URL: %s", clean_input)
            try:
                with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
                    resp = client.get(clean_input)

                if resp.status_code != 200:
                    logger.warning("Candidate image download HTTP error | Status: %d | URL: %s", resp.status_code, clean_input)
                    return None

                nparr = np.frombuffer(resp.content, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None or img.size == 0:
                    logger.warning("Downloaded candidate payload is not a valid image format: %s", clean_input)
                    return None
                return img

            except httpx.TimeoutException:
                logger.warning("Candidate image download timed out (%.1fs): %s", timeout_seconds, clean_input)
                return None
            except Exception as e:
                logger.warning("Network failure downloading candidate image '%s': %s", clean_input, str(e))
                return None

    return None


def detect_candidate_faces(image: np.ndarray) -> FaceDetectionResult:
    """Detect all faces present in a candidate image matrix using OpenCV YuNet."""
    return detect_faces(image, generate_signatures=True)


def generate_candidate_embeddings(
    image: np.ndarray,
    face_detections: List[FaceDetection],
) -> List[np.ndarray]:
    """Generate 128-dimensional SFace normalized feature vectors for all detected faces in an image."""
    if not face_detections or image is None or image.size == 0:
        return []

    try:
        sface = load_sface_recognizer()
    except Exception as e:
        logger.error("Failed to load SFace model for candidate verification: %s", str(e))
        return []

    embeddings: List[np.ndarray] = []
    for face in face_detections:
        try:
            emb, _, _ = generate_face_embedding(image, face, sface_recognizer=sface)
            embeddings.append(emb)
        except Exception as e:
            logger.warning("Failed to generate embedding for candidate face: %s", str(e))

    return embeddings


def compare_candidate_faces(
    input_embedding: np.ndarray,
    candidate_embeddings: List[np.ndarray],
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> Tuple[Optional[int], float]:
    """Compare target input face embedding against all candidate face embeddings (Face A, Face B, Face C...).

    Args:
        input_embedding: 128-D normalized target input face feature vector.
        candidate_embeddings: List of candidate face 128-D feature vectors.
        threshold: Cosine similarity threshold.

    Returns:
        Tuple containing:
        - best_face_index: 0-indexed integer position of best matching face, or None if no candidate faces.
        - best_similarity: Highest cosine similarity matching score achieved.
    """
    if input_embedding is None or not candidate_embeddings:
        return None, 0.0

    best_idx: Optional[int] = None
    max_similarity: float = -1.0

    for idx, candidate_emb in enumerate(candidate_embeddings):
        sim_result = calculate_face_similarity(input_embedding, candidate_emb, threshold=threshold)
        score = sim_result.matching_score

        if score > max_similarity:
            max_similarity = score
            best_idx = idx

    final_score = round(max(-1.0, min(1.0, max_similarity)), 4) if best_idx is not None else 0.0
    return best_idx, final_score


def select_best_face(
    input_embedding: np.ndarray,
    candidate_image: np.ndarray,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> Dict[str, Any]:
    """Detect faces in candidate image, extract embeddings, and identify the best matching candidate face.

    Returns:
        Dict containing faces_detected count, best_face_index, and best_similarity score.
    """
    detection_res = detect_candidate_faces(candidate_image)
    if not detection_res.face_detected or len(detection_res.faces) == 0:
        return {
            "faces_detected": 0,
            "best_face_index": None,
            "best_similarity": 0.0,
            "detections": [],
        }

    candidate_embs = generate_candidate_embeddings(candidate_image, detection_res.faces)
    best_idx, best_sim = compare_candidate_faces(input_embedding, candidate_embs, threshold=threshold)

    return {
        "faces_detected": len(detection_res.faces),
        "best_face_index": best_idx,
        "best_similarity": best_sim,
        "detections": detection_res.faces,
    }


def verify_candidate_image(
    input_image_or_embedding: Union[np.ndarray, bytes, Tuple[np.ndarray, np.ndarray]],
    candidate_input: Union[DiscoveredCandidate, Dict[str, Any], str, np.ndarray],
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> CandidateVerificationResult:
    """Independently verify face correlation and image similarity for a candidate source.

    Pipeline:
    1. Extract primary target face embedding & image matrix from input evidence.
    2. Download & decode candidate image matrix (handling network/file errors gracefully).
    3. Calculate global pHash image similarity between input and candidate scene.
    4. Detect all faces in candidate image (Face A, Face B, Face C).
    5. Compare all candidate faces against target input face signature -> Select best face & matching score.
    6. Formulate match status classification & qualitative assessment using permissible language.

    Args:
        input_image_or_embedding: Input evidence BGR array, bytes, or (input_img, input_emb) tuple.
        candidate_input: DiscoveredCandidate object, dictionary, URL string, or image matrix.
        threshold: Similarity threshold for decision boundary.

    Returns:
        CandidateVerificationResult schema.
    """
    candidate_id = "cand_unknown"
    candidate_url: Optional[str] = None
    candidate_image_url: Optional[str] = None
    raw_candidate_image: Any = None

    if isinstance(candidate_input, DiscoveredCandidate):
        candidate_id = candidate_input.candidate_id
        candidate_url = candidate_input.url
        candidate_image_url = candidate_input.image_url or candidate_input.thumbnail_url
        raw_candidate_image = candidate_image_url or candidate_url
    elif isinstance(candidate_input, dict):
        candidate_id = candidate_input.get("candidate_id", "cand_unknown")
        candidate_url = candidate_input.get("url")
        candidate_image_url = candidate_input.get("image_url") or candidate_input.get("thumbnail_url")
        raw_candidate_image = candidate_image_url or candidate_url
    elif isinstance(candidate_input, (str, np.ndarray, bytes)):
        raw_candidate_image = candidate_input
        if isinstance(candidate_input, str):
            candidate_url = candidate_input
            candidate_id = f"cand_{hashlib.md5(candidate_input.encode()).hexdigest()[:8]}"

    # 1. Resolve Input Image Matrix & Target Face Embedding
    input_img: Optional[np.ndarray] = None
    input_emb: Optional[np.ndarray] = None

    if isinstance(input_image_or_embedding, tuple) and len(input_image_or_embedding) == 2:
        input_img, input_emb = input_image_or_embedding
    elif isinstance(input_image_or_embedding, (np.ndarray, bytes)):
        input_img = download_candidate_image(input_image_or_embedding)

    if input_img is not None and input_emb is None:
        res_in = detect_faces(input_img, generate_signatures=True)
        if res_in.face_detected and len(res_in.faces) > 0:
            sface = load_sface_recognizer()
            input_emb, _, _ = generate_face_embedding(input_img, res_in.faces[0], sface_recognizer=sface)

    if input_img is None or input_emb is None:
        return CandidateVerificationResult(
            candidate_id=candidate_id,
            faces_detected=0,
            best_face_index=None,
            best_face_similarity=0.0,
            image_similarity=0.0,
            match_status="input_error",
            assessment_notes="Failed to extract target face signature from primary input image.",
            candidate_url=candidate_url,
            candidate_image_url=candidate_image_url,
            error="Input evidence image does not contain a detectable face.",
        )

    # 2. Acquire Candidate Image Matrix
    cand_img = download_candidate_image(raw_candidate_image)
    if cand_img is None:
        logger.warning("Candidate image acquisition failed for ID '%s'", candidate_id)
        return CandidateVerificationResult(
            candidate_id=candidate_id,
            faces_detected=0,
            best_face_index=None,
            best_face_similarity=0.0,
            image_similarity=0.0,
            match_status="candidate_unavailable",
            assessment_notes="Candidate image asset unavailable or unreadable.",
            candidate_url=candidate_url,
            candidate_image_url=candidate_image_url,
            error="Candidate image asset could not be downloaded or decoded.",
        )

    # 3. Calculate Global Scene pHash Similarity
    img_sim = 0.0
    try:
        hash_comp = compare_image_hashes(input_img, cand_img)
        img_sim = float(hash_comp.get("phash_similarity", 0.0))
    except Exception as e:
        logger.warning("pHash comparison error for candidate ID '%s': %s", candidate_id, str(e))
        img_sim = 0.0

    # 4. Perform Face Detection & Independent Face Correlation
    face_correlation = select_best_face(input_emb, cand_img, threshold=threshold)
    faces_detected = face_correlation["faces_detected"]
    best_face_idx = face_correlation["best_face_index"]
    best_face_sim = face_correlation["best_similarity"]

    # 5. Formulate Match Status & Qualitative Assessment (Strictly enforcing non-absolute terminology)
    if faces_detected == 0:
        match_status = "no_face_detected"
        assessment = "No face detected in candidate image."
    elif best_face_sim >= 0.70:
        match_status = "strong_correspondence"
        assessment = f"Strong face correspondence detected (High face similarity score: {best_face_sim:.2f}). Candidate matches the input face."
    elif best_face_sim >= threshold:
        match_status = "moderate_correspondence"
        assessment = f"Face correspondence detected (Matching score: {best_face_sim:.2f} above decision threshold)."
    else:
        match_status = "low_correspondence"
        assessment = f"Low face similarity (Matching score: {best_face_sim:.2f} below threshold)."

    # 6. Compute Multi-Signal Transparent Evidence Score
    evidence_score_obj = calculate_overall_score(
        reverse_search=candidate_input,
        face_similarity=best_face_sim,
        image_similarity=img_sim,
        source=candidate_input,
        candidate_id=candidate_id,
    )

    logger.info("Verification complete | ID: %s | Faces: %d | Best Face Sim: %.2f | Scene Sim: %.2f | Overall Score: %.2f | Status: %s",
                candidate_id, faces_detected, best_face_sim, img_sim, evidence_score_obj.overall_score, match_status)

    return CandidateVerificationResult(
        candidate_id=candidate_id,
        faces_detected=faces_detected,
        best_face_index=best_face_idx,
        best_face_similarity=best_face_sim,
        image_similarity=img_sim,
        match_status=match_status,
        assessment_notes=assessment,
        evidence_score=evidence_score_obj,
        candidate_url=candidate_url,
        candidate_image_url=candidate_image_url,
        error=None,
    )



def verify_candidate_batch(
    input_image_or_bytes: Union[np.ndarray, bytes],
    candidates: List[Union[DiscoveredCandidate, Dict[str, Any]]],
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> VerificationBatchResponse:
    """Batch verify multiple discovered candidates against a primary evidence input face image."""
    results: List[CandidateVerificationResult] = []
    matches_count = 0

    # Acquire input image & target embedding once
    input_img = download_candidate_image(input_image_or_bytes)
    input_emb: Optional[np.ndarray] = None

    if input_img is not None:
        res_in = detect_faces(input_img, generate_signatures=True)
        if res_in.face_detected and len(res_in.faces) > 0:
            sface = load_sface_recognizer()
            input_emb, _, _ = generate_face_embedding(input_img, res_in.faces[0], sface_recognizer=sface)

    if input_img is None or input_emb is None:
        return VerificationBatchResponse(
            total_candidates_evaluated=len(candidates),
            verified_matches_count=0,
            results=[],
            error="Primary evidence input image does not contain a valid detectable face.",
        )

    for cand in candidates:
        res = verify_candidate_image((input_img, input_emb), cand, threshold=threshold)
        results.append(res)
        if res.match_status in ("strong_correspondence", "moderate_correspondence"):
            matches_count += 1

    return VerificationBatchResponse(
        total_candidates_evaluated=len(candidates),
        verified_matches_count=matches_count,
        results=results,
        error=None,
    )
