"""Assignment 11 · Security kit.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest professional/11-security/assignments/11-security-kit -v
"""

import base64
import binascii
import hashlib
import hmac
import json
import secrets
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 600_000


class InvalidToken(Exception):
    pass


def safe_join(base, *parts):
    """The resolved path base/parts..., or ValueError if it is not inside base."""
    raise NotImplementedError


def hash_password(password, *, iterations=DEFAULT_ITERATIONS, salt=None):
    """'pbkdf2_sha256$<iterations>$<salt base64>$<hash base64>' with a random 16-byte salt."""
    raise NotImplementedError


def verify_password(password, stored):
    """True if `password` matches the stored hash; False also for malformed hashes."""
    raise NotImplementedError


def needs_rehash(stored, iterations=DEFAULT_ITERATIONS):
    """True if the stored hash is malformed, another algorithm, or uses fewer iterations."""
    raise NotImplementedError


def sign_token(data, key, *, expires_at):
    """'<payload>.<signature>': base64url JSON of data + exp, signed with HMAC-SHA256."""
    raise NotImplementedError


def verify_token(token, key, *, now):
    """The signed data (without exp); InvalidToken if malformed, forged or expired."""
    raise NotImplementedError


def mask(secret, visible=4):
    """'plp_live_8f2a01bc77' -> '***************bc77'."""
    raise NotImplementedError


if __name__ == "__main__":
    stored = hash_password("correct horse battery staple")
    print(stored)
    print(verify_password("correct horse battery staple", stored), verify_password("Tr0ub4dor&3", stored))
    token = sign_token({"user": 42}, b"server-secret", expires_at=2_000_000_000)
    print(token)
    print(verify_token(token, b"server-secret", now=1_800_000_000))
    print(mask("plp_live_8f2a01bc77"))
