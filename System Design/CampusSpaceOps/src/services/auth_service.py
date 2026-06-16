import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import HASH_ALGORITHM, HASH_ITERATIONS, HASH_SALT
from database.db import fetchone, fetchall, execute


def _hash_password(password: str) -> str:
    dk = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode("utf-8"),
        HASH_SALT,
        HASH_ITERATIONS,
    )
    return dk.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    return _hash_password(password) == stored_hash


def authenticate(username: str, password: str) -> dict | None:
    row = fetchone("SELECT * FROM users WHERE username = ?", (username,))
    if row is None:
        return None
    if verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def create_user(username: str, password: str, role: str, full_name: str, email: str = "") -> int:
    pw_hash = _hash_password(password)
    return execute(
        "INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?,?,?,?,?)",
        (username, pw_hash, role, full_name, email),
    )


def get_all_users() -> list:
    return [dict(r) for r in fetchall(
        "SELECT id, username, role, full_name, email, created_at FROM users ORDER BY id"
    )]


def hash_for_seed(password: str) -> str:
    """Utility: print the hash to put in seed_data.sql."""
    return _hash_password(password)
