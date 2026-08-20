from dataclasses import dataclass
from datetime import datetime


@dataclass
class Evidence:
    evidence_id: str
    case_id: str
    file_name: str
    file_path: str
    sha256_hash: str
    investigator_id: str
    created_at: str
    status: str = "REGISTERED"

    @staticmethod
    def create(
        evidence_id: str,
        case_id: str,
        file_name: str,
        file_path: str,
        sha256_hash: str,
        investigator_id: str
    ):
        return Evidence(
            evidence_id=evidence_id,
            case_id=case_id,
            file_name=file_name,
            file_path=file_path,
            sha256_hash=sha256_hash,
            investigator_id=investigator_id,
            created_at=datetime.now().isoformat(),
        )