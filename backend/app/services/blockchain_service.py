"""Phase 11 Web3 Blockchain Integration Service.

==================================================
ARCHITECTURAL & PRIVACY DESIGN
==================================================

1. REAL ON-CHAIN EVIDENCE ANCHORING:
   - Connects off-chain VERIDEX Evidence Fingerprint payloads (Phase 8) to the deployed `VeridexRegistry.sol`
     smart contract on the Polygon Amoy Testnet using Web3.py.
   - Submits real Web3 raw transactions to anchor deterministic cryptographic hashes on-chain.
   - NEVER SIMULATES BLOCKCHAIN SUCCESS. Every anchoring request builds, signs, broadcasts, and confirms real transactions.

2. STRICT PRIVACY & ZERO PII ON-CHAIN:
   - NO raw binary image data is transmitted or stored on-chain.
   - NO 128-dimensional face embedding vectors are transmitted or stored on-chain.
   - NO personal contact details (PII) are transmitted or stored on-chain.
   - Only 256-bit SHA-256 byte digests (bytes32) and block timestamps are stored.

3. ROBUST ERROR HANDLING & EDGE CASE RESILIENCE:
   - RPC Failure (unreachable RPC / timeout)
   - Insufficient Gas (wallet balance lower than gas fees)
   - Transaction Rejection (reverted transaction / duplicate proof ID)
   - Timeout (transaction not mined within confirmation window)
   - Invalid Contract (invalid address or missing bytecode)
   - Wrong Network (connected chain ID does not match Polygon Amoy 80002)
"""

import hashlib
import logging
import os
from typing import Dict, Any, Union, Optional
from web3 import Web3
from web3.exceptions import ContractCustomError, TransactionNotFound

from app.config import BASE_DIR
from app.models.evidence_schemas import (
    EvidencePackage,
    VeridexFingerprintResult,
    BlockchainAnchoringResult,
    OnChainProofRecord,
    IntegrityVerificationResult,
)

from app.services.evidence_service import generate_veridex_fingerprint

