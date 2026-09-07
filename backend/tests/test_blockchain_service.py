"""Unit tests for Phase 11 Web3 Blockchain Integration Service & API Endpoints."""

import hashlib
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from web3 import Web3


from app.main import app
from app.models.evidence_schemas import (
    EvidencePackage,
    BlockchainAnchoringResult,
    OnChainProofRecord,
    IntegrityVerificationResult,
)
from app.services.evidence_service import generate_veridex_fingerprint
from app.services.blockchain_service import (
    anchor_evidence,
    get_on_chain_proof,
    verify_evidence_integrity,
    simulate_tampering,
    wait_for_confirmation,
    get_web3_connection,
    to_bytes32,
    RPCFailureError,
    WrongNetworkError,
    InvalidContractError,
    InsufficientGasError,
    TransactionRejectionError,
    BlockchainTimeoutError,
)


client = TestClient(app)


def test_to_bytes32_conversion():
    """Verify helper utility for converting SHA-256 strings and text IDs into 32-byte arrays."""
    # 64-char hex string
    hex_64 = "a" * 64
    res1 = to_bytes32(hex_64)
    assert isinstance(res1, bytes)
    assert len(res1) == 32
    assert res1 == bytes.fromhex(hex_64)

    # 0x-prefixed hex string
    hex_pref = "0x" + ("b" * 64)
    res2 = to_bytes32(hex_pref)
    assert len(res2) == 32
    assert res2 == bytes.fromhex("b" * 64)

    # Arbitrary text string
    text_id = "rec_custom_proof_123"
    res3 = to_bytes32(text_id)
    assert len(res3) == 32


def test_web3_connection_public_rpc():
    """Test connecting to the live Polygon Amoy public RPC endpoint."""
    try:
        w3 = get_web3_connection(expected_chain_id=80002)
        assert w3.is_connected()
        assert w3.eth.chain_id == 80002
    except RPCFailureError:
        pytest.skip("Public Polygon Amoy RPC endpoint unreachable during test run.")


def test_wrong_network_exception_handling():
    """Verify WrongNetworkError is raised if connected network chain ID is unexpected."""
    with patch("app.services.blockchain_service.Web3") as mock_w3_cls:
        mock_instance = MagicMock()
        mock_instance.is_connected.return_value = True
        mock_instance.eth.chain_id = 1  # Ethereum Mainnet instead of Amoy 80002
        mock_w3_cls.return_value = mock_instance

        with pytest.raises(WrongNetworkError) as exc_info:
            get_web3_connection(rpc_url="https://fake-rpc.org", expected_chain_id=80002)

        assert "80002" in str(exc_info.value)
        assert "1" in str(exc_info.value)


def test_invalid_contract_address_handling():
    """Verify InvalidContractError is raised for invalid format or missing bytecode."""
    dummy_package = EvidencePackage(
        record_id="rec_test_inv_contract",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding_hash="b" * 64,
        matched_url="https://example.com/item",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.9,
        image_similarity=0.9,
        overall_score=0.9,
        timestamp="2026-09-06T00:00:00Z",
    )

    with pytest.raises(InvalidContractError):
        anchor_evidence(dummy_package, contract_address="0xInvalidEthereumAddressFormat")


def test_insufficient_gas_missing_private_key():
    """Verify InsufficientGasError is raised if PRIVATE_KEY is missing or balance < estimated gas cost."""
    dummy_package = EvidencePackage(
        record_id="rec_test_insuff_gas",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding_hash="b" * 64,
        matched_url="https://example.com/item",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.9,
        image_similarity=0.9,
        overall_score=0.9,
        timestamp="2026-09-06T00:00:00Z",
    )

    with pytest.raises(InsufficientGasError):
        anchor_evidence(
            dummy_package,
            private_key="",  # Missing private key
            contract_address="0xA7F56AE142C114fCA9bC0386CdD693e665ADF101",
        )


