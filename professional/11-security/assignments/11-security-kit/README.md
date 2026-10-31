# Assignment 11 · Security kit

> **Lesson:** [11 · Security](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Build the small security primitives that every web service needs, with the standard library only: a file
path helper that cannot be tricked into leaving its folder, password hashing that is salted, slow,
upgradeable and compared in constant time, signed tokens that expire, and a helper that keeps secrets
readable enough for logs without revealing them.

## What to write

| Name | Specification |
|---|---|
| `safe_join(base, *parts)` | joins `base` and `parts`, **resolves** the result (removing `..` and following symbolic links) and returns it as a `Path` if it is inside the resolved `base` (the base itself counts as inside). Otherwise raise `ValueError("path escapes the base directory")`. Absolute parts like `"/etc/passwd"` must be caught too |
| `hash_password(password, *, iterations=600_000, salt=None)` | PBKDF2-HMAC-SHA256 (`hashlib.pbkdf2_hmac`) of the UTF-8 password. The salt is `secrets.token_bytes(16)` unless given. Returns `"pbkdf2_sha256$<iterations>$<salt>$<hash>"`, salt and hash in standard base64 (`base64.b64encode`) |
| `verify_password(password, stored)` | recomputes the hash with the stored salt and iterations and compares with `hmac.compare_digest`. Returns `True` or `False`; a malformed `stored` string (wrong number of parts, other algorithm, bad number, bad base64) gives `False`, never an exception |
| `needs_rehash(stored, iterations=600_000)` | `True` if `stored` is malformed, uses another algorithm, or fewer than `iterations` iterations |
| `sign_token(data, key, *, expires_at)` | the payload is the JSON of `data` plus `"exp": expires_at` (`sort_keys=True`, separators `(",", ":")`), base64url-encoded **without** `=` padding. The signature is the HMAC-SHA256 of the payload text with `key` (bytes), base64url without padding. Returns `"<payload>.<signature>"` |
| `verify_token(token, key, *, now)` | checks the token and returns the data **without** `"exp"`. Raise `InvalidToken` with the message `"malformed token"` (no `.`, an empty part, a payload that is not valid base64url JSON), `"bad signature"` (checked **before** reading the payload, with `hmac.compare_digest`), or `"token expired"` (when `now >= exp`) |
| `mask(secret, visible=4)` | stars for all but the last `visible` characters; a secret with at most `visible` characters becomes all stars |

`InvalidToken`, `ALGORITHM` and `DEFAULT_ITERATIONS` are given.

## Examples

```python
>>> safe_join("/srv/uploads", "ada", "cv.pdf")
PosixPath('/srv/uploads/ada/cv.pdf')
>>> safe_join("/srv/uploads", "../../etc/passwd")
Traceback (most recent call last):
ValueError: path escapes the base directory

>>> stored = hash_password("correct horse battery staple")
>>> stored
'pbkdf2_sha256$600000$uCMrtbIdQMHPxF/hlZIwLg==$DFXYrflxNKT2ioseaSrO9+jkN61tQr2P0wKpCM3Wxqc='
>>> verify_password("correct horse battery staple", stored), verify_password("Tr0ub4dor&3", stored)
(True, False)
>>> needs_rehash(stored), needs_rehash(stored, iterations=1_000_000)
(False, True)

>>> token = sign_token({"user": 42}, b"server-secret", expires_at=2_000_000_000)
>>> token
'eyJleHAiOjIwMDAwMDAwMDAsInVzZXIiOjQyfQ.fu5-pmG8HrseJwhJgh2A520YS0Zb9-6nd1LvTXMtJ0k'
>>> verify_token(token, b"server-secret", now=1_800_000_000)
{'user': 42}
>>> verify_token(token, b"wrong-key", now=1_800_000_000)
Traceback (most recent call last):
InvalidToken: bad signature

>>> mask("plp_live_8f2a01bc77")
'***************bc77'
```

(The salt is random, so your hash looks different every time. That is the point.)

## Hints

<details>
<summary>Hint 1: safe_join</summary>

`root = Path(base).resolve()` and `target = root.joinpath(*parts).resolve()`; then
`target.is_relative_to(root)`. Resolving the base too matters: on macOS `/tmp` is a link to `/private/tmp`.
</details>

<details>
<summary>Hint 2: parsing a stored hash</summary>

`algorithm, iterations, salt, digest = stored.split("$")` raises `ValueError` for the wrong number of
parts, `int()` for a bad number, `base64.b64decode(..., validate=True)` raises `binascii.Error` (a
`ValueError` subclass) for bad base64. One helper that returns `None` for anything malformed serves both
`verify_password` and `needs_rehash`.
</details>

<details>
<summary>Hint 3: base64url without padding</summary>

`base64.urlsafe_b64encode(data).rstrip(b"=").decode()`. To decode, add the padding back:
`base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))`. Compare signatures as bytes
(`.encode()`): `compare_digest` refuses strings with non-ASCII characters.
</details>

## Check your work

```bash
pytest professional/11-security/assignments/11-security-kit -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/11-security/assignments/11-security-kit/exercise.py),
then tick off assignment 11 in the [progress checklist](../../../../README.md#progress-checklist).
