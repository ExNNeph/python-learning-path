"""Tests for assignment 11. Run: pytest professional/11-security/assignments/11-security-kit -v"""

import base64
import hashlib
import hmac
import json
import os
import sys

import pytest

FAST = 1_000          # few iterations keep the tests fast; production uses 600 000
KEY = b"server-secret"


# --- safe_join -----------------------------------------------------------------

@pytest.fixture
def base(tmp_path):
    root = tmp_path / "uploads"
    (root / "ada").mkdir(parents=True)
    (root / "ada" / "cv.pdf").write_text("cv")
    (tmp_path / "secret.txt").write_text("secret")
    return root


def test_safe_join_inside(ex, base):
    assert ex.safe_join(base, "ada", "cv.pdf") == (base / "ada" / "cv.pdf").resolve()
    assert ex.safe_join(str(base), "ada/cv.pdf") == (base / "ada" / "cv.pdf").resolve()
    assert ex.safe_join(base, "new-file.txt") == (base / "new-file.txt").resolve()   # need not exist
    assert ex.safe_join(base) == base.resolve()
    assert ex.safe_join(base, "ada/../ada/cv.pdf") == (base / "ada" / "cv.pdf").resolve()


@pytest.mark.parametrize("parts", [
    ("..", "secret.txt"),
    ("../../etc/passwd",),
    ("ada", "..", "..", "secret.txt"),
    ("..",),
])
def test_safe_join_traversal(ex, base, parts):
    with pytest.raises(ValueError, match="path escapes the base directory"):
        ex.safe_join(base, *parts)


def test_safe_join_absolute_part(ex, base, tmp_path):
    with pytest.raises(ValueError):
        ex.safe_join(base, str(tmp_path / "secret.txt"))


def test_safe_join_sibling_with_same_prefix(ex, base, tmp_path):
    (tmp_path / "uploads-private").mkdir()
    with pytest.raises(ValueError):
        ex.safe_join(base, "../uploads-private/x")        # a string prefix check would accept this


@pytest.mark.skipif(sys.platform == "win32", reason="symbolic links need extra rights on Windows")
def test_safe_join_follows_symlinks(ex, base, tmp_path):
    os.symlink(tmp_path / "secret.txt", base / "innocent.txt")
    with pytest.raises(ValueError):
        ex.safe_join(base, "innocent.txt")


# --- passwords -----------------------------------------------------------------

def test_hash_format(ex):
    salt = b"0123456789abcdef"
    stored = ex.hash_password("hunter2", iterations=FAST, salt=salt)
    expected = hashlib.pbkdf2_hmac("sha256", b"hunter2", salt, FAST)
    assert stored == f"pbkdf2_sha256${FAST}${base64.b64encode(salt).decode()}${base64.b64encode(expected).decode()}"


def test_hash_uses_random_salt(ex, monkeypatch):
    calls = []
    real = ex.secrets.token_bytes
    monkeypatch.setattr(ex.secrets, "token_bytes", lambda n: (calls.append(n), real(n))[1])
    first = ex.hash_password("same", iterations=FAST)
    second = ex.hash_password("same", iterations=FAST)
    assert first != second                                 # equal passwords, different hashes
    assert calls == [16, 16]
    assert len(base64.b64decode(first.split("$")[2])) == 16


def test_hash_default_iterations(ex):
    assert ex.hash_password("pw", salt=b"s" * 16).split("$")[1] == "600000"


def test_verify_password(ex):
    stored = ex.hash_password("correct horse battery staple", iterations=FAST)
    assert ex.verify_password("correct horse battery staple", stored) is True
    assert ex.verify_password("correct horse battery stapl", stored) is False
    assert ex.verify_password("", stored) is False


def test_verify_unicode_password(ex):
    stored = ex.hash_password("pässwörd 🔑", iterations=FAST)
    assert ex.verify_password("pässwörd 🔑", stored)
    assert not ex.verify_password("passwort 🔑", stored)


def test_verify_uses_compare_digest(ex, monkeypatch):
    calls = []
    real = hmac.compare_digest
    monkeypatch.setattr(ex.hmac, "compare_digest", lambda a, b: (calls.append(1), real(a, b))[1])
    ex.verify_password("pw", ex.hash_password("pw", iterations=FAST))
    assert calls


