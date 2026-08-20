import hashlib


def calculate_sha256(file_path: str) -> str:
    """
    Generate SHA-256 hash for a file.
    Reads the file in chunks so large evidence files can be handled.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()

def verify_file_integrity(file_path: str, expected_hash: str) -> bool:
    """
    Verify whether the current file matches its original SHA-256 hash.
    """

    current_hash = calculate_sha256(file_path)

    return current_hash == expected_hash