logger = logging.getLogger("veridex.blockchain_service")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# VeridexRegistry Contract ABI
VERIDEX_REGISTRY_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "proofId", "type": "bytes32"},
            {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "inputImageHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "matchedImageHash", "type": "bytes32"},
        ],
        "name": "anchorProof",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "proofId", "type": "bytes32"}],
        "name": "getProof",
        "outputs": [
            {
                "components": [
                    {"internalType": "bytes32", "name": "proofId", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "inputImageHash", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "matchedImageHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "address", "name": "submitter", "type": "address"},
                ],
                "internalType": "struct VeridexRegistry.ProofRecord",
                "name": "record",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "proofId", "type": "bytes32"}],
        "name": "hasProof",
        "outputs": [{"internalType": "bool", "name": "exists", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getProofCount",
        "outputs": [{"internalType": "uint256", "name": "count", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "bytes32", "name": "proofId", "type": "bytes32"},
            {"indexed": True, "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
            {"indexed": True, "internalType": "address", "name": "submitter", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
        ],
        "name": "ProofAnchored",
        "type": "event",
    },
]


# ==================================================
# CUSTOM EXCEPTION CLASSES
# ==================================================

class BlockchainError(Exception):
    """Base exception for blockchain integration failures."""
    pass


class RPCFailureError(BlockchainError):
    """Raised when Web3 RPC connection fails or returns HTTP 500 error."""
    pass


class WrongNetworkError(BlockchainError):
    """Raised when connected network chain ID does not match expected target network."""
    pass


class InvalidContractError(BlockchainError):
    """Raised when contract address is invalid or lacks deployed bytecode."""
    pass


class InsufficientGasError(BlockchainError):
    """Raised when wallet POL balance is insufficient for gas fees."""
    pass


class TransactionRejectionError(BlockchainError):
    """Raised when transaction is rejected or reverted on-chain (e.g. duplicate proofId)."""
    pass


class BlockchainTimeoutError(BlockchainError):
    """Raised when transaction receipt is not confirmed within specified timeout limit."""
    pass


# ==================================================
# HELPER UTILITIES
# ==================================================

def to_bytes32(val: Union[str, bytes]) -> bytes:
    """Convert a string or hex digest into a 32-byte bytes32 representation.

    Args:
        val: Hex string (e.g. "a1b2c3..."), bytes, or arbitrary string.

    Returns:
        32-byte binary object.
    """
    if isinstance(val, bytes):
        if len(val) == 32:
            return val
        return hashlib.sha256(val).digest()

    clean = val.strip()
    if clean.startswith(("0x", "0X")):
        clean = clean[2:]

    if len(clean) == 64 and all(c in "0123456789abcdefABCDEF" for c in clean):
        return bytes.fromhex(clean)

    # Hash arbitrary strings to 32 bytes
    return hashlib.sha256(clean.encode("utf-8")).digest()


def _get_env_config(
    rpc_url: Optional[str] = None,
    private_key: Optional[str] = None,
    contract_address: Optional[str] = None,
) -> tuple[str, str, str]:
    """Resolve environment configuration settings for Web3 connection."""
    url = rpc_url or os.getenv("POLYGON_RPC_URL") or os.getenv("POLYGON_AMOY_RPC_URL") or "https://polygon-amoy-bor-rpc.publicnode.com"
    pk = private_key or os.getenv("PRIVATE_KEY") or os.getenv("POLYGON_AMOY_PRIVATE_KEY") or ""
    addr = contract_address or os.getenv("CONTRACT_ADDRESS") or "0xA7F56AE142C114fCA9bC0386CdD693e665ADF101"

    return url.strip(), pk.strip(), addr.strip()


def get_web3_connection(rpc_url: Optional[str] = None, expected_chain_id: int = 80002) -> Web3:
    """Establish and validate Web3 connection to RPC provider.

    Args:
        rpc_url: RPC provider URL.
        expected_chain_id: Expected network chain ID (default: 80002 for Polygon Amoy).

    Returns:
        Connected Web3 instance.

    Raises:
        RPCFailureError: If RPC connection fails.
        WrongNetworkError: If chain ID does not match expected_chain_id.
    """
    url, _, _ = _get_env_config(rpc_url=rpc_url)

    try:
        w3 = Web3(Web3.HTTPProvider(url))
        if not w3.is_connected():
            raise RPCFailureError(f"Failed to connect to RPC provider endpoint: '{url}'")

        connected_chain_id = w3.eth.chain_id
        if expected_chain_id is not None and connected_chain_id != expected_chain_id:
            raise WrongNetworkError(
                f"Connected chain ID ({connected_chain_id}) does not match expected Polygon Amoy testnet chain ID ({expected_chain_id})"
            )

        return w3

    except (RPCFailureError, WrongNetworkError):
        raise
    except Exception as e:
        raise RPCFailureError(f"Network failure connecting to RPC provider '{url}': {str(e)}") from e


# ==================================================
# CORE BLOCKCHAIN SERVICE FUNCTIONS
# ==================================================

def wait_for_confirmation(
    w3: Web3,
    tx_hash: Union[str, bytes],
    timeout_seconds: float = 120.0,
    poll_latency: float = 2.0,
) -> Any:
    """Wait for on-chain transaction mining and confirmation receipt.

    Args:
        w3: Connected Web3 instance.
        tx_hash: Transaction hash digest (bytes or hex string).
        timeout_seconds: Maximum wait timeout limit in seconds.
        poll_latency: Polling interval latency in seconds.

    Returns:
        Transaction receipt object.

    Raises:
        BlockchainTimeoutError: If transaction receipt is not mined within timeout window.
    """
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout_seconds, poll_latency=poll_latency)
        return receipt
    except Exception as e:
        tx_str = tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash)
        raise BlockchainTimeoutError(
            f"Transaction confirmation timed out ({timeout_seconds:.1f}s) for tx hash '{tx_str}': {str(e)}"
        ) from e


def anchor_evidence(
    evidence_input: Union[EvidencePackage, VeridexFingerprintResult, Dict[str, Any]],
    rpc_url: Optional[str] = None,
    private_key: Optional[str] = None,
    contract_address: Optional[str] = None,
    timeout_seconds: float = 120.0,
) -> BlockchainAnchoringResult:
    """Anchor deterministic evidence fingerprint (EVIDENCE DNA) onto Polygon Amoy smart contract.

    Pipeline:
    Evidence Package -> VERIDEX Fingerprint -> Web3.py -> Polygon Amoy Contract -> Tx Confirmation

    Args:
        evidence_input: EvidencePackage object, Fingerprint object, or payload dictionary.
        rpc_url: Optional custom RPC URL.
        private_key: Optional wallet private key string.
        contract_address: Optional deployed contract address string.
        timeout_seconds: Confirmation receipt timeout limit in seconds.

    Returns:
        BlockchainAnchoringResult schema containing proof_id, evidence_hash, transaction_hash, block_number, network.

    Raises:
        RPCFailureError: If RPC connection fails.
        WrongNetworkError: If network chain ID does not match Polygon Amoy (80002).
        InvalidContractError: If contract address is invalid or lacks bytecode.
        InsufficientGasError: If wallet POL balance is insufficient.
        TransactionRejectionError: If transaction reverts (e.g. duplicate proofId).
        BlockchainTimeoutError: If transaction mining times out.
    """
    # 1. Resolve Evidence Fingerprint Details
    if isinstance(evidence_input, VeridexFingerprintResult):
        fingerprint = evidence_input
    elif isinstance(evidence_input, EvidencePackage):
        fingerprint = generate_veridex_fingerprint(evidence_input)
    elif isinstance(evidence_input, dict):
        if "evidence_hash" in evidence_input and "record_id" in evidence_input:
            fingerprint = VeridexFingerprintResult(**evidence_input)
        else:
            package = EvidencePackage(**evidence_input)
            fingerprint = generate_veridex_fingerprint(package)
    else:
        raise TypeError(f"Unsupported evidence input type: {type(evidence_input).__name__}")

    package = fingerprint.evidence_package
    if package is None:
        raise ValueError("Evidence input must include an underlying EvidencePackage.")

    proof_id_str = fingerprint.record_id
    evidence_hash_str = fingerprint.evidence_hash

    # 2. Resolve Environment & Web3 Connection
    url, pk, addr = _get_env_config(rpc_url=rpc_url, private_key=private_key, contract_address=contract_address)
    w3 = get_web3_connection(rpc_url=url, expected_chain_id=80002)

    # 3. Validate Contract Address & Bytecode
    if not addr or not w3.is_address(addr):
        raise InvalidContractError(f"Invalid Ethereum contract address format: '{addr}'")

    try:
        checksum_addr = w3.to_checksum_address(addr)
        code = w3.eth.get_code(checksum_addr)
    except Exception as e:
        raise InvalidContractError(f"Failed to query bytecode for contract address '{addr}': {str(e)}") from e

    if not code or code == b"" or code.hex() in ("0x", "0x0"):
        raise InvalidContractError(f"No smart contract bytecode found deployed at address '{checksum_addr}' on Polygon Amoy network.")

    if not pk:
        raise InsufficientGasError("PRIVATE_KEY environment variable is not configured. Real transaction signing requires a wallet private key.")

    contract = w3.eth.contract(address=checksum_addr, abi=VERIDEX_REGISTRY_ABI)


    # 4. Format bytes32 Arguments for Smart Contract Invocation
    proof_bytes = to_bytes32(proof_id_str)
    ev_bytes = to_bytes32(evidence_hash_str)
    in_bytes = to_bytes32(package.input_image_sha256)
    match_bytes = to_bytes32(package.matched_image_sha256)

    # Check for duplicate proof on-chain prior to submitting transaction
    try:
        if contract.functions.hasProof(proof_bytes).call():
            raise TransactionRejectionError(f"Proof ID '{proof_id_str}' has already been anchored on-chain in VeridexRegistry contract.")
    except TransactionRejectionError:
        raise
    except Exception as e:
        logger.warning("hasProof view check warning: %s", str(e))

    # 5. Account Setup & Gas Balance Check
    try:
        account = w3.eth.account.from_key(pk)
    except Exception as e:
        raise InvalidContractError(f"Failed to load wallet account from PRIVATE_KEY: {str(e)}") from e

    balance = w3.eth.get_balance(account.address)
    gas_price = w3.eth.gas_price

    try:
        estimated_gas = contract.functions.anchorProof(
            proof_bytes, ev_bytes, in_bytes, match_bytes
        ).estimate_gas({"from": account.address})
    except ContractCustomError as e:
        raise TransactionRejectionError(f"Smart contract custom error on estimate_gas: {str(e)}") from e
    except Exception as e:
        err_msg = str(e)
        if "ProofAlreadyAnchored" in err_msg or "already anchored" in err_msg.lower():
            raise TransactionRejectionError(f"Duplicate proof ID '{proof_id_str}' rejected by smart contract.") from e
        raise TransactionRejectionError(f"Transaction estimation failed: {err_msg}") from e

    total_gas_cost = estimated_gas * gas_price
    if balance < total_gas_cost:
        balance_eth = w3.from_wei(balance, "ether")
        cost_eth = w3.from_wei(total_gas_cost, "ether")
        raise InsufficientGasError(
            f"Insufficient POL balance on wallet {account.address} ({balance_eth:.6f} POL available, required estimated gas: {cost_eth:.6f} POL)"
        )

    # 6. Build, Sign & Broadcast Real Web3 Transaction
    nonce = w3.eth.get_transaction_count(account.address)
    tx_params = contract.functions.anchorProof(
        proof_bytes, ev_bytes, in_bytes, match_bytes
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "chainId": 80002,
        "gas": int(estimated_gas * 1.2),
        "gasPrice": gas_price,
    })

    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key=pk)
    raw_tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction if hasattr(signed_tx, "raw_transaction") else signed_tx.rawTransaction)
    tx_hash_str = w3.to_hex(raw_tx_hash)

    logger.info("Broadcasted real Web3 transaction | Tx Hash: %s | Proof ID: %s", tx_hash_str, proof_id_str)

    # 7. Wait for On-Chain Confirmation Receipt
    receipt = wait_for_confirmation(w3, raw_tx_hash, timeout_seconds=timeout_seconds)
    if receipt.status != 1:
        raise TransactionRejectionError(f"Transaction reverted on-chain | Status: {receipt.status} | Tx Hash: {tx_hash_str}")

    block_num_str = str(receipt.blockNumber)
    logger.info("Transaction confirmed on-chain | Block: %s | Tx Hash: %s", block_num_str, tx_hash_str)

    return BlockchainAnchoringResult(
        proof_id=proof_id_str,
        evidence_hash=evidence_hash_str,
        transaction_hash=tx_hash_str,
        block_number=block_num_str,
        network="Polygon Amoy",
    )


