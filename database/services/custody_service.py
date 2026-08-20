from datetime import datetime
from forensic.hashing.hash_service import calculate_sha256
from database.models.evidence import Evidence


def register_evidence(
    file_path: str,
    case_id: str,
    evidence_id: str,
    investigator_id: str
) -> Evidence:
    """
    Register a piece of digital evidence.

    The file is hashed using SHA-256 and the
    resulting evidence object is created.
    """

    sha256_hash = calculate_sha256(file_path)

    file_name = file_path.replace("\\", "/").split("/")[-1]

    evidence = Evidence.create(
        evidence_id=evidence_id,
        case_id=case_id,
        file_name=file_name,
        file_path=file_path,
        sha256_hash=sha256_hash,
        investigator_id=investigator_id
    )

    return evidence

from dataclasses import dataclass


@dataclass
class CustodyEvent:
    evidence_id: str
    action: str
    investigator_id: str
    timestamp: str
    description: str


def create_custody_event(
    evidence_id: str,
    action: str,
    investigator_id: str,
    description: str = ""
) -> CustodyEvent:

    return CustodyEvent(
        evidence_id=evidence_id,
        action=action,
        investigator_id=investigator_id,
        timestamp=datetime.now().isoformat(),
        description=description
    )