import json
import os
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3


# Load environment variables
load_dotenv()


RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
INVESTIGATOR_ADDRESS = os.getenv("INVESTIGATOR_ADDRESS")


# Connect to local Hardhat blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))


# Load contract ABI
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ABI_PATH = (
    PROJECT_ROOT
    / "blockchain"
    / "artifacts"
    / "blockchain"
    / "contracts"
    / "EvidenceRegistry.sol"
    / "EvidenceRegistry.json"
)

with open(ABI_PATH, "r") as file:
    contract_data = json.load(file)

ABI = contract_data["abi"]


# Create contract instance
contract = web3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI
)


def check_blockchain_connection():
    return web3.is_connected()


def register_evidence_on_blockchain(
    evidence_id: str,
    case_id: str,
    evidence_hash: str,
    investigator_id: str
):
    """
    Register evidence metadata on the local blockchain.
    """

    if not web3.is_connected():
        raise ConnectionError("Blockchain connection failed")

    transaction_hash = contract.functions.registerEvidence(
        evidence_id,
        case_id,
        evidence_hash,
        investigator_id
    ).transact({
        "from": Web3.to_checksum_address(INVESTIGATOR_ADDRESS)
    })

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    return {
        "transaction_hash": receipt["transactionHash"].hex(),
        "block_number": receipt["blockNumber"],
        "contract_address": CONTRACT_ADDRESS
    }


def get_evidence_from_blockchain(evidence_id: str):
    """
    Retrieve registered evidence from blockchain.
    """

    result = contract.functions.getEvidence(
        evidence_id
    ).call()

    return {
        "evidence_id": result[0],
        "case_id": result[1],
        "evidence_hash": result[2],
        "investigator_id": result[3],
        "timestamp": result[4],
        "registered": result[5]
    }

from forensic.hashing.hash_service import calculate_sha256


def verify_evidence_integrity(file_path: str, evidence_id: str):
    """
    Compare the current evidence file hash
    with the hash stored on the blockchain.
    """

    blockchain_evidence = get_evidence_from_blockchain(evidence_id)

    if not blockchain_evidence["registered"]:
        return {
            "verified": False,
            "status": "NOT_REGISTERED",
            "message": "Evidence is not registered on blockchain."
        }

    current_hash = calculate_sha256(file_path)
    blockchain_hash = blockchain_evidence["evidence_hash"]

    if current_hash == blockchain_hash:
        return {
            "verified": True,
            "status": "VERIFIED",
            "message": "Evidence integrity verified.",
            "current_hash": current_hash,
            "blockchain_hash": blockchain_hash
        }

    return {
        "verified": False,
        "status": "TAMPERED",
        "message": "Evidence has been modified.",
        "current_hash": current_hash,
        "blockchain_hash": blockchain_hash
    }