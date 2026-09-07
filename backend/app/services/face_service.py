"""Face Detection & Face Signature (Embedding) Service powered by OpenCV YuNet and SFace.

==================================================
EDUCATIONAL OVERVIEW & DESIGN PRINCIPLES
==================================================

1. WHAT YUNET & SFACE DO:
   - YuNet (Face Detection): Locates human faces in an image and identifies 5 key facial landmarks.
   - SFace (Face Signature / Feature Extraction): Takes an aligned facial crop (112x112) and projects
     facial traits into a 128-dimensional normalized floating-point feature space (the Face Signature).

2. FACE SIGNATURE & EMBEDDINGS:
   - A Face Signature is a 128-dimensional numerical representation of facial structure, geometry, and texture.
   - IT IS NOT A LEGAL BIOMETRIC IDENTITY PROOF.
   - Purpose: Enables mathematical comparison of facial correspondence between an input evidence image
     and visual samples discovered online.

3. FACIAL ALIGNMENT (alignCrop):
   - Unaligned face crops introduce rotation, tilt, and scale variance that degrade embedding quality.
   - Facial alignment applies an affine transformation mapping the 5 key landmarks (eyes, nose, mouth corners)
     to a canonical 112x112 pixel coordinate template before feature extraction.

4. COSINE SIMILARITY & MATCHING METRICS:
   - Cosine Similarity measures the directional alignment between two 128-D normalized embedding vectors:
     similarity(A, B) = (A · B) / (||A|| * ||B||)
   - Range: -1.0 to 1.0 (for normalized vectors, identical signatures yield ~1.0).
   - Terminology: Results are expressed as "matching score", "face similarity", or "face correspondence",
     NEVER as "absolute identity proof".

5. LIMITATIONS:
   - Sensitive to extreme lighting shifts, severe face occlusion (>50%), heavy profile angles (>70°), and age progression.
   - High similarity scores indicate visual face correspondence, not legal identity verification.
"""

import os
import hashlib
from typing import List, Union, Optional, Tuple
import cv2
import numpy as np

from app.config import (
    YUNET_MODEL_PATH,
    SFACE_MODEL_PATH,
    DEFAULT_SCORE_THRESHOLD,
    DEFAULT_NMS_THRESHOLD,
    DEFAULT_TOP_K,
    DEFAULT_SIMILARITY_THRESHOLD,
)
from app.models.face_schemas import (
    FaceDetectionResult,
    FaceDetection,
    FacialLandmarks,
    FaceSignature,
    FaceSimilarityResult,
)


def load_yunet_detector(
    image_width: int,
    image_height: int,
    model_path: str = YUNET_MODEL_PATH,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    nms_threshold: float = DEFAULT_NMS_THRESHOLD,
    top_k: int = DEFAULT_TOP_K,
) -> cv2.FaceDetectorYN:
    """Instantiate and configure OpenCV YuNet face detector."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"YuNet model ONNX file not found at path '{model_path}'. "
            f"Please run 'python scripts/download_models.py' or place the model file in the 'models/' directory."
        )

    try:
        detector = cv2.FaceDetectorYN.create(
            model=model_path,
            config="",
            input_size=(image_width, image_height),
            score_threshold=score_threshold,
            nms_threshold=nms_threshold,
            top_k=top_k,
        )
        return detector
    except Exception as e:
        raise RuntimeError(f"Failed to load OpenCV YuNet model: {str(e)}") from e


def load_sface_recognizer(model_path: str = SFACE_MODEL_PATH) -> cv2.FaceRecognizerSF:
    """Instantiate and configure OpenCV SFace face signature recognizer.

    Args:
        model_path: Absolute or relative path to SFace ONNX model file.

    Returns:
        Configured cv2.FaceRecognizerSF instance.

    Raises:
        FileNotFoundError: If SFace ONNX model file is missing.
        RuntimeError: If OpenCV fails to initialize SFace model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"SFace model ONNX file not found at path '{model_path}'. "
            f"Please run 'python scripts/download_models.py' or place model file in 'models/' directory."
        )

    try:
        recognizer = cv2.FaceRecognizerSF.create(model=model_path, config="")
        return recognizer
    except Exception as e:
        raise RuntimeError(f"Failed to load OpenCV SFace model: {str(e)}") from e


