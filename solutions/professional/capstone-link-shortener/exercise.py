"""Capstone · Link shortener: template solution.

One file, four layers, as in lesson 10: settings and rules (milestone 1), the SQLite repository
(milestone 2), the service (milestone 3), and two adapters on the outside, a JSON web API and a
command line (milestone 4).
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
    errors = []
    values: dict[str, object] = {}
    if env.get("SHORT_API_KEY"):
        values["api_key"] = env["SHORT_API_KEY"]
    else:
        errors.append("SHORT_API_KEY: missing")
    if "SHORT_DATABASE" in env:
        values["database"] = env["SHORT_DATABASE"]
    if "SHORT_BASE_URL" in env:
        base_url = env["SHORT_BASE_URL"].rstrip("/")
        if urlsplit(base_url).scheme not in ("http", "https") or not urlsplit(base_url).netloc:
            errors.append(f"SHORT_BASE_URL: expected an http(s) URL, got {env['SHORT_BASE_URL']!r}")
        values["base_url"] = base_url
    if "SHORT_CODE_LENGTH" in env:
        text = env["SHORT_CODE_LENGTH"]
        if not text.isdigit() or not 4 <= int(text) <= 32:
            errors.append(f"SHORT_CODE_LENGTH: expected a number from 4 to 32, got {text!r}")
        else:
            values["code_length"] = int(text)
    if errors:
        raise ConfigError(errors)
    return Settings(**values)  # type: ignore[arg-type]


def validate_url(url: str) -> str:
    url = url.strip()
    if not url or len(url) > MAX_URL_LENGTH or any(c.isspace() for c in url):
        raise InvalidInput("invalid URL")
    try:
        parts = urlsplit(url)
        parts.port                                  # raises ValueError for a port like :99999 or :abc
    except ValueError:
        raise InvalidInput("invalid URL") from None
    if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
        raise InvalidInput("only http and https URLs with a host can be shortened")
    # Scheme and host are case-insensitive: normalise them. The path is not.
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, parts.fragment))


def validate_code(code: str) -> str:
    if not CODE_RE.fullmatch(code) or code.lower() in RESERVED_CODES:
        raise InvalidInput(f"invalid code: {code!r}")
    return code


def generate_code(length: int, choice: Callable[[str], str] = secrets.choice) -> str:
    return "".join(choice(ALPHABET) for _ in range(length))


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
    conn = sqlite3.connect(path, check_same_thread=False)   # the web server may use another thread
    conn.execute("PRAGMA foreign_keys = ON")
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    for number, statements in enumerate(MIGRATIONS, start=1):
        if number <= version:
            continue
        conn.execute("BEGIN")
        try:
            for statement in statements:
                conn.execute(statement)
            conn.execute(f"PRAGMA user_version = {number}")
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
    return conn


class LinkRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, code: str, url: str, created_at: str) -> Link:
        try:
            with self.conn:
                self.conn.execute("INSERT INTO links (code, url, created_at) VALUES (?, ?, ?)",
                                  (code, url, created_at))
        except sqlite3.IntegrityError as error:
            raise CodeTaken(f"code already taken: {code}") from error
        return Link(code, url, created_at)

    def get(self, code: str) -> Link | None:
        row = self.conn.execute(
            """SELECT links.code, links.url, links.created_at, COUNT(visits.id)
               FROM links LEFT JOIN visits ON visits.code = links.code
               WHERE links.code = ?
               GROUP BY links.code""",
            (code,),
        ).fetchone()
        return Link(*row) if row else None

    def record_visit(self, code: str, at: str) -> None:
        with self.conn:
            self.conn.execute("INSERT INTO visits (code, visited_at) VALUES (?, ?)", (code, at))

    def last_visit(self, code: str) -> str | None:
        last: str | None = self.conn.execute(
            "SELECT MAX(visited_at) FROM visits WHERE code = ?", (code,)).fetchone()[0]
        return last

    def recent(self, limit: int = 10) -> list[Link]:
        rows = self.conn.execute(
            """SELECT links.code, links.url, links.created_at, COUNT(visits.id)
               FROM links LEFT JOIN visits ON visits.code = links.code
               GROUP BY links.code
               ORDER BY links.created_at DESC, links.code
               LIMIT ?""",
            (limit,),
        )
        return [Link(*row) for row in rows]


# ---------------------------------------------------------------------------
# Milestone 3 · The service
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ShortenerService:
    def __init__(self, repo: LinkRepository, *, base_url: str, code_length: int = 6,
                 clock: Callable[[], datetime] = utc_now,
                 make_code: Callable[[int], str] = generate_code) -> None:
        self.repo = repo
        self.base_url = base_url.rstrip("/")
        self.code_length = code_length
        self.clock = clock
        self.make_code = make_code

    def _now(self) -> str:
        return self.clock().isoformat(timespec="seconds")

    def short_url(self, code: str) -> str:
        return f"{self.base_url}/{code}"

    def shorten(self, url: str, code: str | None = None) -> Link:
        url = validate_url(url)
        if code is not None:
            return self.repo.add(validate_code(code), url, self._now())
        for _ in range(5):
            try:
                return self.repo.add(self.make_code(self.code_length), url, self._now())
            except CodeTaken:
                continue                         # a collision: rare, so simply try another code
        raise ShortenerError("could not find a free code")

    def resolve(self, code: str) -> str:
        link = self.repo.get(code)
        if link is None:
            raise NotFound(f"no link with code {code!r}")
        self.repo.record_visit(code, self._now())
        return link.url

    def stats(self, code: str) -> dict[str, Any]:
        link = self.repo.get(code)
        if link is None:
            raise NotFound(f"no link with code {code!r}")
        return {
            "code": link.code,
            "url": link.url,
            "short_url": self.short_url(link.code),
            "created_at": link.created_at,
            "clicks": link.clicks,
            "last_visit": self.repo.last_visit(code),
        }


# ---------------------------------------------------------------------------
# Milestone 4 · The web API and the command line
# ---------------------------------------------------------------------------

STATS_RE = re.compile(r"/links/([A-Za-z0-9_-]+)/stats")
REDIRECT_RE = re.compile(r"/([A-Za-z0-9_-]+)")


class HttpError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


def _json_response(status: int, data: Any, headers: Iterable[tuple[str, str]] = ()) -> tuple[int, Headers, bytes]:
    body = json.dumps(data).encode()
    return status, [("Content-Type", "application/json; charset=utf-8"), *headers], body


def create_app(service: ShortenerService, api_key: str) -> WsgiApp:
    def check_key(environ: Environ) -> None:
        given = environ.get("HTTP_X_API_KEY", "")
        if not hmac.compare_digest(given.encode(), api_key.encode()):
            raise HttpError(401, "missing or wrong API key")

    def read_json(environ: Environ) -> Any:
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            return json.loads(environ["wsgi.input"].read(length) if length > 0 else b"")
        except ValueError:
            raise HttpError(400, "invalid JSON") from None

    def route(environ: Environ) -> tuple[int, Headers, bytes]:
        method, path = environ["REQUEST_METHOD"], environ.get("PATH_INFO") or "/"
        if path == "/health":
            return _json_response(200, {"status": "ok"})
        if path == "/links":
            if method != "POST":
                return _json_response(405, {"error": "method not allowed"}, [("Allow", "POST")])
            check_key(environ)
            data = read_json(environ)
            if not isinstance(data, dict) or not isinstance(data.get("url"), str):
                raise HttpError(422, "url is required")
            code = data.get("code")
            if code is not None and not isinstance(code, str):
                raise HttpError(422, "code must be a string")
            link = service.shorten(data["url"], code)
            return _json_response(201, {"code": link.code, "url": link.url,
                                        "short_url": service.short_url(link.code)},
                                  [("Location", service.short_url(link.code))])
        if match := STATS_RE.fullmatch(path):
            check_key(environ)
            return _json_response(200, service.stats(match.group(1)))
        if (match := REDIRECT_RE.fullmatch(path)) and method in ("GET", "HEAD"):
            url = service.resolve(match.group(1))
            return 302, [("Location", url)], b""
        raise HttpError(404, "not found")

    def app(environ: Environ, start_response: Callable[..., Any]) -> list[bytes]:
        start = time.perf_counter()
        try:
            status, headers, body = route(environ)
        except HttpError as error:
            status, headers, body = _json_response(error.status, {"error": str(error)})
        except NotFound as error:
            status, headers, body = _json_response(404, {"error": str(error)})
        except InvalidInput as error:
            status, headers, body = _json_response(422, {"error": str(error)})
        except CodeTaken as error:
            status, headers, body = _json_response(409, {"error": str(error)})
        except Exception:
            log.exception("unhandled error")
            status, headers, body = _json_response(500, {"error": "internal server error"})
        start_response(f"{status} {HTTPStatus(status).phrase}", [*headers, ("Content-Length", str(len(body)))])
        log.info("%s %s %d %.1fms", environ["REQUEST_METHOD"], environ.get("PATH_INFO"), status,
                 (time.perf_counter() - start) * 1000)
        return [body]

    return app


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
    args = build_parser().parse_args(argv)
    try:
        settings = load_settings(dict(os.environ if env is None else env))
    except ConfigError as error:
        print(f"shortener: {error}", file=sys.stderr)
        return 2
    conn = connect(settings.database)
    service = ShortenerService(LinkRepository(conn), base_url=settings.base_url, code_length=settings.code_length)
    try:
        if args.command == "shorten":
            print(service.short_url(service.shorten(args.url, args.code).code))
        elif args.command == "stats":
            for key, value in service.stats(args.code).items():
                print(f"{key + ':':<12}{'-' if value is None else value}")
        elif args.command == "recent":
            for link in service.repo.recent():
                print(f"{link.code:<10}{link.clicks:>6}  {link.url}")
        elif args.command == "serve":
            serve(create_app(service, settings.api_key), args.host, args.port)
        return 0
    except ShortenerError as error:
        print(f"shortener: error: {error}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    sys.exit(main())