@pytest.mark.parametrize("stored", [
    "",
    "nonsense",
    "md5$1000$c2FsdA==$aGFzaA==",
    "pbkdf2_sha256$many$c2FsdA==$aGFzaA==",
    "pbkdf2_sha256$1000$not base64!$aGFzaA==",
    "pbkdf2_sha256$1000$c2FsdA==",
    "pbkdf2_sha256$1000$c2FsdA==$aGFzaA==$extra",
])
def test_verify_malformed_is_false(ex, stored):
    assert ex.verify_password("pw", stored) is False
    assert ex.needs_rehash(stored) is True


def test_needs_rehash(ex):
    old = ex.hash_password("pw", iterations=FAST)
    assert ex.needs_rehash(old) is True
    assert ex.needs_rehash(old, iterations=FAST) is False
    assert ex.needs_rehash(old, iterations=FAST - 1) is False
    assert ex.needs_rehash(ex.hash_password("pw", iterations=2 * FAST), iterations=2 * FAST) is False


# --- tokens --------------------------------------------------------------------

def b64url_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def test_sign_token_format(ex):
    token = ex.sign_token({"user": 42}, KEY, expires_at=2_000_000_000)
    assert token == "eyJleHAiOjIwMDAwMDAwMDAsInVzZXIiOjQyfQ.fu5-pmG8HrseJwhJgh2A520YS0Zb9-6nd1LvTXMtJ0k"
    payload, signature = token.split(".")
    assert "=" not in token
    assert json.loads(b64url_decode(payload)) == {"exp": 2_000_000_000, "user": 42}
    expected = hmac.new(KEY, payload.encode(), hashlib.sha256).digest()
    assert b64url_decode(signature) == expected


def test_sign_token_does_not_change_the_data(ex):
    data = {"user": 1, "role": "admin"}
    ex.sign_token(data, KEY, expires_at=10)
    assert data == {"user": 1, "role": "admin"}


def test_verify_token_roundtrip(ex):
    data = {"user": 42, "scopes": ["read", "write"], "name": "Zoë"}
    token = ex.sign_token(data, KEY, expires_at=1000)
    assert ex.verify_token(token, KEY, now=999) == data


def test_verify_token_expired(ex):
    token = ex.sign_token({"user": 42}, KEY, expires_at=1000)
    with pytest.raises(ex.InvalidToken, match="^token expired$"):
        ex.verify_token(token, KEY, now=1000)


def test_verify_token_wrong_key(ex):
    token = ex.sign_token({"user": 42}, KEY, expires_at=1000)
    with pytest.raises(ex.InvalidToken, match="^bad signature$"):
        ex.verify_token(token, b"other-key", now=0)


def test_verify_token_tampered_payload(ex):
    token = ex.sign_token({"user": 42, "role": "reader"}, KEY, expires_at=1000)
    payload, signature = token.split(".")
    forged = base64.urlsafe_b64encode(b'{"exp":1000,"role":"admin","user":42}').rstrip(b"=").decode()
    with pytest.raises(ex.InvalidToken, match="^bad signature$"):
        ex.verify_token(f"{forged}.{signature}", KEY, now=0)


def test_signature_is_checked_before_expiry(ex):
    token = ex.sign_token({"user": 42}, KEY, expires_at=1000)
    with pytest.raises(ex.InvalidToken, match="^bad signature$"):
        ex.verify_token(token, b"other-key", now=5000)


@pytest.mark.parametrize("token", ["", "nodot", ".sig", "payload.", "a.b.c", "ünï.cödé"])
def test_verify_token_malformed(ex, token):
    with pytest.raises(ex.InvalidToken):
        ex.verify_token(token, KEY, now=0)


def test_verify_token_signed_garbage_is_malformed(ex):
    payload = "bm90IGpzb24"                                  # base64url of "not json"
    signature = base64.urlsafe_b64encode(hmac.new(KEY, payload.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
    with pytest.raises(ex.InvalidToken, match="^malformed token$"):
        ex.verify_token(f"{payload}.{signature}", KEY, now=0)


# --- mask ----------------------------------------------------------------------

@pytest.mark.parametrize("secret, visible, expected", [
    ("plp_live_8f2a01bc77", 4, "***************bc77"),
    ("abcdef", 2, "****ef"),
    ("abcd", 4, "****"),
    ("abc", 4, "***"),
    ("", 4, ""),
    ("secret", 0, "******"),
])
def test_mask(ex, secret, visible, expected):
    assert ex.mask(secret, visible) == expected