def get_on_chain_proof(
    proof_id: Union[str, bytes],
    rpc_url: Optional[str] = None,
    contract_address: Optional[str] = None,
) -> OnChainProofRecord:
    """Retrieve an anchored evidence proof record directly from the VeridexRegistry smart contract on-chain.

    Args:
        proof_id: Unique proof identifier string or bytes.
        rpc_url: Optional custom RPC provider URL.
        contract_address: Optional deployed contract address.

    Returns:
        OnChainProofRecord schema instance.

    Raises:
        RPCFailureError: If RPC connection fails.
        InvalidContractError: If contract is invalid.
        TransactionRejectionError: If proof_id is not found on-chain.
    """
    url, _, addr = _get_env_config(rpc_url=rpc_url, contract_address=contract_address)
    w3 = get_web3_connection(rpc_url=url, expected_chain_id=80002)

    checksum_addr = w3.to_checksum_address(addr)
    contract = w3.eth.contract(address=checksum_addr, abi=VERIDEX_REGISTRY_ABI)

    proof_bytes = to_bytes32(proof_id if isinstance(proof_id, str) else proof_id.hex())

    try:
        record_tuple = contract.functions.getProof(proof_bytes).call()
    except Exception as e:
        err_msg = str(e)
        if "ProofNotFound" in err_msg or "not found" in err_msg.lower():
            raise TransactionRejectionError(f"Proof ID '{proof_id}' was not found in VeridexRegistry on-chain.") from e
        raise TransactionRejectionError(f"Failed to query on-chain proof record for '{proof_id}': {err_msg}") from e

    rec_proof_id, rec_evidence_hash, rec_input_hash, rec_matched_hash, rec_timestamp, rec_submitter = record_tuple

    return OnChainProofRecord(
        proof_id=w3.to_hex(rec_proof_id),
        evidence_hash=w3.to_hex(rec_evidence_hash),
        input_image_hash=w3.to_hex(rec_input_hash),
        matched_image_hash=w3.to_hex(rec_matched_hash),
        timestamp=int(rec_timestamp),
        submitter=rec_submitter,
        network="Polygon Amoy",
    )


