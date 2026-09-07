# VERIDEX Privacy Policy & Data Handling Specification

---

## 1. Executive Summary & Privacy Principles

VERIDEX (Visual Evidence Verification Engine) is designed under strict **Privacy-by-Design** principles. It establishes tamper-evident cryptographic provenance for visual evidence without exposing or persisting Personally Identifiable Information (PII) or raw biometric data.

---

## 2. On-Chain Privacy Constraints

### MANDATORY ON-CHAIN PROHIBITIONS

To guarantee strict privacy and prevent permanent exposure on public blockchain networks, the following data items **MUST NEVER** be submitted, emitted in smart contract events, or stored on-chain:

| Prohibited Item | Rationale & Protection |
|---|---|
| **Raw Binary Face Images** | High-density personal biometric data. Exposing raw images publicly violates global privacy regulations (GDPR, CCPA). |
| **Raw 128-D Face Embedding Vectors** | High-dimensional floating-point feature vectors (SFace) could potentially be reconstructed or weaponized for tracking. |
| **Person's Full Name / Identity** | Personal names must never be attached to public cryptographic proofs unless explicitly authorized by consent. |
| **Email Addresses & Phone Numbers** | Contact PII is strictly excluded from all evidence schema packages. |
| **Private Metadata & Location Coordinates** | Exact GPS coordinates or personal EXIF headers are stripped before evidence packaging. |

### PERMISSIBLE ON-CHAIN ANCHORING PAYLOADS

The deployed `VeridexRegistry.sol` smart contract accepts **ONLY** non-reversible 256-bit cryptographic SHA-256 hashes:

- `proofId` (`bytes32`): Sha256 hash digest of record identifier
- `evidenceHash` (`bytes32`): Sha256 hash over canonical JSON Evidence Package (Evidence DNA)
- `inputImageHash` (`bytes32`): Sha256 byte digest of primary input image file
- `matchedImageHash` (`bytes32`): Sha256 byte digest of discovered candidate image
- `timestamp` (`uint256`): Block timestamp when mined on Polygon Amoy testnet
- `submitter` (`address`): Ethereum wallet address of the submitting node

---

## 3. Temporary & Ephemeral Data Management

Where practical, all intermediate visual assets and floating-point vector representations are maintained strictly **in-memory** during request execution and cleaned immediately upon request completion:

1. **Uploaded Primary Evidence Images**:
   - Processed entirely in memory buffers (`io.BytesIO`, `numpy.ndarray`).
   - Binary buffers are garbage collected after face detection and signature extraction.

2. **Downloaded Candidate Images**:
   - Decoded directly into memory arrays.
   - Never written to persistent server disk storage.

3. **Raw 128-Dimensional SFace Embedding Vectors**:
   - Converted into SHA-256 fingerprint hashes (`embedding_hash`) immediately after landmark alignment.
   - Raw floating-point arrays are discarded upon completing cosine similarity matrix evaluation.

---

## 4. Responsible Use & Non-Legal Identity Disclaimer

> [!IMPORTANT]
> **FACE SIMILARITY IS NOT PROOF OF LEGAL IDENTITY**
> 
> OpenCV YuNet and SFace metrics quantify mathematical feature correspondence between visual samples. An Evidence Correspondence score (e.g. 91.0%) measures multi-factor similarity correlation; it does **NOT** represent a probability of legal identity or legal identity confirmation.

### CONSENT & TEST DATASET GUIDELINES

- All live demonstrations, integration tests, and benchmark evaluations **MUST** use consenting subjects, synthetic facial renders, or appropriately licensed public domain/creative commons test images (e.g. LFW test datasets).
- Unauthorized biometric scanning or surveillance of non-consenting individuals is strictly prohibited.
