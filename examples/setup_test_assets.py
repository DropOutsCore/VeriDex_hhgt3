"""Utility script to download/generate test image assets for VERIDEX Phase 1, Phase 2, and Phase 3.

Creates:
- A: single_face.jpg (Original image)
- B: single_face_copy.jpg (Exact byte copy of A)
- C: single_face_compressed.jpg (Resized & compressed version of A)
- D: single_face_modified.jpg (Slightly modified/watermarked version of A)
- E: different_face.jpg (Completely different image)
- Additional test assets: same_person.jpg, multi_face.jpg, no_face.jpg, blurry_face.jpg, invalid_image.dat
"""

import os
import shutil
import urllib.request
import cv2
import numpy as np
from PIL import Image

EXAMPLES_DIR = os.path.abspath(os.path.dirname(__file__))

SINGLE_FACE_URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/lena.jpg"
DIFFERENT_FACE_URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/messi5.jpg"


def setup_test_assets():
    os.makedirs(EXAMPLES_DIR, exist_ok=True)

    # A: Original Image (single_face.jpg)
    path_A = os.path.join(EXAMPLES_DIR, "single_face.jpg")
    if not os.path.exists(path_A):
        print("[*] Downloading Image A (single_face.jpg)...")
        try:
            urllib.request.urlretrieve(SINGLE_FACE_URL, path_A)
            print("[+] Downloaded Image A.")
        except Exception as e:
            print(f"[-] Failed to download Image A: {e}")

    # E: Completely Different Image (different_face.jpg)
    path_E = os.path.join(EXAMPLES_DIR, "different_face.jpg")
    if not os.path.exists(path_E):
        print("[*] Downloading Image E (different_face.jpg)...")
        try:
            urllib.request.urlretrieve(DIFFERENT_FACE_URL, path_E)
            print("[+] Downloaded Image E.")
        except Exception as e:
            print(f"[-] Failed to download Image E: {e}")

    if os.path.exists(path_A):
        # B: Exact Copy of A (single_face_copy.jpg)
        path_B = os.path.join(EXAMPLES_DIR, "single_face_copy.jpg")
        if not os.path.exists(path_B):
            shutil.copyfile(path_A, path_B)
            print(f"[+] Created Image B (Exact Copy): '{path_B}'.")

        # C: Resized & Compressed Version of A (single_face_compressed.jpg)
        path_C = os.path.join(EXAMPLES_DIR, "single_face_compressed.jpg")
        if not os.path.exists(path_C):
            pil_img = Image.open(path_A)
            # Resize down to 256x256 and save with heavy JPEG compression (quality=30)
            pil_resized = pil_img.resize((256, 256))
            pil_resized.save(path_C, "JPEG", quality=30)
            print(f"[+] Created Image C (Resized & Compressed): '{path_C}'.")

        # D: Slightly Modified Version of A (single_face_modified.jpg)
        path_D = os.path.join(EXAMPLES_DIR, "single_face_modified.jpg")
        if not os.path.exists(path_D):
            img_cv = cv2.imread(path_A)
            if img_cv is not None:
                # Add a small white rectangle watermark in the top corner
                cv2.rectangle(img_cv, (10, 10), (60, 60), (255, 255, 255), -1)
                cv2.putText(img_cv, "V1", (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
                cv2.imwrite(path_D, img_cv)
                print(f"[+] Created Image D (Slightly Modified Watermark): '{path_D}'.")

        # Additional assets for Phase 1 & 2 tests
        same_person_path = os.path.join(EXAMPLES_DIR, "same_person.jpg")
        if not os.path.exists(same_person_path):
            img = cv2.imread(path_A)
            if img is not None:
                same_person = cv2.convertScaleAbs(img, alpha=1.05, beta=10)
                cv2.imwrite(same_person_path, same_person)

        multi_face_path = os.path.join(EXAMPLES_DIR, "multi_face.jpg")
        if not os.path.exists(multi_face_path):
            img = cv2.imread(path_A)
            if img is not None:
                multi_img = np.hstack((img, img))
                cv2.imwrite(multi_face_path, multi_img)

        blurry_face_path = os.path.join(EXAMPLES_DIR, "blurry_face.jpg")
        if not os.path.exists(blurry_face_path):
            img = cv2.imread(path_A)
            if img is not None:
                blurry = cv2.GaussianBlur(img, (35, 35), 0)
                cv2.imwrite(blurry_face_path, blurry)

    # No-face image
    no_face_path = os.path.join(EXAMPLES_DIR, "no_face.jpg")
    if not os.path.exists(no_face_path):
        grid = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.putText(grid, "VERIDEX TEST - NO FACE", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imwrite(no_face_path, grid)

    # Invalid non-image file
    invalid_path = os.path.join(EXAMPLES_DIR, "invalid_image.dat")
    if not os.path.exists(invalid_path):
        with open(invalid_path, "wb") as f:
            f.write(b"NOT_A_REAL_IMAGE_FILE_HEADER_BINARY_DATA_CORRUPT_1234567890")


if __name__ == "__main__":
    setup_test_assets()
