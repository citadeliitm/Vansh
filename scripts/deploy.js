const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying contract...");

  const PMKisanRegistry = await hre.ethers.getContractFactory("PMKisanRegistry");
  const contract = await PMKisanRegistry.deploy();

  console.log("⏳ Waiting for deployment to be mined...");
  await contract.waitForDeployment();

  console.log("✅ Contract deployed at:", contract.target);
}

main().catch((error) => {
  console.error("❌ Deployment failed:", error);
  process.exitCode = 1;
});
