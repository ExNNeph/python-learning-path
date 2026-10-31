"""Tests for assignment 05. Run: pytest professional/05-configuration-and-secrets/assignments/05-settings-loader -v"""

import dataclasses

import pytest

REQUIRED = {"APP_DATABASE_URL": "sqlite:///app.db", "APP_SECRET_KEY": "k3y"}


def errors_of(ex, **kwargs):
    with pytest.raises(ex.ConfigError) as info:
        ex.load_settings(**kwargs)
    return info.value.errors


# --- Secret --------------------------------------------------------------------

def test_secret_hides_its_value(ex):
    secret = ex.Secret("s3cr3t")
    assert secret.reveal() == "s3cr3t"
    assert repr(secret) == "Secret('***')"
    assert str(secret) == f"{secret}" == "***"
    assert "s3cr3t" not in repr([secret, {"key": secret}])


def test_secret_equality(ex, monkeypatch):
    calls = []
    real = ex.hmac.compare_digest
    monkeypatch.setattr(ex.hmac, "compare_digest", lambda a, b: (calls.append(1), real(a, b))[1])
    assert ex.Secret("a") == ex.Secret("a")
    assert ex.Secret("a") != ex.Secret("b")
    assert calls, "compare secrets with hmac.compare_digest"
    assert ex.Secret("a") != "a"
    with pytest.raises(TypeError):
        hash(ex.Secret("a"))


def test_secret_in_a_traceback(ex):
    settings = ex.load_settings(env=REQUIRED)
    assert "k3y" not in repr(settings)


# --- ConfigError ---------------------------------------------------------------

def test_config_error(ex):
    error = ex.ConfigError(["a: missing", "b: bad"])
    assert isinstance(error, ValueError)
    assert error.errors == ["a: missing", "b: bad"]
    assert str(error) == "invalid configuration:\n  - a: missing\n  - b: bad"


# --- parse_dotenv --------------------------------------------------------------

def test_dotenv_basics(ex):
    text = """
# database
APP_DATABASE_URL=sqlite:///dev.db
  APP_DEBUG = true
export APP_PORT=9000
APP_EMPTY=
APP_HOSTS=a.com,b.com   # two hosts
APP_URL=http://x.com/#anchor
"""
    assert ex.parse_dotenv(text) == {
        "APP_DATABASE_URL": "sqlite:///dev.db",
        "APP_DEBUG": "true",
        "APP_PORT": "9000",
        "APP_EMPTY": "",
        "APP_HOSTS": "a.com,b.com",
        "APP_URL": "http://x.com/#anchor",
    }


def test_dotenv_quotes(ex):
    text = r"""
A='literal \n # not a comment'
B="line1\nline2\ttab \"quoted\" back\\slash"
C="has # hash"  # comment
D=""
E='it''s'
"""
    assert ex.parse_dotenv(text) == {
        "A": r"literal \n # not a comment",
        "B": 'line1\nline2\ttab "quoted" back\\slash',
        "C": "has # hash",
        "D": "",
        "E": "it",
    }


def test_dotenv_later_lines_win(ex):
    assert ex.parse_dotenv("X=1\nX=2\n") == {"X": "2"}


def test_dotenv_empty(ex):
    assert ex.parse_dotenv("") == {}


@pytest.mark.parametrize("text, message", [
    ("A=1\nnot a pair\n", "line 2: expected KEY=VALUE"),
    ("1ABC=x", "line 1: expected KEY=VALUE"),
    ("MY-KEY=x", "line 1: expected KEY=VALUE"),
    ("=x", "line 1: expected KEY=VALUE"),
    ('\n\nA="open', "line 3: unterminated quote"),
    ("A='open", "line 1: unterminated quote"),
    ('A="ends with escape\\"', "line 1: unterminated quote"),
])
def test_dotenv_errors(ex, text, message):
    with pytest.raises(ValueError, match=f"^{message}$"):
        ex.parse_dotenv(text)


# --- load_settings: happy paths -----------------------------------------------

def test_defaults(ex):
    settings = ex.load_settings(env=REQUIRED)
    assert settings == ex.Settings(database_url="sqlite:///app.db", secret_key=ex.Secret("k3y"))
    assert (settings.debug, settings.port, settings.log_level, settings.allowed_hosts) == (
        False, 8000, "INFO", ("localhost",))
    assert isinstance(settings.secret_key, ex.Secret)
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.port = 1