def _format_face_matrix(face_data: Union[np.ndarray, List[float], FaceDetection]) -> np.ndarray:
    """Convert face bounding box and landmarks into a 1x15 float32 NumPy array expected by SFace alignCrop."""
    if isinstance(face_data, np.ndarray):
        arr = face_data.astype(np.float32)
        if arr.ndim == 1:
            arr = np.expand_dims(arr, axis=0)
        return arr

    if isinstance(face_data, FaceDetection):
        bbox = face_data.bbox
        lm = face_data.landmarks
        if not lm:
            raise ValueError("FaceDetection object must contain facial landmarks for alignment.")
        row = [
            float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]),
            float(lm.right_eye[0]), float(lm.right_eye[1]),
            float(lm.left_eye[0]), float(lm.left_eye[1]),
            float(lm.nose_tip[0]), float(lm.nose_tip[1]),
            float(lm.right_mouth[0]), float(lm.right_mouth[1]),
            float(lm.left_mouth[0]), float(lm.left_mouth[1]),
            float(face_data.confidence),
        ]
        return np.array([row], dtype=np.float32)

    if isinstance(face_data, (list, tuple)) and len(face_data) == 15:
        return np.array([face_data], dtype=np.float32)

    raise ValueError(f"Invalid face data format: {type(face_data).__name__}")


