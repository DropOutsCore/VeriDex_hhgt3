const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("==================================================");
  console.log("VERIDEX POLYGON AMOY SMART CONTRACT DEPLOYMENT");
  console.log("==================================================");

  const networkName = hre.network.name;
  const networkConfig = hre.network.config;
  const providerNetwork = await hre.ethers.provider.getNetwork();
  const chainId = providerNetwork.chainId.toString();

  console.log(`Target Network : ${networkName}`);
  console.log(`Chain ID       : ${chainId}`);

  const [deployer] = await hre.ethers.getSigners();
  console.log(`Deployer Wallet: ${deployer.address}`);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log(`Wallet Balance : ${hre.ethers.formatEther(balance)} POL`);

  console.log("\nDeploying VeridexRegistry.sol...");
  const VeridexRegistry = await hre.ethers.getContractFactory("VeridexRegistry");
  const registry = await VeridexRegistry.deploy();

  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  const deploymentTx = registry.deploymentTransaction();
  const txHash = deploymentTx ? deploymentTx.hash : "N/A";

  console.log("\n==================================================");
  console.log("DEPLOYMENT SUCCESSFUL");
  console.log("==================================================");
  console.log(`Network          : ${networkName}`);
  console.log(`Chain ID         : ${chainId}`);
  console.log(`Contract Address : ${contractAddress}`);
  console.log(`Tx Hash          : ${txHash}`);

  // 1. Verify deployment by reading contract state
  console.log("\nVerifying contract deployment by reading state...");
  const initialProofCount = await registry.getProofCount();
  console.log(`Verified getProofCount() state call -> Total Proofs: ${initialProofCount.toString()}`);

  // 2. Save contract address and network config to root .env
  const envPath = path.resolve(__dirname, "../../.env");
  let envContent = "";
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, "utf8");
  } else {
    // Copy from .env.example baseline
    const examplePath = path.resolve(__dirname, "../../.env.example");
    if (fs.existsSync(examplePath)) {
      envContent = fs.readFileSync(examplePath, "utf8");
    }
  }

  const envVars = {
    CONTRACT_ADDRESS: contractAddress,
    POLYGON_RPC_URL: networkConfig.url || "https://polygon-amoy-bor-rpc.publicnode.com",
    POLYGON_CHAIN_ID: chainId,
  };

  for (const [key, value] of Object.entries(envVars)) {
    const regex = new RegExp(`^${key}=.*$`, "m");
    if (regex.test(envContent)) {
      envContent = envContent.replace(regex, `${key}=${value}`);
    } else {
      envContent += `\n${key}=${value}`;
    }
  }

  fs.writeFileSync(envPath, envContent.trim() + "\n", "utf8");
  console.log(`\nSaved CONTRACT_ADDRESS (${contractAddress}) to .env`);

  console.log("\n==================================================");
  console.log("PHASE 10 OUTPUT SUMMARY");
  console.log("==================================================");
  console.log(`network: ${networkName}`);
  console.log(`chain ID: ${chainId}`);
  console.log(`contract address: ${contractAddress}`);
  console.log(`deployment transaction hash: ${txHash}`);
}

main().catch((error) => {
  console.error("Deployment Error:", error);
  process.exitCode = 1;
});
