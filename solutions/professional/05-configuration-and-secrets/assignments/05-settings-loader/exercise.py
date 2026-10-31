"""Assignment 05 · Settings loader: template solution."""

import dataclasses
import hmac
import os
import re
from dataclasses import dataclass

PREFIX = "APP_"
KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
TRUE, FALSE = {"1", "true", "yes", "on"}, {"0", "false", "no", "off"}
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class Secret:
    def __init__(self, value):
        self._value = value

    def reveal(self):
        return self._value

    def __repr__(self):
        return "Secret('***')"

    def __str__(self):
        return "***"

    def __eq__(self, other):
        if not isinstance(other, Secret):
            return NotImplemented
        # Constant-time comparison: the time taken does not leak how many characters matched.
        return hmac.compare_digest(self._value.encode(), other._value.encode())

    __hash__ = None                                  # mutable-looking value with custom __eq__: unhashable


class ConfigError(ValueError):
    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("invalid configuration:\n" + "\n".join(f"  - {e}" for e in self.errors))


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: Secret
    debug: bool = False
    port: int = 8000
    log_level: str = "INFO"
    allowed_hosts: tuple = ("localhost",)


def _unquote(value, number):
    quote = value[0]
    end = value.find(quote, 1)
    if quote == "'":
        if end == -1:
            raise ValueError(f"line {number}: unterminated quote")
        return value[1:end]                          # single quotes: completely literal
    chars, i = [], 1
    while i < len(value):
        char = value[i]
        if char == "\\" and i + 1 < len(value):
            chars.append(ESCAPES.get(value[i + 1], "\\" + value[i + 1]))
            i += 2
        elif char == '"':
            return "".join(chars)
        else:
            chars.append(char)
            i += 1
    raise ValueError(f"line {number}: unterminated quote")


def parse_dotenv(text):
    values = {}
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, sep, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not KEY_RE.fullmatch(key):
            raise ValueError(f"line {number}: expected KEY=VALUE")
        if value[:1] in {'"', "'"}:
            value = _unquote(value, number)
        else:
            value = value.split(" #", 1)[0].rstrip()   # an unquoted value ends at " #"
        values[key] = value
    return values


# --- converters: string -> value, or ValueError with the reason -----------------

def _to_bool(text):
    if text.lower() in TRUE:
        return True
    if text.lower() in FALSE:
        return False
    raise ValueError(f"expected a boolean, got {text!r}")


def _to_port(text):
    try:
        port = int(text)
    except ValueError:
        raise ValueError(f"expected an integer, got {text!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"must be between 1 and 65535, got {port}")
    return port


def _to_log_level(text):
    if text.upper() not in LOG_LEVELS:
        raise ValueError(f"must be one of {', '.join(LOG_LEVELS)}, got {text!r}")
    return text.upper()


def _to_hosts(text):
    hosts = tuple(host.strip() for host in text.split(",") if host.strip())
    if not hosts:
        raise ValueError("must not be empty")
    return hosts


CONVERTERS = {
    "database_url": str,
    "secret_key": Secret,
    "debug": _to_bool,
    "port": _to_port,
    "log_level": _to_log_level,
    "allowed_hosts": _to_hosts,
}


def load_settings(*, env=None, dotenv_text=None, overrides=None):
    env = os.environ if env is None else env
    fields = [f.name for f in dataclasses.fields(Settings)]
    raw, unknown = {}, set()

    # Lowest layer first; each later layer overwrites the earlier ones.
    for source in (parse_dotenv(dotenv_text or ""), env):
        for key, value in source.items():
            if not key.startswith(PREFIX):
                continue                             # not ours: PATH, HOME, ...
            name = key[len(PREFIX):].lower()
            if name in fields:
                raw[name] = value
            else:
                unknown.add(f"unknown setting: {key}")
    for name, value in (overrides or {}).items():
        if value is None:
            continue                                 # an option that was not given
        if name in fields:
            raw[name] = value
        else:
            unknown.add(f"unknown setting: {name}")

    values, errors = {}, []
    for field in dataclasses.fields(Settings):
        variable = PREFIX + field.name.upper()
        if field.name not in raw:
            if field.default is dataclasses.MISSING:
                errors.append(f"{variable}: missing")
            continue                                 # the dataclass default applies
        try:
            values[field.name] = CONVERTERS[field.name](raw[field.name])
        except ValueError as error:
            errors.append(f"{variable}: {error}")
    errors.extend(sorted(unknown))
    if errors:
        raise ConfigError(errors)                    # every problem at once, not one per attempt
    return Settings(**values)


if __name__ == "__main__":
    dotenv = 'APP_DATABASE_URL=sqlite:///dev.db\nAPP_SECRET_KEY="dev only"\nAPP_DEBUG=true\n'
    print(load_settings(env={"APP_PORT": "9000"}, dotenv_text=dotenv))
    try:
        load_settings(env={"APP_PORT": "80OO", "APP_DEUBG": "1"})
    except ConfigError as error:
        print(error)