def test_conversions(ex):
    env = dict(REQUIRED, APP_DEBUG="Yes", APP_PORT="9000", APP_LOG_LEVEL="debug",
               APP_ALLOWED_HOSTS=" a.com, ,b.com ,")
    settings = ex.load_settings(env=env)
    assert settings.debug is True
    assert settings.port == 9000
    assert settings.log_level == "DEBUG"
    assert settings.allowed_hosts == ("a.com", "b.com")


@pytest.mark.parametrize("text, expected", [
    ("1", True), ("TRUE", True), ("on", True), ("yes", True),
    ("0", False), ("False", False), ("OFF", False), ("no", False),
])
def test_booleans(ex, text, expected):
    assert ex.load_settings(env=dict(REQUIRED, APP_DEBUG=text)).debug is expected


def test_layers(ex):
    dotenv = "APP_DATABASE_URL=from-dotenv\nAPP_SECRET_KEY=dotenv-key\nAPP_PORT=7000\nAPP_DEBUG=true\n"
    env = {"APP_PORT": "9000", "APP_LOG_LEVEL": "warning", "PATH": "/usr/bin", "HOME": "/home/ada"}
    overrides = {"port": "9100", "log_level": None}
    settings = ex.load_settings(env=env, dotenv_text=dotenv, overrides=overrides)
    assert settings.database_url == "from-dotenv"      # only in .env
    assert settings.debug is True                      # only in .env
    assert settings.port == 9100                       # .env < env < overrides
    assert settings.log_level == "WARNING"             # override None is skipped
    assert settings.secret_key.reveal() == "dotenv-key"


def test_env_defaults_to_os_environ(ex, monkeypatch):
    for key, value in REQUIRED.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("APP_PORT", "1234")
    assert ex.load_settings().port == 1234


# --- load_settings: errors -----------------------------------------------------

def test_everything_missing(ex):
    assert errors_of(ex, env={}) == ["APP_DATABASE_URL: missing", "APP_SECRET_KEY: missing"]


def test_all_errors_at_once_in_field_order(ex):
    env = {"APP_LOG_LEVEL": "loud", "APP_PORT": "abc", "APP_DEBUG": "maybe", "APP_ALLOWED_HOSTS": " , ",
           "APP_SECRET_KEY": "x"}
    assert errors_of(ex, env=env) == [
        "APP_DATABASE_URL: missing",
        "APP_DEBUG: expected a boolean, got 'maybe'",
        "APP_PORT: expected an integer, got 'abc'",
        "APP_LOG_LEVEL: must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL, got 'loud'",
        "APP_ALLOWED_HOSTS: must not be empty",
    ]


@pytest.mark.parametrize("port, message", [
    ("0", "APP_PORT: must be between 1 and 65535, got 0"),
    ("65536", "APP_PORT: must be between 1 and 65535, got 65536"),
    ("80OO", "APP_PORT: expected an integer, got '80OO'"),
    ("", "APP_PORT: expected an integer, got ''"),
])
def test_port_errors(ex, port, message):
    assert errors_of(ex, env=dict(REQUIRED, APP_PORT=port)) == [message]


def test_port_boundaries_are_valid(ex):
    assert ex.load_settings(env=dict(REQUIRED, APP_PORT="1")).port == 1
    assert ex.load_settings(env=dict(REQUIRED, APP_PORT="65535")).port == 65535


def test_unknown_settings_come_last_sorted(ex):
    env = dict(REQUIRED, APP_DEUBG="1", APP_PORT="x")
    errors = errors_of(ex, env=env, dotenv_text="APP_COLOUR=red\n", overrides={"verbose": "1", "port": None})
    assert errors == [
        "APP_PORT: expected an integer, got 'x'",
        "unknown setting: APP_COLOUR",
        "unknown setting: APP_DEUBG",
        "unknown setting: verbose",
    ]


def test_config_error_message(ex):
    with pytest.raises(ex.ConfigError, match=r"^invalid configuration:\n  - APP_DATABASE_URL: missing$"):
        ex.load_settings(env={"APP_SECRET_KEY": "x"})


def test_bad_dotenv_raises_value_error(ex):
    with pytest.raises(ValueError, match="line 1"):
        ex.load_settings(env=REQUIRED, dotenv_text="oops\n")