def verify_evidence_integrity(
    evidence_input: Union[EvidencePackage, VeridexFingerprintResult, Dict[str, Any]],
    proof_id: Optional[str] = None,
    rpc_url: Optional[str] = None,
    contract_address: Optional[str] = None,
) -> IntegrityVerificationResult:
    """Read actual smart contract record on-chain and compare against recomputed local Evidence DNA fingerprint.

    Pipeline:
    1. Recompute local canonical SHA-256 evidence fingerprint -> `local_hash`.
    2. Query VeridexRegistry smart contract directly on Polygon Amoy testnet -> `on_chain_hash`.
    3. Compare local_hash vs. on_chain_hash:
       - Match: returns verified=True, status="VERIFIED".
       - Mismatch: returns verified=False, status="TAMPER_DETECTED".

    Args:
        evidence_input: EvidencePackage object, Fingerprint object, or payload dictionary.
        proof_id: Optional proof identifier string override.
        rpc_url: Optional custom RPC provider URL.
        contract_address: Optional deployed contract address string.

    Returns:
        IntegrityVerificationResult schema instance.
    """
    # 1. Recompute Local Canonical Fingerprint
    if isinstance(evidence_input, VeridexFingerprintResult):
        fingerprint = evidence_input
    elif isinstance(evidence_input, EvidencePackage):
        fingerprint = generate_veridex_fingerprint(evidence_input)
    elif isinstance(evidence_input, dict):
        if "evidence_hash" in evidence_input and "record_id" in evidence_input:
            fingerprint = VeridexFingerprintResult(**evidence_input)
        else:
            package = EvidencePackage(**evidence_input)
            fingerprint = generate_veridex_fingerprint(package)
    else:
        raise TypeError(f"Unsupported evidence input type: {type(evidence_input).__name__}")

    target_proof_id = proof_id or fingerprint.record_id
    local_hash = fingerprint.evidence_hash.lower()

    # 2. Read Actual Blockchain Record On-Chain (No local caching)
    on_chain_record = get_on_chain_proof(target_proof_id, rpc_url=rpc_url, contract_address=contract_address)

    # Standardize on-chain hash string
    raw_on_chain_hash = on_chain_record.evidence_hash.strip()
    if raw_on_chain_hash.startswith(("0x", "0X")):
        raw_on_chain_hash = raw_on_chain_hash[2:]
    on_chain_hash = raw_on_chain_hash.lower()

    # 3. Perform Cryptographic Integrity Match Check
    is_verified = bool(local_hash == on_chain_hash)
    status = "VERIFIED" if is_verified else "TAMPER_DETECTED"

    if is_verified:
        details = f"Evidence integrity verified on-chain against Polygon Amoy registry (Record ID: {target_proof_id})."
    else:
        details = f"TAMPER DETECTED! Recomputed local fingerprint ({local_hash[:12]}...) does NOT match anchored on-chain fingerprint ({on_chain_hash[:12]}...)."

    logger.info("Integrity verification complete | Proof ID: %s | Verified: %s | Status: %s",
                target_proof_id, is_verified, status)

    return IntegrityVerificationResult(
        local_hash=local_hash,
        on_chain_hash=on_chain_hash,
        verified=is_verified,
        status=status,
        proof_id=target_proof_id,
        details=details,
    )


