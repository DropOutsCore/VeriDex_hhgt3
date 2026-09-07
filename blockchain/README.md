# VERIDEX Blockchain Module

Smart contracts and anchoring pipeline for registering cryptographic evidence fingerprints onto the Polygon Amoy testnet.

## Technology Stack & Environment
- **Smart Contract Language**: Solidity `^0.8.20`
- **Development Tooling**: Hardhat
- **Target Network**: Polygon Amoy Testnet (Chain ID: `80002`)
- **RPC Endpoint**: `https://polygon-amoy-bor-rpc.publicnode.com`

## Polygon Amoy Overview & Why Testnet Is Used
1. **Polygon Amoy**: Official EVM-compatible Layer 2 testnet for Polygon PoS (replacing Mumbai). Uses testnet `POL` for gas fees and supports standard EVM smart contracts.
2. **Why Testnet**: Allows verification of tamper-evident timestamped proof anchoring, state reads, event emissions, and web3 integration without risking real mainnet capital.
3. **Decentralized Integrity**: Anyone can independently query contract state on Polygonscan to verify that an evidence fingerprint existed at a specific timestamp.

## Deployed Contract Information
- **Contract Name**: `VeridexRegistry.sol`
- **Contract Address**: `0xA7F56AE142C114fCA9bC0386CdD693e665ADF101`
- **Deployment Tx Hash**: `0x1e0b1c03ba329e9fb8bb8bcc2c5d87908002f23a2b5a7811cbda8b298d465d78`
- **Chain ID**: `80002`
- **Polygonscan Explorer**: [Amoy Contract Address](https://amoy.polygonscan.com/address/0xA7F56AE142C114fCA9bC0386CdD693e665ADF101)

## Command Reference

### Compile Contracts
```bash
npx hardhat compile
```

### Run Hardhat Tests
```bash
npx hardhat test
```

### Deploy to Polygon Amoy Testnet
```bash
npx hardhat run scripts/deploy.js --network amoy
```
