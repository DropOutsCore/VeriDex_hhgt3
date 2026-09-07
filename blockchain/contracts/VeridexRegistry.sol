// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title VeridexRegistry
 * @author VERIDEX - Visual Evidence Verification Engine
 * @notice Immutable, tamper-evident registry for anchoring cryptographic evidence fingerprints on Polygon Amoy Testnet.
 *
 * ==================================================
 * ARCHITECTURAL PRINCIPLES & SECURITY GUARANTEES
 * ==================================================
 * 1. OFF-CHAIN AI ANALYSIS, ON-CHAIN ANCHORING:
 *    - The smart contract DOES NOT perform facial recognition or visual analysis.
 *    - OpenCV YuNet face detection and SFace embedding analysis run off-chain in the VERIDEX backend.
 *    - This contract acts strictly as an immutable, timestamped public ledger for evidence fingerprints.
 *
 * 2. STRICT PRIVACY & ZERO PII:
 *    - NO raw binary images are stored on-chain.
 *    - NO 128-dimensional face embedding vectors are stored on-chain.
 *    - NO names, emails, or personal identifiable information (PII) are stored on-chain.
 *    - Only 256-bit cryptographic SHA-256 hashes (bytes32) and block timestamps are anchored.
 *
 * 3. IMMUTABILITY & DUPLICATE PREVENTION:
 *    - Once anchored, a proof record cannot be altered, updated, or overwritten.
 *    - Duplicate proof IDs are rejected with custom error `ProofAlreadyAnchored`.
 */
contract VeridexRegistry {

    struct ProofRecord {
        bytes32 proofId;           // Deterministic unique record identifier hash
        bytes32 evidenceHash;      // Canonical evidence package SHA-256 fingerprint (EVIDENCE DNA)
        bytes32 inputImageHash;    // SHA-256 hash digest of primary evidence input image
        bytes32 matchedImageHash;  // SHA-256 hash digest of candidate image asset
        uint256 timestamp;         // Block timestamp when proof was anchored on-chain
        address submitter;         // Wallet address that submitted and anchored the proof
    }

    // Mapping from proofId to anchored ProofRecord
    mapping(bytes32 => ProofRecord) private _proofs;

    // Total count of anchored evidence proof records
    uint256 private _totalProofs;

    // Custom errors
    error ProofAlreadyAnchored(bytes32 proofId);
    error InvalidZeroHash(string paramName);
    error ProofNotFound(bytes32 proofId);

    // Events
    event ProofAnchored(
        bytes32 indexed proofId,
        bytes32 indexed evidenceHash,
        address indexed submitter,
        uint256 timestamp
    );

    /**
     * @notice Anchor a cryptographic evidence fingerprint onto the Polygon Amoy blockchain.
     * @param proofId Deterministic unique proof identifier (bytes32).
     * @param evidenceHash Canonical Evidence DNA SHA-256 hash (bytes32).
     * @param inputImageHash SHA-256 hash of the primary evidence image (bytes32).
     * @param matchedImageHash SHA-256 hash of the candidate image (bytes32).
     */
    function anchorProof(
        bytes32 proofId,
        bytes32 evidenceHash,
        bytes32 inputImageHash,
        bytes32 matchedImageHash
    ) external {
        if (proofId == bytes32(0)) revert InvalidZeroHash("proofId");
        if (evidenceHash == bytes32(0)) revert InvalidZeroHash("evidenceHash");
        if (inputImageHash == bytes32(0)) revert InvalidZeroHash("inputImageHash");
        if (matchedImageHash == bytes32(0)) revert InvalidZeroHash("matchedImageHash");
        if (_proofs[proofId].timestamp != 0) revert ProofAlreadyAnchored(proofId);

        ProofRecord memory newRecord = ProofRecord({
            proofId: proofId,
            evidenceHash: evidenceHash,
            inputImageHash: inputImageHash,
            matchedImageHash: matchedImageHash,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        _proofs[proofId] = newRecord;
        _totalProofs += 1;

        emit ProofAnchored(proofId, evidenceHash, msg.sender, block.timestamp);
    }

    /**
     * @notice Retrieve an anchored evidence proof record by its proofId.
     * @param proofId Unique proof identifier.
     * @return record The complete ProofRecord struct.
     */
    function getProof(bytes32 proofId) external view returns (ProofRecord memory record) {
        if (_proofs[proofId].timestamp == 0) revert ProofNotFound(proofId);
        return _proofs[proofId];
    }

    /**
     * @notice Check whether a proofId has already been anchored in the registry.
     * @param proofId Unique proof identifier.
     * @return exists True if proofId exists on-chain, false otherwise.
     */
    function hasProof(bytes32 proofId) external view returns (bool exists) {
        return _proofs[proofId].timestamp != 0;
    }

    /**
     * @notice Get total count of anchored evidence proofs in registry.
     * @return count Total number of anchored proofs.
     */
    function getProofCount() external view returns (uint256 count) {
        return _totalProofs;
    }
}
