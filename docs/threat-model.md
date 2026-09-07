# VERIDEX Threat Model & Risk Assessment

---

## 1. System Architecture & Trust Boundaries

The VERIDEX system processes visual evidence across four key trust boundaries:

```
[ Client User / Dashboard ]  <-- Unverified User Input (Public Trust Boundary)
            │ (HTTP Multipart Uploads)
            ▼
[ VERIDEX FastAPI Backend ]  <-- Application Trust Boundary (YuNet / SFace / Evidence Scoring)
      │            │
      │ (HTTPS)    │ (Web3 Signed Raw Tx)
      ▼            ▼
[ SerpApi / Lens ] [ Polygon Amoy Testnet ] <-- External Decentralized Boundary
```

---

## 2. Threat Analysis (STRIDE Matrix)

### S - SPOOFING IDENTITY / EVIDENCE

- **Threat**: An adversary uploads synthetic, deepfake, or altered facial images trying to mimic a target person.
- **Impact**: Incorrect correspondence score calculation.
- **Mitigation**:
  - Dual-signal verification combining SFace 128-D cosine similarity and DCT pHash scene similarity.
  - Transparent evidence scoring breakdown highlighting individual signal strengths.
  - Strict disclaimers confirming evidence score is not legal identity proof.

---

### T - TAMPERING WITH EVIDENCE

- **Threat**: An adversary alters a single attribute of an evidence package (e.g. modifying `matched_url` or `face_similarity`) post-verification.
- **Impact**: False evidence presentation.
- **Mitigation**:
  - Canonical JSON sorting and SHA-256 Evidence DNA hash generation.
  - Proof anchoring on the immutable `VeridexRegistry.sol` smart contract.
  - Zero-trust `verify_evidence_integrity()` function reading actual on-chain state directly.

---

### R - REPUDIATION

- **Threat**: A party claims a verification proof was never generated or anchored.
- **Impact**: Loss of evidence auditability.
- **Mitigation**:
  - Signed Web3 raw transactions containing block timestamps, block numbers, transaction hashes, and submitter wallet addresses emitted in `ProofAnchored` events.

---

### I - INFORMATION DISCLOSURE

- **Threat**: An attacker queries the public Polygon Amoy blockchain to harvest raw biometric face vectors or personal identifying details.
- **Impact**: Severe privacy violation.
- **Mitigation**:
  - Strict Non-PII On-Chain Policy: Only 256-bit SHA-256 byte digests (`bytes32`) and block timestamps are stored on-chain.
  - Raw binary images and 128-D face embeddings are discarded after in-memory processing.

---

### D - DENIAL OF SERVICE (DoS)

- **Threat**: An attacker uploads 1GB files or zip bombs to crash the backend server.
- **Impact**: Application unavailability.
- **Mitigation**:
  - File upload cap at 10.0 MB (`MAX_ALLOWED_IMAGE_SIZE_BYTES`).
  - Magic byte header checks (`validate_image_payload`).
  - OpenCV decoding error boundaries.

---

### E - ELEVATION OF PRIVILEGE / SSRF

- **Threat**: An attacker provides a candidate image URL pointing to `http://169.254.169.254/latest/meta-data/` or `http://127.0.0.1:8000/internal` to extract internal credentials.
- **Impact**: Internal network compromise or credential theft.
- **Mitigation**:
  - `is_ssrf_safe_url()` checks URL scheme and resolves hostname IPs against loopback, private Class A/B/C, and link-local networks before executing HTTP requests.
