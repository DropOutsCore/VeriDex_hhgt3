"""VERIDEX Backend Configuration Settings.

Centralized configuration for model paths, API keys, default thresholds, and system settings.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"

# YuNet Face Detection Configuration
YUNET_MODEL_FILENAME = os.getenv("YUNET_MODEL_FILENAME", "face_detection_yunet_2023mar.onnx")
YUNET_MODEL_PATH = os.getenv("YUNET_MODEL_PATH", str(MODELS_DIR / YUNET_MODEL_FILENAME))

DEFAULT_SCORE_THRESHOLD = float(os.getenv("YUNET_SCORE_THRESHOLD", "0.6"))
DEFAULT_NMS_THRESHOLD = float(os.getenv("YUNET_NMS_THRESHOLD", "0.3"))
DEFAULT_TOP_K = int(os.getenv("YUNET_TOP_K", "5000"))

# SFace Face Signature / Embedding Configuration
SFACE_MODEL_FILENAME = os.getenv("SFACE_MODEL_FILENAME", "face_recognition_sface_2021dec.onnx")
SFACE_MODEL_PATH = os.getenv("SFACE_MODEL_PATH", str(MODELS_DIR / SFACE_MODEL_FILENAME))

# Default Cosine Similarity Threshold for SFace (Standard OpenCV SFace threshold is ~0.3633)
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3633"))

# SerpApi & Google Lens Reverse Search Configuration
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
SERPAPI_BASE_URL = os.getenv("SERPAPI_BASE_URL", "https://serpapi.com/search.json")
SERPAPI_UPLOAD_URL = os.getenv("SERPAPI_UPLOAD_URL", "https://serpapi.com/upload")

# Evidence Scoring Configuration (Default weights sum to 1.0)
WEIGHT_REVERSE_SEARCH = float(os.getenv("WEIGHT_REVERSE_SEARCH", "0.40"))
WEIGHT_FACE_SIMILARITY = float(os.getenv("WEIGHT_FACE_SIMILARITY", "0.35"))
WEIGHT_IMAGE_SIMILARITY = float(os.getenv("WEIGHT_IMAGE_SIMILARITY", "0.10"))
WEIGHT_SOURCE_RELEVANCE = float(os.getenv("WEIGHT_SOURCE_RELEVANCE", "0.10"))
WEIGHT_METADATA_CONSISTENCY = float(os.getenv("WEIGHT_METADATA_CONSISTENCY", "0.05"))

