# Assignment 05 · Settings loader

> **Lesson:** [05 · Configuration and secrets](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Build the settings layer of a web service: read a `.env` file, combine it with the environment and
command-line overrides, convert every value to its type, validate it, report **every** problem at once,
and keep the secret key out of logs and tracebacks.

## The settings

`Settings` is given: a frozen dataclass. Each field is set by the variable `APP_<FIELD NAME IN CAPITALS>`:

| Field | Variable | Type and rule | Default |
|---|---|---|---|
| `database_url` | `APP_DATABASE_URL` | text | **required** |
| `secret_key` | `APP_SECRET_KEY` | a `Secret` | **required** |
| `debug` | `APP_DEBUG` | boolean: `1`/`true`/`yes`/`on` or `0`/`false`/`no`/`off`, any case | `False` |
| `port` | `APP_PORT` | integer from 1 to 65535 | `8000` |
| `log_level` | `APP_LOG_LEVEL` | one of `DEBUG INFO WARNING ERROR CRITICAL`, any case, stored in capitals | `"INFO"` |
| `allowed_hosts` | `APP_ALLOWED_HOSTS` | comma-separated, stored as a tuple; spaces and empty parts removed; must not be empty | `("localhost",)` |

## What to write

| Name | Specification |
|---|---|
| `Secret(value)` | `reveal()` returns the value. `repr()` is `"Secret('***')"`, `str()` is `"***"`. Two secrets are equal if their values are, compared with `hmac.compare_digest`; a `Secret` is never equal to a plain string. Not hashable (`__hash__ = None` is given) |
| `ConfigError(errors)` | a `ValueError` with the attribute `errors` (a list of strings) and the message `"invalid configuration:"` followed by one line `"  - <error>"` per error |
| `parse_dotenv(text)` | `{KEY: value}` from the text of a `.env` file, see below |
| `load_settings(*, env=None, dotenv_text=None, overrides=None)` | builds `Settings` from the layers **defaults < `.env` < `env` < `overrides`**, see below |

### `.env` rules

- Blank lines and lines starting with `#` are skipped. An `export ` prefix is allowed.
- `KEY=VALUE`, with optional spaces around the key and value. Keys are letters, digits and `_`, not
  starting with a digit. Anything else: `ValueError("line N: expected KEY=VALUE")`.
- An **unquoted** value ends at the first ` #` (a comment) and is stripped. `KEY=` gives `""`.
- A value in **single quotes** is taken literally. A value in **double quotes** understands the escapes
  `\n`, `\t`, `\"` and `\\`. Text after the closing quote is ignored. A missing closing quote:
  `ValueError("line N: unterminated quote")`.

### Loading rules

- `env` defaults to `os.environ`. Only keys starting with `APP_` are looked at; others are ignored.
- `overrides` maps **field names** to strings (for example from command-line options); `None` values are
  skipped.
- Every value is converted by the rules in the table. Errors, collected for **all** fields, in field order:
  - `"APP_DATABASE_URL: missing"` for a required field that no layer sets;
  - `"APP_PORT: expected an integer, got 'abc'"`, `"APP_PORT: must be between 1 and 65535, got 0"`;
  - `"APP_DEBUG: expected a boolean, got 'maybe'"`;
  - `"APP_LOG_LEVEL: must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL, got 'loud'"`;
  - `"APP_ALLOWED_HOSTS: must not be empty"`.
- After those, sorted: `"unknown setting: APP_DEUBG"` for every `APP_` variable (in `.env` or `env`) and
  every override name that is not a field.
- Any error: raise `ConfigError` with all of them. Otherwise return the `Settings`.

## Examples

```python
>>> dotenv = 'APP_DATABASE_URL=sqlite:///dev.db\nAPP_SECRET_KEY="dev only"\nAPP_DEBUG=true\n'
>>> load_settings(env={"APP_PORT": "9000"}, dotenv_text=dotenv)
Settings(database_url='sqlite:///dev.db', secret_key=Secret('***'), debug=True, port=9000, log_level='INFO', allowed_hosts=('localhost',))

>>> load_settings(env={"APP_PORT": "80OO", "APP_DEUBG": "1"})
Traceback (most recent call last):
ConfigError: invalid configuration:
  - APP_DATABASE_URL: missing
  - APP_SECRET_KEY: missing
  - APP_PORT: expected an integer, got '80OO'
  - unknown setting: APP_DEUBG
```

## Hints

<details>
<summary>Hint 1: layers</summary>

Collect the raw strings first: a dict `raw = {}` that you fill from the `.env` dict, then from `env`,
then from `overrides`. Later sources simply overwrite earlier keys. Convert only at the end.
</details>

<details>
<summary>Hint 2: one converter per field</summary>

A dict `{field name: function}` where each function takes the string and returns the value or raises
`ValueError("expected a boolean, got 'maybe'")`. The loader adds the variable name in front. Loop over
`dataclasses.fields(Settings)`: `field.default is dataclasses.MISSING` tells you a field is required.
</details>

<details>
<summary>Hint 3: double quotes</summary>

Walk through the characters after the opening quote with an index. A backslash takes the next character
as an escape; a `"` ends the value; reaching the end without one is an unterminated quote.
</details>

## Check your work

```bash
pytest professional/05-configuration-and-secrets/assignments/05-settings-loader -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/05-configuration-and-secrets/assignments/05-settings-loader/exercise.py),
then tick off assignment 05 in the [progress checklist](../../../../README.md#progress-checklist).
