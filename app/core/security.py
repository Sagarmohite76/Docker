import hashlib
import os


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using PBKDF2 with SHA-256 and a random salt.
    Returns format: 'salt$hash'
    """
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored 'salt$hash' string.
    """
    try:
        salt, stored_hash = hashed_password.split("$", 1)
    except ValueError:
        return False

    computed_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return computed_hash == stored_hash
