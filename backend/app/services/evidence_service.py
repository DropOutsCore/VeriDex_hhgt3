"""Phase 8 VERIDEX Fingerprint / Evidence DNA Service.

==================================================
CONCEPTUAL & PRIVACY ARCHITECTURE
==================================================

1. DETERMINISTIC CRYPTOGRAPHIC FINGERPRINT (EVIDENCE DNA):
   - Combines primary evidence image fingerprints (SHA-256 & pHash), target face signature hash,
     and candidate match provenance metadata into a single canonical Evidence Package.
   - Canonicalizes JSON deterministically (sorted keys, compact formatting, float normalization).
   - Generates SHA-256 hash over canonical JSON -> `evidence_hash`.

2. REPRODUCIBILITY GUARANTEE:
   - The exact same evidence inputs will ALWAYS yield the exact same `evidence_hash`.
   - Modifying even 1 bit or 1 parameter results in a completely distinct `evidence_hash`.

3. STRICT ON-CHAIN PRIVACY PRESERVATION:
   - RAW BINARY IMAGES ARE NEVER STORED IN THE EVIDENCE PACKAGE OR ANCHORED ON-CHAIN.
   - RAW 128-DIMENSIONAL SFACE FACE EMBEDDINGS ARE NEVER STORED IN THE EVIDENCE PACKAGE.
   - PERSONAL IDENTIFIABLE INFORMATION (PII) IS NEVER STORED IN THE EVIDENCE PACKAGE.
   - Only non-reversible cryptographic hashes, pHashes, normalized similarity metrics, and web match URLs are preserved.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Union, Optional
import numpy as np

from app.models.evidence_schemas import EvidencePackage, VeridexFingerprintResult
from app.utils.canonical_json import canonicalize_json, canonical_sha256
from app.utils.hashing import sha256_bytes

logger = logging.getLogger("veridex.evidence_service")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def hash_face_embedding(embedding: Union[np.ndarray, list, str, bytes]) -> str:
    """Helper to convert raw face embedding vector or bytes into a SHA-256 hash string."""
    if isinstance(embedding, str):
        clean_str = embedding.strip()
        if len(clean_str) == 64 and all(c in "0123456789abcdefABCDEF" for c in clean_str):
            return clean_str.lower()
        return hashlib.sha256(clean_str.encode("utf-8")).hexdigest()

    if isinstance(embedding, np.ndarray):
        norm_emb = embedding.astype(np.float32).tobytes()
        return hashlib.sha256(norm_emb).hexdigest()

    if isinstance(embedding, (list, tuple)):
        arr = np.array(embedding, dtype=np.float32).tobytes()
        return hashlib.sha256(arr).hexdigest()

    if isinstance(embedding, (bytes, bytearray)):
        return sha256_bytes(embedding)

    raise TypeError(f"Unsupported face embedding type for hashing: {type(embedding).__name__}")


def create_evidence_package(
    input_image_sha256: str,
    input_image_phash: str,
    face_embedding: Union[str, np.ndarray, list, bytes],
    matched_url: str,
    matched_image_sha256: str,
    matched_image_phash: str,
    reverse_search_rank: int = 1,
    face_similarity: float = 0.0,
    image_similarity: float = 0.0,
    overall_score: float = 0.0,
    search_provider: str = "Google Lens via SerpApi",
    record_id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> EvidencePackage:
    """Create a deterministic non-PII Evidence Package containing cryptographic hashes and metrics.

    Args:
        input_image_sha256: SHA-256 hash of primary input image file.
        input_image_phash: Perceptual pHash hex string of input image.
        face_embedding: Target face embedding vector, array, or pre-computed SHA-256 hash string.
        matched_url: Discovered candidate page or asset web URL.
        matched_image_sha256: SHA-256 hash of candidate image file.
        matched_image_phash: Perceptual pHash hex string of candidate image.
        reverse_search_rank: Candidate search result rank position.
        face_similarity: Cosine similarity score between input and candidate face.
        image_similarity: pHash scene image similarity score.
        overall_score: Weighted evidence correspondence score.
        search_provider: Reverse search engine provider name.
        record_id: Optional unique record identifier. Auto-generated if None.
        timestamp: Optional ISO 8601 UTC timestamp string. Auto-generated if None.

    Returns:
        EvidencePackage Pydantic schema instance.
    """
    # Hash face embedding if passed as vector
    emb_hash = hash_face_embedding(face_embedding)

    # Standardize timestamp
    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Generate deterministic record_id if not supplied
    if not record_id:
        raw_seed = f"{input_image_sha256[:16]}_{matched_url}_{timestamp}"
        rec_hash = hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()[:12]
        record_id = f"rec_{rec_hash}"

    package = EvidencePackage(
        record_id=record_id,
        input_image_sha256=input_image_sha256.lower(),
        input_image_phash=input_image_phash.lower(),
        face_embedding_hash=emb_hash.lower(),
        matched_url=matched_url,
        matched_image_sha256=matched_image_sha256.lower(),
        matched_image_phash=matched_image_phash.lower(),
        reverse_search_rank=max(1, int(reverse_search_rank)),
        face_similarity=round(float(face_similarity), 4),
        image_similarity=round(float(image_similarity), 4),
        overall_score=round(float(overall_score), 4),
        search_provider=search_provider,
        timestamp=timestamp,
    )

    logger.info("Created Evidence Package | Record ID: %s | Match URL: %s", record_id, matched_url)
    return package


def canonicalize_evidence(evidence_input: Union[EvidencePackage, Dict[str, Any]]) -> str:
    """Serialize an evidence package or dictionary into a deterministic canonical JSON string.

    Args:
        evidence_input: EvidencePackage object or dictionary.

    Returns:
        Deterministic canonical JSON string with sorted keys and normalized floats.
    """
    if isinstance(evidence_input, EvidencePackage):
        data = evidence_input.model_dump()
    elif isinstance(evidence_input, dict):
        data = evidence_input
    else:
        raise TypeError(f"Expected EvidencePackage or dict, got {type(evidence_input).__name__}")

    return canonicalize_json(data, float_precision=4)


def generate_veridex_fingerprint(
    evidence_input: Union[EvidencePackage, Dict[str, Any]],
) -> VeridexFingerprintResult:
    """Generate reproducible cryptographic SHA-256 evidence fingerprint (EVIDENCE DNA) for a verification event.

    Pipeline:
    Evidence Object -> Canonicalize JSON -> SHA-256 Digest -> VERIDEX Fingerprint Result

    Args:
        evidence_input: EvidencePackage object or dictionary.

    Returns:
        VeridexFingerprintResult schema containing record_id, evidence_hash, package, and canonical JSON.
    """
    if isinstance(evidence_input, EvidencePackage):
        package = evidence_input
        record_id = package.record_id
    elif isinstance(evidence_input, dict):
        package = EvidencePackage(**evidence_input)
        record_id = package.record_id
    else:
        raise TypeError(f"Expected EvidencePackage or dict, got {type(evidence_input).__name__}")

    canonical_str = canonicalize_evidence(package)
    evidence_hash = canonical_sha256(package, float_precision=4)

    logger.info("Generated VERIDEX Fingerprint | Record ID: %s | Evidence Hash: %s", record_id, evidence_hash)

    return VeridexFingerprintResult(
        record_id=record_id,
        evidence_hash=evidence_hash,
        evidence_package=package,
        canonical_json=canonical_str,
    )
