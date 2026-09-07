const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("VeridexRegistry Smart Contract", function () {
  let registry;
  let owner;
  let addr1;

  // Sample bytes32 test hashes
  const proofId1 = ethers.keccak256(ethers.toUtf8Bytes("rec_test_001"));
  const evidenceHash1 = ethers.keccak256(ethers.toUtf8Bytes("canonical_json_evidence_dna_1"));
  const inputImageHash1 = "0x" + "a".repeat(64);
  const matchedImageHash1 = "0x" + "b".repeat(64);

  const proofId2 = ethers.keccak256(ethers.toUtf8Bytes("rec_test_002"));
  const evidenceHash2 = ethers.keccak256(ethers.toUtf8Bytes("canonical_json_evidence_dna_2"));

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();
    const VeridexRegistryFactory = await ethers.getContractFactory("VeridexRegistry");
    registry = await VeridexRegistryFactory.deploy();
    await registry.waitForDeployment();
  });

  describe("1. Successful Proof Anchoring", function () {
    it("should allow anchoring a valid evidence fingerprint", async function () {
      const tx = await registry.anchorProof(proofId1, evidenceHash1, inputImageHash1, matchedImageHash1);
      await tx.wait();

      expect(await registry.hasProof(proofId1)).to.equal(true);
      expect(await registry.getProofCount()).to.equal(1);
    });

    it("should increment total proof count when multiple distinct proofs are anchored", async function () {
      await registry.anchorProof(proofId1, evidenceHash1, inputImageHash1, matchedImageHash1);
      await registry.anchorProof(proofId2, evidenceHash2, inputImageHash1, matchedImageHash1);

      expect(await registry.getProofCount()).to.equal(2);
    });
  });

  describe("2. Proof Retrieval", function () {
    it("should accurately retrieve anchored proof record details", async function () {
      const tx = await registry.connect(addr1).anchorProof(proofId1, evidenceHash1, inputImageHash1, matchedImageHash1);
      const receipt = await tx.wait();
      const block = await ethers.provider.getBlock(receipt.blockNumber);

      const record = await registry.getProof(proofId1);

      expect(record.proofId).to.equal(proofId1);
      expect(record.evidenceHash).to.equal(evidenceHash1);
      expect(record.inputImageHash).to.equal(inputImageHash1);
      expect(record.matchedImageHash).to.equal(matchedImageHash1);
      expect(record.timestamp).to.equal(block.timestamp);
      expect(record.submitter).to.equal(addr1.address);
    });

    it("should revert if attempting to retrieve an unanchored proofId", async function () {
      const fakeProofId = ethers.keccak256(ethers.toUtf8Bytes("non_existent_proof"));
      await expect(registry.getProof(fakeProofId))
        .to.be.revertedWithCustomError(registry, "ProofNotFound")
        .withArgs(fakeProofId);
    });
  });

  describe("3. Event Emission", function () {
    it("should emit ProofAnchored event with correct indexed args upon successful anchoring", async function () {
      const tx = registry.connect(owner).anchorProof(proofId1, evidenceHash1, inputImageHash1, matchedImageHash1);

      await expect(tx)
        .to.emit(registry, "ProofAnchored")
        .withArgs(proofId1, evidenceHash1, owner.address, (timestamp) => timestamp > 0);
    });
  });

  describe("4. Duplicate Proof Rejection", function () {
    it("should reject duplicate anchoring attempts for the same proofId", async function () {
      await registry.anchorProof(proofId1, evidenceHash1, inputImageHash1, matchedImageHash1);

      await expect(registry.anchorProof(proofId1, evidenceHash1, inputImageHash1, matchedImageHash1))
        .to.be.revertedWithCustomError(registry, "ProofAlreadyAnchored")
        .withArgs(proofId1);
    });
  });

  describe("5. Validation & Edge Cases", function () {
    it("should revert if any hash argument is zero bytes32", async function () {
      const zero = ethers.ZeroHash;
      await expect(registry.anchorProof(zero, evidenceHash1, inputImageHash1, matchedImageHash1))
        .to.be.revertedWithCustomError(registry, "InvalidZeroHash")
        .withArgs("proofId");

      await expect(registry.anchorProof(proofId1, zero, inputImageHash1, matchedImageHash1))
        .to.be.revertedWithCustomError(registry, "InvalidZeroHash")
        .withArgs("evidenceHash");
    });
  });
});
