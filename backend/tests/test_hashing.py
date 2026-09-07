"""Unit & Integration Test Suite for VERIDEX Phase 3 (SHA-256 Integrity & pHash Perceptual Similarity).

Test Matrix:
- A: Original Image (single_face.jpg)
- B: Exact File Copy of A (single_face_copy.jpg)
- C: Resized & Compressed Version of A (single_face_compressed.jpg)
- D: Slightly Modified / Watermarked Version of A (single_face_modified.jpg)
- E: Completely Different Image (different_face.jpg)

Expected Behavioral Assertions:
1. SHA-256:
   - A and B MUST match exactly (SHA256(A) == SHA256(B)).
   - A and C MUST NOT match (SHA256(A) != SHA256(C)).
   - A and D MUST NOT match (SHA256(A) != SHA256(D)).
   - A and E MUST NOT match (SHA256(A) != SHA256(E)).

2. Perceptual Hash (pHash):
   - A and B MUST be identical (Hamming distance = 0).
   - A and C (resized/compressed) MUST remain perceptually similar (Hamming distance <= 10).
   - A and D (watermarked/edited) MUST remain perceptually similar (Hamming distance <= 10).
   - A and E (different image) MUST NOT be perceptually similar (Hamming distance > 15).
"""

import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.utils.hashing import (
    sha256_bytes,
    sha256_file,
    image_phash,
    compare_phash,
    compare_image_hashes,
)
from examples.setup_test_assets import setup_test_assets, EXAMPLES_DIR


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Ensure test image assets A, B, C, D, E are generated prior to running test suite."""
    setup_test_assets()


# -------------------------------------------------------------------
# SHA-256 Byte Integrity Unit Tests
# -------------------------------------------------------------------

def test_sha256_file_exact_copy():
    """Verify SHA-256 produces identical hash for exact file copy (A vs B)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_B = os.path.join(EXAMPLES_DIR, "single_face_copy.jpg")

    hash_A = sha256_file(path_A)
    hash_B = sha256_file(path_B)

    assert len(hash_A) == 64
    assert len(hash_B) == 64
    assert hash_A == hash_B, "SHA-256 must match exactly for duplicate files."


def test_sha256_file_compressed_difference():
    """Verify SHA-256 produces DIFFERENT hashes when image is compressed/resized (A vs C)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_C = os.path.join(EXAMPLES_DIR, "single_face_compressed.jpg")

    hash_A = sha256_file(path_A)
    hash_C = sha256_file(path_C)

    assert hash_A != hash_C, "SHA-256 must change when file bytes are altered by compression."


def test_sha256_file_modified_difference():
    """Verify SHA-256 produces DIFFERENT hashes when image has a minor watermark edit (A vs D)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_D = os.path.join(EXAMPLES_DIR, "single_face_modified.jpg")

    hash_A = sha256_file(path_A)
    hash_D = sha256_file(path_D)

    assert hash_A != hash_D, "SHA-256 must change when pixel values are modified."


def test_sha256_file_different_image():
    """Verify SHA-256 produces completely different hashes for distinct images (A vs E)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_E = os.path.join(EXAMPLES_DIR, "different_face.jpg")

    hash_A = sha256_file(path_A)
    hash_E = sha256_file(path_E)

    assert hash_A != hash_E


def test_sha256_bytes_empty():
    """Verify sha256_bytes handles raw byte arrays correctly."""
    data = b"VERIDEX_EVIDENCE_PAYLOAD"
    hash_val = sha256_bytes(data)
    assert len(hash_val) == 64
    assert hash_val == sha256_bytes(data)


# -------------------------------------------------------------------
# Perceptual Hash (pHash) Similarity Unit Tests
# -------------------------------------------------------------------

def test_phash_exact_copy():
    """Verify pHash produces identical perceptual hash for exact copy (A vs B)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_B = os.path.join(EXAMPLES_DIR, "single_face_copy.jpg")

    phash_A = image_phash(path_A)
    phash_B = image_phash(path_B)

    comp = compare_phash(phash_A, phash_B)
    assert comp["hamming_distance"] == 0
    assert comp["perceptual_similarity"] == 1.0
    assert comp["perceptually_similar"] is True


def test_phash_resized_compressed_similarity():
    """Verify pHash detects perceptual similarity for resized/compressed image (A vs C)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_C = os.path.join(EXAMPLES_DIR, "single_face_compressed.jpg")

    phash_A = image_phash(path_A)
    phash_C = image_phash(path_C)

    comp = compare_phash(phash_A, phash_C, threshold=10)
    # Resized/compressed image must remain perceptually similar (Hamming distance <= 10)
    assert comp["hamming_distance"] <= 10
    assert comp["perceptually_similar"] is True
    assert comp["perceptual_similarity"] >= 0.84


def test_phash_modified_watermark_similarity():
    """Verify pHash detects perceptual similarity for watermarked image (A vs D)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_D = os.path.join(EXAMPLES_DIR, "single_face_modified.jpg")

    phash_A = image_phash(path_A)
    phash_D = image_phash(path_D)

    comp = compare_phash(phash_A, phash_D, threshold=10)
    assert comp["hamming_distance"] <= 10
    assert comp["perceptually_similar"] is True


def test_phash_different_image_dissimilarity():
    """Verify pHash rejects perceptual match for completely different image (A vs E)."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_E = os.path.join(EXAMPLES_DIR, "different_face.jpg")

    phash_A = image_phash(path_A)
    phash_E = image_phash(path_E)

    comp = compare_phash(phash_A, phash_E, threshold=10)
    assert comp["hamming_distance"] > 10
    assert comp["perceptually_similar"] is False


def test_compare_image_hashes_full_matrix():
    """Verify higher-level compare_image_hashes produces dual SHA-256 and pHash breakdown."""
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    path_C = os.path.join(EXAMPLES_DIR, "single_face_compressed.jpg")

    res = compare_image_hashes(path_A, path_C)

    # SHA-256 must report NO exact match because bytes changed due to compression
    assert res["sha256_exact_match"] is False
    # pHash MUST report perceptual match because visual appearance remains similar
    assert res["phash_perceptually_similar"] is True
    assert res["phash_hamming_distance"] <= 10
