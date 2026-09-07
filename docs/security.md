# VERIDEX Security Architecture & Safeguards Guide

---

## 1. Executive Summary & Security Model

The VERIDEX security architecture safeguards the backend verification pipeline, Web3 blockchain integration, and REST API endpoints against common web vulnerabilities, arbitrary code execution, denial of service, and cryptographic key leakage.

---

## 2. Credentials & Secrets Isolation

1. **Zero Committed Secrets**:
   - `PRIVATE_KEY`, `SERPAPI_API_KEY`, and RPC provider URLs are loaded strictly from environment variables (`.env`).
   - `.env` and `*.key` files are excluded from version control via `.gitignore`.
   - Sample credentials in repository templates (`.env.example`) contain non-functional placeholders.

2. **Web3 Private Key Safety**:
   - Raw private keys are processed strictly in memory during EIP-155 transaction signing (`web3.eth.account.sign_transaction`).
   - Private keys are never logged, serialized, or returned in API responses.

---

## 3. Server-Side Request Forgery (SSRF) Protection

When candidate images are downloaded from discovered external web URLs, VERIDEX enforces strict SSRF protections in `app.utils.security_utils.is_ssrf_safe_url()`:

- **Scheme Validation**: Strictly restricts protocols to `http://` and `https://`. Prohibits `file://`, `gopher://`, `ftp://`, or custom schemes.
- **Loopback & Private Network Filtering**:
  - Rejects `127.0.0.1`, `localhost`, `0.0.0.0`, `::1`.
  - Resolves domain hostnames via DNS and blocks private IP networks:
    - `10.0.0.0/8` (Private Class A)
    - `172.16.0.0/12` (Private Class B)
    - `192.168.0.0/16` (Private Class C)
    - `169.254.0.0/16` (Link-Local / AWS IMDS Metadata `169.254.169.254`)
- **Download Timeout & Size Controls**:
  - Network HTTP requests enforce a strict timeout (default: 5.0 seconds).
  - Redirects are limited to prevent infinite redirect loops.

---

## 4. File Upload & Malicious Payload Sanitization

1. **Payload Size Limits**:
   - Uploaded multipart image files are capped at a maximum of **10.0 MB** (`MAX_ALLOWED_IMAGE_SIZE_BYTES`) to prevent Memory Exhaustion Denial of Service (DoS).

2. **Magic Bytes File Type Verification**:
   - Inspects initial byte signatures rather than relying solely on file extensions:
     - JPEG: `\xFF\xD8\xFF`
     - PNG: `\x89PNG\r\n\x1a\n`
     - WEBP: `RIFF....WEBP`
   - Rejects executable files, scripts, or corrupted byte streams.

3. **OpenCV Memory Safety**:
   - `cv2.imdecode` safely isolates image parsing. Invalid or corrupted image payloads return empty matrices (`None`) and trigger non-fatal validation errors.

---

## 5. API Exception Isolation & Information Leakage

- Global exception handlers (`@app.exception_handler`) catch all unhandled server exceptions.
- Internal stack traces, database details, or system file paths are **NEVER** returned to client callers.
- Standardized structured JSON responses with appropriate HTTP status codes (400, 404, 409, 402, 503, 500) are returned cleanly.

---

## 6. Smart Contract Anchoring Security

- **Duplicate Proof Protection**: `VeridexRegistry.sol` enforces `hasProof(proofId)` checks prior to mining to prevent evidence tampering or overwrite collisions.
- **Immutability**: Proof records once written to Polygon Amoy cannot be modified or deleted by any wallet address.
