const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

  const PMKisanRegistry = await hre.ethers.getContractAt("PMKisanRegistry", contractAddress);

  // ✅ Store mock decision
  const tx = await PMKisanRegistry.storeDecision(
    "QmFakeDatabaseCID",
    "QmFakeExplanationCID",
    "Eligible",
    42
  );
  await tx.wait();
  console.log("✅ Decision stored");

  // ✅ Read back the record
  const record = await PMKisanRegistry.getRecord(deployer.address, 0);
  console.log("📦 Retrieved Record:");
  console.log("Database CID:", record[0]);
  console.log("Explanation CID:", record[1]);
  console.log("Decision:", record[2]);
  console.log("Participant ID:", record[3].toString());
}

main().catch((error) => {
  console.error("❌ Error:", error);
  process.exitCode = 1;
});
