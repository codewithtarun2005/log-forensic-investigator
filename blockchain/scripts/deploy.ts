import { network } from "hardhat";

const { ethers } = await network.create();

const evidenceRegistry = await ethers.deployContract("EvidenceRegistry");

await evidenceRegistry.waitForDeployment();

console.log(
  "EvidenceRegistry deployed to:",
  await evidenceRegistry.getAddress()
);