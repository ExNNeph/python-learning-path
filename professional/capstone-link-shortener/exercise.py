"""Capstone · Link shortener.

Work through the four milestones in the README, in order. Each milestone has its own tests:
    pytest professional/capstone-link-shortener -v -k milestone1
Try it for real (locally, the API key can be anything):
    SHORT_API_KEY=dev python professional/capstone-link-shortener/exercise.py shorten https://www.python.org
    SHORT_API_KEY=dev python professional/capstone-link-shortener/exercise.py serve
"""

from __future__ import annotations

import argparse
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import sys
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any
from urllib.parse import urlsplit, urlunsplit

log = logging.getLogger("shortener")

ALPHABET = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # no 0/O, 1/l/I
CODE_RE = re.compile(r"[A-Za-z0-9_-]{3,32}")
RESERVED_CODES = {"links", "health"}
MAX_URL_LENGTH = 2048

Environ = dict[str, Any]
Headers = list[tuple[str, str]]
WsgiApp = Callable[[Environ, Callable[..., Any]], Iterable[bytes]]


# ---------------------------------------------------------------------------
# Milestone 1 · Settings and rules
# ---------------------------------------------------------------------------

class ShortenerError(Exception):
    """Base class for every error the shortener raises on purpose."""


class InvalidInput(ShortenerError):
    pass


class NotFound(ShortenerError):
    pass


class CodeTaken(ShortenerError):
    pass


class ConfigError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = list(errors)
        super().__init__("invalid configuration:\n" + "\n".join(f"  - {e}" for e in self.errors))


@dataclass(frozen=True)
class Settings:
    api_key: str
    database: str = ":memory:"
    base_url: str = "http://localhost:8000"
    code_length: int = 6

    def __repr__(self) -> str:                    # never print the key (lesson 05)
        return (f"Settings(api_key='***', database={self.database!r}, "
                f"base_url={self.base_url!r}, code_length={self.code_length})")


def load_settings(env: Mapping[str, str]) -> Settings:
    """Settings from the SHORT_* variables in `env`; ConfigError listing every problem."""
    raise NotImplementedError


def validate_url(url: str) -> str:
    """The normalised http(s) URL, or InvalidInput."""
    raise NotImplementedError


def validate_code(code: str) -> str:
    """The code if it is a valid custom code, or InvalidInput."""
    raise NotImplementedError


def generate_code(length: int, choice: Callable[[str], str] = secrets.choice) -> str:
    """A random code of `length` characters from ALPHABET."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Milestone 2 · Storage
# ---------------------------------------------------------------------------

MIGRATIONS = [
    [
        """CREATE TABLE links (
            code       TEXT PRIMARY KEY,
            url        TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""",
    ],
    [
        """CREATE TABLE visits (
            id         INTEGER PRIMARY KEY,
            code       TEXT NOT NULL REFERENCES links(code),
            visited_at TEXT NOT NULL
        )""",
        "CREATE INDEX visits_code ON visits(code)",
    ],
]


@dataclass(frozen=True)
class Link:
    code: str
    url: str
    created_at: str
    clicks: int = 0


def connect(path: str = ":memory:") -> sqlite3.Connection:
    """Open the database (check_same_thread=False), turn foreign keys on, apply MIGRATIONS."""
    raise NotImplementedError


class LinkRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, code: str, url: str, created_at: str) -> Link:
        raise NotImplementedError

    def get(self, code: str) -> Link | None:
        raise NotImplementedError

    def record_visit(self, code: str, at: str) -> None:
        raise NotImplementedError

    def last_visit(self, code: str) -> str | None:
        raise NotImplementedError

    def recent(self, limit: int = 10) -> list[Link]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Milestone 3 · The service
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ShortenerService:
    def __init__(self, repo: LinkRepository, *, base_url: str, code_length: int = 6,
                 clock: Callable[[], datetime] = utc_now,
                 make_code: Callable[[int], str] = generate_code) -> None:
        raise NotImplementedError

    def short_url(self, code: str) -> str:
        raise NotImplementedError

    def shorten(self, url: str, code: str | None = None) -> Link:
        raise NotImplementedError

    def resolve(self, code: str) -> str:
        raise NotImplementedError

    def stats(self, code: str) -> dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Milestone 4 · The web API and the command line
# ---------------------------------------------------------------------------

def create_app(service: ShortenerService, api_key: str) -> WsgiApp:
    """Return the WSGI application."""
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shortener", description="A small link shortener.")
    commands = parser.add_subparsers(dest="command", required=True)
    shorten = commands.add_parser("shorten", help="create a short link")
    shorten.add_argument("url")
    shorten.add_argument("--code", help="a custom code instead of a random one")
    stats = commands.add_parser("stats", help="show the statistics of a link")
    stats.add_argument("code")
    commands.add_parser("recent", help="list the newest links")
    serve = commands.add_parser("serve", help="run the web API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def _wsgiref_serve(app: WsgiApp, host: str, port: int) -> None:
    from wsgiref.simple_server import make_server

    print(f"serving on http://{host}:{port}  (Ctrl+C to stop)")
    make_server(host, port, app).serve_forever()


def main(argv: list[str] | None = None, *, env: Mapping[str, str] | None = None,
         serve: Callable[[WsgiApp, str, int], None] = _wsgiref_serve) -> int:
    """Run one command; return the exit code."""
    raise NotImplementedError


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    sys.exit(main())