def simulate_tampering(
    evidence_input: Union[EvidencePackage, Dict[str, Any]],
    field_to_modify: str = "matched_url",
    new_value: Any = "https://tampered-malicious-site.com/fake.jpg",
) -> EvidencePackage:
    """Simulate evidence tampering by altering exactly ONE attribute of an EvidencePackage while preserving record_id.

    Args:
        evidence_input: EvidencePackage object or payload dictionary.
        field_to_modify: Attribute field name to tamper (e.g. matched_url, face_similarity, matched_image_sha256).
        new_value: Tampered replacement value.

    Returns:
        Tampered EvidencePackage object with altered payload.
    """
    if isinstance(evidence_input, EvidencePackage):
        data = evidence_input.model_dump()
    elif isinstance(evidence_input, dict):
        data = evidence_input.copy()
    else:
        raise TypeError(f"Expected EvidencePackage or dict, got {type(evidence_input).__name__}")

    if field_to_modify not in data:
        raise KeyError(f"Field '{field_to_modify}' is not a valid attribute of EvidencePackage.")

    logger.warning("Simulating evidence tampering | Field: %s | Old: %s -> New: %s",
                   field_to_modify, data[field_to_modify], new_value)

    data[field_to_modify] = new_value
    return EvidencePackage(**data)

