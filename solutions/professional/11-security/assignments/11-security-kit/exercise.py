"""Assignment 11 · Security kit: template solution."""

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


# --- paths ---------------------------------------------------------------------

def safe_join(base, *parts):
    root = Path(base).resolve()
    # resolve() removes ".." and follows symbolic links, so the check sees the REAL target.
    target = root.joinpath(*parts).resolve()
    if not target.is_relative_to(root):
        raise ValueError("path escapes the base directory")
    return target


# --- passwords -----------------------------------------------------------------

def _b64(data):
    return base64.b64encode(data).decode("ascii")


def hash_password(password, *, iterations=DEFAULT_ITERATIONS, salt=None):
    salt = secrets.token_bytes(16) if salt is None else salt
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    # Everything needed to check the password later travels with the hash.
    return f"{ALGORITHM}${iterations}${_b64(salt)}${_b64(digest)}"


def _parse(stored):
    """(iterations, salt, digest), or None if `stored` is not one of our hashes."""
    try:
        algorithm, iterations, salt, digest = stored.split("$")
        if algorithm != ALGORITHM:
            return None
        return int(iterations), base64.b64decode(salt, validate=True), base64.b64decode(digest, validate=True)
    except (ValueError, binascii.Error):
        return None


def verify_password(password, stored):
    parsed = _parse(stored)
    if parsed is None:
        return False
    iterations, salt, expected = parsed
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return hmac.compare_digest(actual, expected)         # constant time: no timing leak


def needs_rehash(stored, iterations=DEFAULT_ITERATIONS):
    parsed = _parse(stored)
    return parsed is None or parsed[0] < iterations


# --- signed tokens -------------------------------------------------------------

def _b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64url(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _signature(payload, key):
    return _b64url(hmac.new(key, payload.encode("ascii"), hashlib.sha256).digest())


def sign_token(data, key, *, expires_at):
    body = json.dumps({**data, "exp": expires_at}, sort_keys=True, separators=(",", ":"))
    payload = _b64url(body.encode())
    return f"{payload}.{_signature(payload, key)}"


def verify_token(token, key, *, now):
    payload, dot, signature = token.partition(".")
    if not dot or not payload or not signature or not payload.isascii():
        raise InvalidToken("malformed token")
    # Check the signature FIRST: never parse or trust data that might have been forged.
    if not hmac.compare_digest(signature.encode(), _signature(payload, key).encode()):
        raise InvalidToken("bad signature")
    try:
        data = json.loads(_unb64url(payload))
    except ValueError:
        raise InvalidToken("malformed token") from None
    if now >= data.pop("exp"):
        raise InvalidToken("token expired")
    return data


# --- logging -------------------------------------------------------------------

def mask(secret, visible=4):
    if len(secret) <= visible:
        return "*" * len(secret)
    return "*" * (len(secret) - visible) + secret[len(secret) - visible:]


if __name__ == "__main__":
    stored = hash_password("correct horse battery staple")
    print(stored)
    print(verify_password("correct horse battery staple", stored), verify_password("Tr0ub4dor&3", stored))
    token = sign_token({"user": 42}, b"server-secret", expires_at=2_000_000_000)
    print(token)
    print(verify_token(token, b"server-secret", now=1_800_000_000))
    print(mask("plp_live_8f2a01bc77"))
