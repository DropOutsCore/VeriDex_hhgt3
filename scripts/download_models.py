"""Utility script to download pre-trained models for VERIDEX.

Do NOT download models silently at runtime. This script allows explicit pre-fetching of model assets.
"""

import os
import sys
import urllib.request

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))

MODELS = {
    "face_detection_yunet_2023mar.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}


def download_models():
    os.makedirs(MODELS_DIR, exist_ok=True)
    for filename, url in MODELS.items():
        dest_path = os.path.join(MODELS_DIR, filename)
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            print(f"[+] Model already exists: {dest_path} ({os.path.getsize(dest_path)} bytes)")
            continue

        print(f"[*] Downloading {filename} from {url}...")
        try:
            urllib.request.urlretrieve(url, dest_path)
            print(f"[+] Successfully downloaded {filename} ({os.path.getsize(dest_path)} bytes)")
        except Exception as e:
            print(f"[-] Failed to download {filename}: {e}", file=sys.stderr)


if __name__ == "__main__":
    download_models()