def align_face(
    image: np.ndarray,
    face_data: Union[np.ndarray, List[float], FaceDetection],
    sface_recognizer: Optional[cv2.FaceRecognizerSF] = None,
) -> np.ndarray:
    """Align and crop face ROI using facial landmark affine transformation.

    Args:
        image: Source image numpy array (BGR).
        face_data: Face detection matrix or FaceDetection object with landmarks.
        sface_recognizer: Optional pre-loaded SFace instance.

    Returns:
        112x112 aligned BGR face crop array.
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot align face from empty or invalid image array.")

    face_mat = _format_face_matrix(face_data)
    recognizer = sface_recognizer or load_sface_recognizer()

    aligned_crop = recognizer.alignCrop(image, face_mat)
    if aligned_crop is None or aligned_crop.size == 0:
        raise RuntimeError("OpenCV FaceRecognizerSF alignCrop failed to produce an aligned face crop.")
    return aligned_crop


def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """Normalize embedding vector to L2 unit length.

    Args:
        embedding: 1D or 2D numpy array embedding vector.

    Returns:
        L2 normalized float32 embedding vector.
    """
    emb = embedding.astype(np.float32).flatten()
    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm
    return emb


def compute_embedding_hash(embedding: np.ndarray) -> str:
    """Compute cryptographic SHA-256 fingerprint hex of raw embedding vector bytes."""
    norm_emb = normalize_embedding(embedding)
    return hashlib.sha256(norm_emb.tobytes()).hexdigest()


def generate_face_embedding(
    image: np.ndarray,
    face_data: Union[np.ndarray, List[float], FaceDetection],
    sface_recognizer: Optional[cv2.FaceRecognizerSF] = None,
) -> Tuple[np.ndarray, str, FaceSignature]:
    """Generate 128-dimensional Face Signature embedding for a detected face.

    Pipeline:
    1. Align face using 5 key landmarks (alignCrop) -> 112x112 normalized ROI.
    2. Extract feature vector via SFace CNN -> 128-float raw embedding.
    3. L2 Unit Normalize embedding.
    4. Compute SHA-256 fingerprint hash.

    Args:
        image: Source BGR image numpy array.
        face_data: Detected face row matrix or FaceDetection object.
        sface_recognizer: Optional pre-loaded FaceRecognizerSF instance.

    Returns:
        Tuple containing:
        - normalized_embedding (np.ndarray of shape (128,))
        - embedding_hash (str SHA-256 fingerprint hex)
        - FaceSignature Pydantic schema
    """
    recognizer = sface_recognizer or load_sface_recognizer()
    aligned_crop = align_face(image, face_data, sface_recognizer=recognizer)

    raw_feature = recognizer.feature(aligned_crop)
    norm_feature = normalize_embedding(raw_feature)
    emb_hash = compute_embedding_hash(norm_feature)
    l2_norm = float(np.linalg.norm(norm_feature))

    signature_schema = FaceSignature(
        embedding_generated=True,
        embedding_dimension=int(norm_feature.shape[0]),
        embedding_hash=emb_hash,
        norm=round(l2_norm, 4),
    )

    return norm_feature, emb_hash, signature_schema


def calculate_face_similarity(
    embedding1: np.ndarray,
    embedding2: np.ndarray,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> FaceSimilarityResult:
    """Calculate Cosine Similarity score between two 128-dimensional Face Signature embeddings.

    Cosine Similarity Formula:
    similarity(A, B) = (A · B) / (||A|| * ||B||)

    Args:
        embedding1: First 128-D feature vector.
        embedding2: Second 128-D feature vector.
        threshold: Decision boundary similarity threshold (default: 0.3633).

    Returns:
        FaceSimilarityResult schema detailing matching score, match status, and qualitative assessment.
    """
    if embedding1 is None or embedding2 is None or len(embedding1) == 0 or len(embedding2) == 0:
        return FaceSimilarityResult(
            matching_score=0.0,
            correspondence_match=False,
            threshold_used=threshold,
            quality_assessment="Invalid or empty embedding vector provided.",
            error="Embedding vectors must be non-empty numpy arrays.",
        )

    emb1_norm = normalize_embedding(embedding1)
    emb2_norm = normalize_embedding(embedding2)

    hash1 = compute_embedding_hash(emb1_norm)
    hash2 = compute_embedding_hash(emb2_norm)

    dot_prod = float(np.dot(emb1_norm, emb2_norm))
    # Clamp cosine similarity to [-1.0, 1.0] to guard against floating-point precision error
    score = max(-1.0, min(1.0, dot_prod))
    score_rounded = round(score, 4)

    is_match = bool(score >= threshold)

    # Formulate qualitative correspondence assessment (avoiding absolute identity claims)
    if score >= 0.70:
        assessment = "High Face Correspondence (Strong visual similarity)"
    elif score >= threshold:
        assessment = "Moderate Face Correspondence (Above similarity threshold)"
    elif score >= 0.20:
        assessment = "Low Face Correspondence (Below match threshold)"
    else:
        assessment = "Disparate / Non-Matching Faces"

    return FaceSimilarityResult(
        matching_score=score_rounded,
        correspondence_match=is_match,
        threshold_used=threshold,
        face1_hash=hash1,
        face2_hash=hash2,
        quality_assessment=assessment,
    )


def extract_face(
    image: np.ndarray,
    bbox: List[int],
    margin: float = 0.0,
) -> np.ndarray:
    """Crop face Region of Interest (ROI) from an image matrix given a bounding box [x, y, w, h]."""
    if image is None or image.size == 0:
        raise ValueError("Cannot extract face from an empty or invalid image.")
    if len(bbox) != 4:
        raise ValueError("Bounding box must be a list of 4 integers: [x, y, width, height]")

    x, y, w, h = bbox
    img_h, img_w = image.shape[:2]

    if margin > 0.0:
        pad_w = int(w * margin)
        pad_h = int(h * margin)
        x = max(0, x - pad_w)
        y = max(0, y - pad_h)
        w = min(img_w - x, w + 2 * pad_w)
        h = min(img_h - y, h + 2 * pad_h)

    crop = image[y : y + h, x : x + w]
    if crop.size == 0:
        raise ValueError("Extracted face crop resulted in an empty image array.")
    return crop


def validate_face_detection(result: FaceDetectionResult) -> bool:
    """Validate whether a face detection result contains at least one valid detected face."""
    return bool(result.face_detected and result.face_count > 0 and len(result.faces) > 0)


def detect_faces(
    image_input: Union[bytes, bytearray, np.ndarray],
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    nms_threshold: float = DEFAULT_NMS_THRESHOLD,
    generate_signatures: bool = True,
) -> FaceDetectionResult:
    """Detect human faces and generate Face Signatures using OpenCV YuNet and SFace.

    Handles edge cases gracefully:
    - Empty / corrupt image data
    - Invalid image formats
    - No faces present
    - Single or multiple faces
    - Blurry / small faces

    Args:
        image_input: Binary image bytes or decoded OpenCV BGR numpy array.
        score_threshold: Confidence threshold for face detection.
        nms_threshold: Non-maximum suppression threshold.
        generate_signatures: If True, computes SFace embedding metadata for each detected face.

    Returns:
        FaceDetectionResult schema detailing detection status, faces, and signature fingerprints.
    """
    # 1. Decode / Validate Input Image
    image: Optional[np.ndarray] = None
    if isinstance(image_input, (bytes, bytearray)):
        if not image_input or len(image_input) == 0:
            return FaceDetectionResult(
                face_detected=False,
                face_count=0,
                faces=[],
                error="Received empty image bytes payload.",
            )
        try:
            nparr = np.frombuffer(image_input, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return FaceDetectionResult(
                face_detected=False,
                face_count=0,
                faces=[],
                error=f"Failed to decode image bytes: {str(e)}",
            )
    elif isinstance(image_input, np.ndarray):
        image = image_input
    else:
        return FaceDetectionResult(
            face_detected=False,
            face_count=0,
            faces=[],
            error=f"Unsupported image input type: {type(image_input).__name__}",
        )

    if image is None or image.size == 0 or len(image.shape) < 2:
        return FaceDetectionResult(
            face_detected=False,
            face_count=0,
            faces=[],
            error="Invalid or corrupted image format. Unable to read image matrix.",
        )

    height, width = image.shape[:2]

    # 2. Check Model File Availability
    if not os.path.exists(YUNET_MODEL_PATH):
        return FaceDetectionResult(
            face_detected=False,
            face_count=0,
            faces=[],
            image_width=width,
            image_height=height,
            error=f"YuNet model ONNX file not found at '{YUNET_MODEL_PATH}'. Run 'python scripts/download_models.py' to fetch model.",
        )

    # 3. Load YuNet Detector
    try:
        detector = load_yunet_detector(
            image_width=width,
            image_height=height,
            score_threshold=score_threshold,
            nms_threshold=nms_threshold,
        )
        status, detected_faces = detector.detect(image)
    except Exception as e:
        return FaceDetectionResult(
            face_detected=False,
            face_count=0,
            faces=[],
            image_width=width,
            image_height=height,
            error=f"Error executing YuNet face detection: {str(e)}",
        )

    # 4. Parse Detection Results & Generate Face Signatures
    if detected_faces is None or len(detected_faces) == 0:
        return FaceDetectionResult(
            face_detected=False,
            face_count=0,
            faces=[],
            image_width=width,
            image_height=height,
        )

    sface_recognizer: Optional[cv2.FaceRecognizerSF] = None
    if generate_signatures and os.path.exists(SFACE_MODEL_PATH):
        try:
            sface_recognizer = load_sface_recognizer()
        except Exception:
            sface_recognizer = None

    parsed_faces: List[FaceDetection] = []
    for face in detected_faces:
        box_x, box_y, box_w, box_h = face[0:4]
        right_eye = [float(face[4]), float(face[5])]
        left_eye = [float(face[6]), float(face[7])]
        nose_tip = [float(face[8]), float(face[9])]
        right_mouth = [float(face[10]), float(face[11])]
        left_mouth = [float(face[12]), float(face[13])]
        confidence = float(face[14])

        int_x = max(0, min(int(round(box_x)), width - 1))
        int_y = max(0, min(int(round(box_y)), height - 1))
        int_w = max(1, min(int(round(box_w)), width - int_x))
        int_h = max(1, min(int(round(box_h)), height - int_y))

        landmarks = FacialLandmarks(
            right_eye=right_eye,
            left_eye=left_eye,
            nose_tip=nose_tip,
            right_mouth=right_mouth,
            left_mouth=left_mouth,
        )

        signature_schema: Optional[FaceSignature] = None
        if sface_recognizer is not None:
            try:
                _, _, signature_schema = generate_face_embedding(
                    image, face, sface_recognizer=sface_recognizer
                )
            except Exception:
                signature_schema = None

        parsed_faces.append(
            FaceDetection(
                confidence=round(confidence, 4),
                bbox=[int_x, int_y, int_w, int_h],
                landmarks=landmarks,
                signature=signature_schema,
            )
        )

    parsed_faces.sort(key=lambda f: f.confidence, reverse=True)

    return FaceDetectionResult(
        face_detected=len(parsed_faces) > 0,
        face_count=len(parsed_faces),
        faces=parsed_faces,
        image_width=width,
        image_height=height,
    )
