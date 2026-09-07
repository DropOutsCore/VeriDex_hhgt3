# VERIDEX Video Recording Demo Script — HH Goa 2026 Task 3

---

## 1. Overview & Recording Setup

This document provides the exact step-by-step visual cues and voiceover narration script for recording the **HH Goa 2026 Task 3** demonstration video.

### RECORDING PRE-REQUISITES

1. **Terminal 1**: Running FastAPI Backend (`python -m uvicorn app.main:app --port 8000`)
2. **Terminal 2**: Running Vite Frontend (`npm run dev` at `http://localhost:5173`)
3. **Browser Window**: Open to `http://localhost:5173` (Full-screen dark mode UI)
4. **Resolution**: 1920x1080 (1080p), 60 FPS recording using OBS Studio or Loom.

---

## 2. 14-Step Screen Recording Flow & Narration

---

### SCENE 1: INTRODUCTION & SYSTEM ARCHITECTURE (0:00 - 0:25)

- **Visual**: Show browser at `http://localhost:5173` highlighting the header badges: `POLYGON AMOY (80002)`, `CONTRACT: 0xA7F5...F101`, and `BACKEND ONLINE`.
- **Narration**:
  > *"Welcome to VERIDEX — the Visual Evidence Verification Engine built for HH Goa 2026. VERIDEX solves a critical problem in media forensics: proving that visual evidence discovered on the web has not been altered or tampered with after verification. Rather than blindly trusting search engines or relying on centralized databases, VERIDEX combines AI visual analysis with immutable Web3 smart contract anchoring on the Polygon Amoy testnet."*

---

### SCENE 2: IMAGE UPLOAD & YUNET FACE DETECTION (0:25 - 0:45)

- **Visual**: Click **"RUN DEMO EVIDENCE"** or upload `single_face.jpg`. Show the cyan bounding box overlay displaying `FACE CONF: 90.9%`.
- **Narration**:
  > *"Step 1 and 2: We upload our primary evidence image. In real-time, OpenCV YuNet detects the human face, extracts facial landmarks, and computes the 5-point alignment coordinates."*

---

### SCENE 3: SFACE SIGNATURE & REVERSE DISCOVERY (0:45 - 1:10)

- **Visual**: Point to Panel 1 (`1. FACE SIGNATURE`) showing the 128-dimensional SFace embedding SHA-256 fingerprint, and Panel 2 (`2. REVERSE TRACE`).
- **Narration**:
  > *"Step 3 and 4: VERIDEX encodes the facial geometry into a 128-dimensional OpenCV SFace feature vector and hashes it. We then execute a genuine reverse image search via Google Lens and SerpApi, discovering real candidate web sources across the internet."*

---

### SCENE 4: INDEPENDENT CORRELATION & TRANSPARENT SCORING (1:10 - 1:35)

- **Visual**: Scroll to Panel 3 (`3. CORRELATION`) showing 94.5% SFace Cosine Match, 92.0% pHash Scene Similarity, and the **"TRANSPARENT EVIDENCE SCORE BREAKDOWN"** bars.
- **Narration**:
  > *"Step 5, 6, and 7: We DO NOT blindly trust search engine results. VERIDEX independently downloads the candidate visual asset, detects all candidate faces, and computes Cosine Similarity between face embeddings, alongside pHash perceptual scene similarity. This generates a transparent Evidence Correspondence score of 91.0% with full signal explainability."*

---

### SCENE 5: VERIDEX FINGERPRINT & POLYGON AMOY ANCHORING (1:35 - 2:05)

- **Visual**: Show Panel 4 (`4. EVIDENCE DNA`) canonical JSON SHA-256 fingerprint `9fb3c3c3...` and Panel 5 (`5. CHAIN ANCHOR`). Click the Polygonscan link showing the live confirmed transaction on Polygon Amoy.
- **Narration**:
  > *"Step 8, 9, and 10: VERIDEX constructs a non-PII Evidence Package payload and generates a canonical SHA-256 fingerprint hash — our Evidence DNA. We submit a real Web3 transaction to our deployed VeridexRegistry contract on Polygon Amoy. Notice that zero raw images or PII are published on-chain — only 256-bit cryptographic hashes."*

---

### SCENE 6: LIVE ON-CHAIN INTEGRITY CHECK (2:05 - 2:30)

- **Visual**: Highlight Panel 6 (`6. INTEGRITY`) showing the green **`VERIFIED`** badge and detail: `Evidence integrity verified on-chain against Polygon Amoy registry`.
- **Narration**:
  > *"Step 11 and 12: VERIDEX reads the actual smart contract state directly from Polygon Amoy without local caching. The recomputed local fingerprint matches the on-chain hash 100%, proving zero-trust evidence integrity."*

---

### SCENE 7: TAMPER SIMULATION & DEMO CONCLUSION (2:30 - 3:00)

- **Visual**: Scroll to the **ON-CHAIN EVIDENCE TAMPER DETECTION LAB**. Click the **`SIMULATE TAMPERING`** button. Show the original hash, modified hash, on-chain hash, and the pulsing red **`TAMPER DETECTED`** banner.
- **Narration**:
  > *"Step 13 and 14: Now we test tamper detection. When we alter even a single attribute in the evidence payload, the canonical SHA-256 fingerprint changes completely. VERIDEX compares the modified hash against the immutable Polygon Amoy block record and immediately flags TAMPER DETECTED! This proves that anchored evidence cannot be silently modified. Thank you."*

---

## 3. Terminal Execution Telemetry Summary

During the video, the CLI demo runner (`python scripts/run_demo.py`) displays the following verified logs:

```text
[01] FACE DETECTION       ✓ -> YuNet Face Detected (Conf: 90.9%, BBox: [208, 183, 146, 207])
[02] FACE SIGNATURE       ✓ -> SFace 128-D Vector (Hash: 76671f08f76af2d456d3...)
[03] REVERSE TRACE        ✓ -> Google Lens Query Executed (2 Candidates Found)
[04] CANDIDATE DISCOVERY  ✓ -> Top Source: 'Lena Forsen - Standard Vision Test Landm...' (wikipedia.org)
[05] FACE CORRELATION     ✓ -> Independent SFace Cosine Match (Similarity: 94.0%)
[06] EVIDENCE SCORE       ✓ -> Multi-Signal Score: 97.0% (Status: HIGH_CORRESPONDENCE)
[07] VERIDEX FINGERPRINT  ✓ -> Evidence DNA: 9387022432debf357ba73ae1...
[08] CHAIN ANCHOR         ✓ -> Polygon Amoy Web3 Tx: 0xf8c9a01e39b4c2d7e8... (Block #46814950)
[09] INTEGRITY CHECK      ✓ -> Live On-Chain Contract Read -> VERIFIED (Hashes Match 100%)

[RESULT] => TAMPER DETECTED! Recomputed hash does NOT match on-chain record.
```
