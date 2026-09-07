"""Image Fingerprinting Utilities: Cryptographic SHA-256 & Perceptual Hash (pHash).

==================================================
EDUCATIONAL BREAKDOWN: SHA-256 vs. pHash
==================================================

1. SHA-256 (EXACT INTEGRITY):
   - Answers: "Has the exact binary file changed?"
   - Nature: Cryptographic avalanche effect. Changing even 1 bit in the image file
     completely alters the resulting 256-bit hash digest.
   - Purpose in VERIDEX: Cryptographic evidence tampering verification & blockchain anchoring.
     Guarantees evidence integrity against byte-level modification.

2. PERCEPTUAL HASH / pHash (VISUAL SIMILARITY):
   - Answers: "Does this image remain perceptually similar to human eyes?"
   - Nature: Frequency domain analysis using Discrete Cosine Transform (DCT).
     Extracts low-frequency visual structures, ignoring high-frequency compression noise,
     resolution scaling, and minor color balance shifts.
   - Purpose in VERIDEX: Candidate discovery & duplicate image detection.
     Identifies when a candidate web/social image is a re-uploaded, resized, or compressed
     version of the target evidence image.

3. HAMMING DISTANCE & PERCEPTUAL MATCHING:
   - Hamming Distance represents the number of differing bits between two 64-bit pHash codes.
   - Distance = 0: Identical or imperceptibly altered visual appearance.
   - Distance <= 10: High perceptual similarity (likely re-compressed, resized, or slightly edited variant).
   - Distance > 20: Visually distinct images.
"""

import hashlib
import os
from io import BytesIO
from typing import Union, Dict, Any
import cv2
import numpy as np
import imagehash
from PIL import Image


def sha256_bytes(data: bytes) -> str:
    """Calculate cryptographic SHA-256 hex digest of raw binary bytes.

    Args:
        data: Binary payload bytes.

    Returns:
        64-character lowercase SHA-256 hex string.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"Expected bytes or bytearray, got {type(data).__name__}")
    return hashlib.sha256(data).hexdigest()


def sha256_file(file_path: str, chunk_size: int = 65536) -> str:
    """Calculate cryptographic SHA-256 hex digest of a disk file in memory-efficient chunks.

    Args:
        file_path: Absolute or relative file path.
        chunk_size: Read buffer size in bytes (default: 64KB).

    Returns:
        64-character lowercase SHA-256 hex string.

    Raises:
        FileNotFoundError: If target file path does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target file for SHA-256 hash not found: '{file_path}'")

    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def _to_pil_image(image_input: Union[bytes, bytearray, str, np.ndarray, Image.Image]) -> Image.Image:
    """Helper utility to convert various image input formats into a PIL Image instance."""
    if isinstance(image_input, Image.Image):
        return image_input

    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise FileNotFoundError(f"Image file not found: '{image_input}'")
        return Image.open(image_input)

    if isinstance(image_input, (bytes, bytearray)):
        if not image_input or len(image_input) == 0:
            raise ValueError("Cannot convert empty bytes payload to PIL Image.")
        return Image.open(BytesIO(image_input))

    if isinstance(image_input, np.ndarray):
        if image_input.size == 0:
            raise ValueError("Cannot convert empty NumPy array to PIL Image.")
        # Handle BGR (OpenCV) to RGB conversion
        if len(image_input.shape) == 3 and image_input.shape[2] == 3:
            rgb_arr = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb_arr)
        elif len(image_input.shape) == 2:
            return Image.fromarray(image_input)
        return Image.fromarray(image_input)

    raise TypeError(f"Unsupported image input type for pHash conversion: {type(image_input).__name__}")