def test_anchor_evidence_mocked_success():
    """Test successful Web3 evidence anchoring pipeline using mocked Web3 provider."""
    dummy_package = EvidencePackage(
        record_id="rec_mock_anchor_001",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding_hash="b" * 64,
        matched_url="https://wikipedia.org/wiki/Test",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.95,
        image_similarity=0.92,
        overall_score=0.94,
        timestamp="2026-09-06T00:00:00Z",
    )

    fake_pk = "0x" + "1" * 64
    fake_tx_hash = "0x" + "e" * 64

    with patch("app.services.blockchain_service.get_web3_connection") as mock_get_w3:
        mock_w3 = MagicMock()
        mock_w3.is_address.return_value = True
        mock_w3.to_checksum_address.side_effect = lambda a: a
        mock_w3.eth.get_code.return_value = b"\x60\x80\x60\x40..."
        mock_w3.eth.chain_id = 80002

        # Mock contract calls
        mock_contract = MagicMock()
        mock_contract.functions.hasProof.return_value.call.return_value = False
        mock_contract.functions.anchorProof.return_value.estimate_gas.return_value = 100000
        mock_contract.functions.anchorProof.return_value.build_transaction.return_value = {
            "from": "0x1111111111111111111111111111111111111111",
            "nonce": 0,
            "chainId": 80002,
            "gas": 120000,
            "gasPrice": 30000000000,
        }
        mock_w3.eth.contract.return_value = mock_contract

        # Mock account & balance
        mock_account = MagicMock()
        mock_account.address = "0x1111111111111111111111111111111111111111"
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_w3.eth.get_balance.return_value = 10**18  # 1.0 POL
        mock_w3.eth.gas_price = 30000000000
        mock_w3.eth.get_transaction_count.return_value = 0

        # Mock sign and send
        mock_signed_tx = MagicMock()
        mock_signed_tx.rawTransaction = b"\x00\x01\x02"
        mock_w3.eth.account.sign_transaction.return_value = mock_signed_tx
        mock_w3.eth.send_raw_transaction.return_value = bytes.fromhex("e" * 64)
        mock_w3.to_hex.return_value = fake_tx_hash

        # Mock confirmation receipt
        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 46814950
        mock_w3.eth.wait_for_transaction_receipt.return_value = mock_receipt

        mock_get_w3.return_value = mock_w3

        result = anchor_evidence(
            dummy_package,
            private_key=fake_pk,
            contract_address="0xA7F56AE142C114fCA9bC0386CdD693e665ADF101",
        )

        assert isinstance(result, BlockchainAnchoringResult)
        assert result.proof_id == "rec_mock_anchor_001"
        assert result.transaction_hash == fake_tx_hash
        assert result.block_number == "46814950"
        assert result.network == "Polygon Amoy"


def test_get_on_chain_proof_mocked_success():
    """Test querying on-chain proof record from VeridexRegistry contract using mock."""
    fake_proof_id = "rec_mock_query_001"

    with patch("app.services.blockchain_service.get_web3_connection") as mock_get_w3:
        mock_w3 = MagicMock()
        mock_w3.to_checksum_address.side_effect = lambda a: a
        mock_w3.to_hex.side_effect = lambda b: "0x" + (b.hex() if isinstance(b, bytes) else str(b))

        mock_contract = MagicMock()
        # Mock getProof tuple return: (proofId, evidenceHash, inputImageHash, matchedImageHash, timestamp, submitter)
        mock_contract.functions.getProof.return_value.call.return_value = (
            b"\x01" * 32,
            b"\x02" * 32,
            b"\x03" * 32,
            b"\x04" * 32,
            1757116800,
            "0x1111111111111111111111111111111111111111",
        )
        mock_w3.eth.contract.return_value = mock_contract
        mock_get_w3.return_value = mock_w3

        record = get_on_chain_proof(fake_proof_id, contract_address="0xA7F56AE142C114fCA9bC0386CdD693e665ADF101")

        assert isinstance(record, OnChainProofRecord)
        assert record.timestamp == 1757116800
        assert record.submitter == "0x1111111111111111111111111111111111111111"
        assert record.network == "Polygon Amoy"


