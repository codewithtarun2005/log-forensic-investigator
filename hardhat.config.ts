import { defineConfig } from "hardhat/config";
import hardhatEthers from "@nomicfoundation/hardhat-ethers";

export default defineConfig({
  plugins: [hardhatEthers],

  solidity: {
    version: "0.8.28",
  },

  paths: {
    sources: "./blockchain/contracts",
    artifacts: "./blockchain/artifacts",
    cache: "./blockchain/cache",
  },
});