def image_phash(
    image_input: Union[bytes, bytearray, str, np.ndarray, Image.Image],
    hash_size: int = 8,
) -> str:
    """Compute Discrete Cosine Transform (DCT) based Perceptual Hash (pHash).

    Args:
        image_input: Image bytes, file path, OpenCV BGR matrix, or PIL Image.
        hash_size: Size of the hash grid (default: 8 produces 8x8 = 64 bit / 16-hex hash).

    Returns:
        Hexadecimal string representation of the 64-bit perceptual hash.
    """
    pil_img = _to_pil_image(image_input)
    phash_obj = imagehash.phash(pil_img, hash_size=hash_size)
    return str(phash_obj)


def compare_phash(
    hash1: str,
    hash2: str,
    threshold: int = 10,
) -> Dict[str, Any]:
    """Compare two perceptual hash hex strings using Hamming Distance.

    Args:
        hash1: First pHash hex string.
        hash2: Second pHash hex string.
        threshold: Maximum Hamming distance for perceptual similarity match (default: 10).

    Returns:
        Dictionary detailing Hamming distance, max bit length, normalized similarity score, and match status.
    """
    if not hash1 or not hash2:
        raise ValueError("Both hash1 and hash2 must be non-empty strings for comparison.")

    try:
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
    except Exception as e:
        raise ValueError(f"Failed to parse pHash hex strings ('{hash1}', '{hash2}'): {str(e)}") from e

    hamming_dist = int(h1 - h2)
    total_bits = int(len(h1.hash.flatten()))

    # Normalized perceptual similarity score (1.0 = identical pHash, 0.0 = opposite pHash)
    similarity = max(0.0, min(1.0, 1.0 - (hamming_dist / float(total_bits))))

    return {
        "hamming_distance": hamming_dist,
        "max_bits": total_bits,
        "perceptual_similarity": round(similarity, 4),
        "perceptually_similar": bool(hamming_dist <= threshold),
        "threshold_used": threshold,
    }


def compare_image_hashes(
    image1_input: Union[bytes, str, np.ndarray],
    image2_input: Union[bytes, str, np.ndarray],
    phash_threshold: int = 10,
) -> Dict[str, Any]:
    """Higher-level comparative helper that evaluates both SHA-256 byte integrity and pHash visual similarity.

    Args:
        image1_input: Primary image (bytes, path, or NumPy array).
        image2_input: Secondary image for comparison.
        phash_threshold: Hamming distance threshold for perceptual match.

    Returns:
        Dictionary containing SHA-256 exact match decision and pHash perceptual match decision.
    """
    # 1. Compute SHA-256 for byte integrity comparison
    if isinstance(image1_input, bytes):
        sha1 = sha256_bytes(image1_input)
    elif isinstance(image1_input, str) and os.path.exists(image1_input):
        sha1 = sha256_file(image1_input)
    elif isinstance(image1_input, np.ndarray):
        sha1 = sha256_bytes(image1_input.tobytes())
    else:
        sha1 = "UNABLE_TO_HASH_TYPE"

    if isinstance(image2_input, bytes):
        sha2 = sha256_bytes(image2_input)
    elif isinstance(image2_input, str) and os.path.exists(image2_input):
        sha2 = sha256_file(image2_input)
    elif isinstance(image2_input, np.ndarray):
        sha2 = sha256_bytes(image2_input.tobytes())
    else:
        sha2 = "UNABLE_TO_HASH_TYPE"

    sha256_exact_match = bool(sha1 == sha2 and sha1 != "UNABLE_TO_HASH_TYPE")

    # 2. Compute pHash for visual similarity comparison
    phash1 = image_phash(image1_input)
    phash2 = image_phash(image2_input)

    phash_comp = compare_phash(phash1, phash2, threshold=phash_threshold)

    return {
        "sha256_exact_match": sha256_exact_match,
        "sha256_image1": sha1,
        "sha256_image2": sha2,
        "phash_image1": phash1,
        "phash_image2": phash2,
        "phash_hamming_distance": phash_comp["hamming_distance"],
        "phash_similarity": phash_comp["perceptual_similarity"],
        "phash_perceptually_similar": phash_comp["perceptually_similar"],
    }