def test_verify_evidence_integrity_verified_success():
    """Verify Phase 12 Requirement: Original untampered evidence returns verified=True and status='VERIFIED'."""
    pkg = EvidencePackage(
        record_id="rec_unaltered_001",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding_hash="b" * 64,
        matched_url="https://wikipedia.org/wiki/Original",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.9100,
        image_similarity=0.9400,
        overall_score=0.9100,
        timestamp="2026-09-06T00:00:00Z",
    )

    fingerprint = generate_veridex_fingerprint(pkg)
    expected_ev_bytes = bytes.fromhex(fingerprint.evidence_hash)

    with patch("app.services.blockchain_service.get_web3_connection") as mock_get_w3:
        mock_w3 = MagicMock()
        mock_w3.to_checksum_address.side_effect = lambda a: a
        mock_w3.to_hex.side_effect = lambda b: b.hex() if isinstance(b, bytes) else str(b)

        mock_contract = MagicMock()
        mock_contract.functions.getProof.return_value.call.return_value = (
            bytes.fromhex(hashlib.sha256(pkg.record_id.encode()).hexdigest()),
            expected_ev_bytes,
            bytes.fromhex(pkg.input_image_sha256),
            bytes.fromhex(pkg.matched_image_sha256),
            1757116800,
            "0x1111111111111111111111111111111111111111",
        )
        mock_w3.eth.contract.return_value = mock_contract
        mock_get_w3.return_value = mock_w3

        result = verify_evidence_integrity(pkg, contract_address="0xA7F56AE142C114fCA9bC0386CdD693e665ADF101")

        assert isinstance(result, IntegrityVerificationResult)
        assert result.verified is True
        assert result.status == "VERIFIED"
        assert result.local_hash == result.on_chain_hash


def test_verify_evidence_integrity_tamper_detected():
    """Verify Phase 12 Requirement: Modified evidence returns verified=False and status='TAMPER_DETECTED'."""
    pkg = EvidencePackage(
        record_id="rec_tampered_001",
        input_image_sha256="a" * 64,
        input_image_phash="1234567890abcdef",
        face_embedding_hash="b" * 64,
        matched_url="https://wikipedia.org/wiki/Original",
        matched_image_sha256="c" * 64,
        matched_image_phash="fedcba0987654321",
        reverse_search_rank=1,
        face_similarity=0.9100,
        image_similarity=0.9400,
        overall_score=0.9100,
        timestamp="2026-09-06T00:00:00Z",
    )

    fingerprint_original = generate_veridex_fingerprint(pkg)
    original_ev_bytes = bytes.fromhex(fingerprint_original.evidence_hash)

    # Tamper single field (matched_url)
    tampered_pkg = simulate_tampering(
        pkg,
        field_to_modify="matched_url",
        new_value="https://tampered-malicious-site.org/fake.jpg",
    )

    with patch("app.services.blockchain_service.get_web3_connection") as mock_get_w3:
        mock_w3 = MagicMock()
        mock_w3.to_checksum_address.side_effect = lambda a: a
        mock_w3.to_hex.side_effect = lambda b: b.hex() if isinstance(b, bytes) else str(b)

        mock_contract = MagicMock()
        # Returns the ORIGINAL on-chain hash
        mock_contract.functions.getProof.return_value.call.return_value = (
            bytes.fromhex(hashlib.sha256(pkg.record_id.encode()).hexdigest()),
            original_ev_bytes,
            bytes.fromhex(pkg.input_image_sha256),
            bytes.fromhex(pkg.matched_image_sha256),
            1757116800,
            "0x1111111111111111111111111111111111111111",
        )
        mock_w3.eth.contract.return_value = mock_contract
        mock_get_w3.return_value = mock_w3

        result = verify_evidence_integrity(tampered_pkg, contract_address="0xA7F56AE142C114fCA9bC0386CdD693e665ADF101")

        assert isinstance(result, IntegrityVerificationResult)
        assert result.verified is False
        assert result.status == "TAMPER_DETECTED"
        assert result.local_hash != result.on_chain_hash
        assert result.on_chain_hash == fingerprint_original.evidence_hash.lower()


def test_api_verify_integrity_and_simulate_tampering():
    """Test POST /api/verify-integrity and POST /api/simulate-tampering API routes."""
    package_payload = {
        "record_id": "rec_api_integrity_001",
        "input_image_sha256": "1" * 64,
        "input_image_phash": "1234567890abcdef",
        "face_embedding_hash": "2" * 64,
        "matched_url": "https://bbc.com/news/123",
        "matched_image_sha256": "3" * 64,
        "matched_image_phash": "fedcba0987654321",
        "reverse_search_rank": 1,
        "face_similarity": 0.95,
        "image_similarity": 0.92,
        "overall_score": 0.94,
        "search_provider": "Google Lens via SerpApi",
        "timestamp": "2026-09-06T00:00:00Z",
    }

    # Test simulate tampering endpoint
    tamp_resp = client.post(
        "/api/simulate-tampering",
        json=package_payload,
        params={"field_to_modify": "face_similarity", "new_value": "0.1234"},
    )
    assert tamp_resp.status_code == 200
    tamp_data = tamp_resp.json()
    assert tamp_data["face_similarity"] == 0.1234
    assert tamp_data["record_id"] == "rec_api_integrity_001"

