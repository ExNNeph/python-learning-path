"""Assignment 05 · Settings loader.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest professional/05-configuration-and-secrets/assignments/05-settings-loader -v
"""

import dataclasses
import hmac
import os
import re
from dataclasses import dataclass

PREFIX = "APP_"
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class Secret:
    """Holds a secret value; shows '***' everywhere except through reveal()."""

    def __init__(self, value):
        raise NotImplementedError

    def reveal(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    __hash__ = None


class ConfigError(ValueError):
    """Raised with the list of ALL configuration problems."""

    def __init__(self, errors):
        raise NotImplementedError


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: Secret
    debug: bool = False
    port: int = 8000
    log_level: str = "INFO"
    allowed_hosts: tuple = ("localhost",)


def parse_dotenv(text):
    """Parse the text of a .env file into {KEY: value}."""
    raise NotImplementedError


def load_settings(*, env=None, dotenv_text=None, overrides=None):
    """Defaults < .env < environment < overrides, converted and validated into Settings."""
    raise NotImplementedError


if __name__ == "__main__":
    dotenv = 'APP_DATABASE_URL=sqlite:///dev.db\nAPP_SECRET_KEY="dev only"\nAPP_DEBUG=true\n'
    print(load_settings(env={"APP_PORT": "9000"}, dotenv_text=dotenv))
    try:
        load_settings(env={"APP_PORT": "80OO", "APP_DEUBG": "1"})
    except ConfigError as error:
        print(error)
