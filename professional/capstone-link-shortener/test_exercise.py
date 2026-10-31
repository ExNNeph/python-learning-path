"""Tests for the Professional capstone. Run one milestone at a time:

    pytest professional/capstone-link-shortener -v -k milestone1
"""

import dataclasses
import inspect
import io
import json
import logging
import secrets
import sqlite3
import threading
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from wsgiref.simple_server import WSGIRequestHandler, make_server
from wsgiref.util import setup_testing_defaults

import pytest

KEY = "test-key"


class FakeClock:
    def __init__(self):
        self.now = datetime(2026, 11, 1, 9, 30, tzinfo=timezone.utc)

    def __call__(self):
        return self.now

    def advance(self, **delta):
        self.now += timedelta(**delta)


def codes(*values):
    """A make_code replacement that returns the given codes in order."""
    queue = list(values)
    return lambda length: queue.pop(0)


@pytest.fixture
def conn(ex):
    connection = ex.connect()
    yield connection
    connection.close()


@pytest.fixture
def repo(ex, conn):
    return ex.LinkRepository(conn)


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def service(ex, repo, clock):
    return ex.ShortenerService(repo, base_url="https://sho.rt/", clock=clock,
                               make_code=codes("abc123", "def456", "ghi789", "jkl012"))


# ===========================================================================
# Milestone 1 · Settings and rules
# ===========================================================================

def test_milestone1_settings_defaults(ex):
    settings = ex.load_settings({"SHORT_API_KEY": "s3cr3t", "PATH": "/usr/bin"})
    assert settings == ex.Settings(api_key="s3cr3t")
    assert (settings.database, settings.base_url, settings.code_length) == (":memory:", "http://localhost:8000", 6)
    assert "s3cr3t" not in repr(settings)


def test_milestone1_settings_from_env(ex):
    settings = ex.load_settings({
        "SHORT_API_KEY": "k", "SHORT_DATABASE": "/data/links.db",
        "SHORT_BASE_URL": "https://sho.rt/", "SHORT_CODE_LENGTH": "8",
    })
    assert settings == ex.Settings(api_key="k", database="/data/links.db", base_url="https://sho.rt", code_length=8)


def test_milestone1_settings_all_errors(ex):
    with pytest.raises(ex.ConfigError) as info:
        ex.load_settings({"SHORT_BASE_URL": "sho.rt", "SHORT_CODE_LENGTH": "3"})
    assert info.value.errors == [
        "SHORT_API_KEY: missing",
        "SHORT_BASE_URL: expected an http(s) URL, got 'sho.rt'",
        "SHORT_CODE_LENGTH: expected a number from 4 to 32, got '3'",
    ]
    assert isinstance(info.value, ValueError)


@pytest.mark.parametrize("length", ["33", "abc", "", "-5"])
def test_milestone1_settings_bad_code_length(ex, length):
    with pytest.raises(ex.ConfigError):
        ex.load_settings({"SHORT_API_KEY": "k", "SHORT_CODE_LENGTH": length})


@pytest.mark.parametrize("url, expected", [
    ("https://www.python.org", "https://www.python.org"),
    ("HTTPS://Example.COM/Docs?Q=1#Top", "https://example.com/Docs?Q=1#Top"),
    ("  http://localhost:8000/x  ", "http://localhost:8000/x"),
])
def test_milestone1_validate_url(ex, url, expected):
    assert ex.validate_url(url) == expected


@pytest.mark.parametrize("url", [
    "", "python.org", "ftp://files.example.com/a", "javascript:alert(1)", "https://", "http:///path",
    "https://exa mple.com", "https://example.com:99999/", "https://example.com/" + "a" * 2048,
])
def test_milestone1_validate_url_rejects(ex, url):
    with pytest.raises(ex.InvalidInput):
        ex.validate_url(url)


def test_milestone1_validate_code(ex):
    for code in ["abc", "My-Link_2", "x" * 32]:
        assert ex.validate_code(code) == code
    for code in ["ab", "x" * 33, "with space", "ümlaut", "a/b", "links", "Health", ""]:
        with pytest.raises(ex.InvalidInput):
            ex.validate_code(code)


def test_milestone1_errors_hierarchy(ex):
    for cls in (ex.InvalidInput, ex.NotFound, ex.CodeTaken):
        assert issubclass(cls, ex.ShortenerError)


def test_milestone1_generate_code(ex):
    code = ex.generate_code(8)
    assert len(code) == 8 and set(code) <= set(ex.ALPHABET)
    assert len({ex.generate_code(8) for _ in range(50)}) == 50
    assert ex.generate_code(5, choice=lambda alphabet: alphabet[0]) == ex.ALPHABET[0] * 5


def test_milestone1_generate_code_uses_secrets_by_default(ex):
    default = inspect.signature(ex.generate_code).parameters["choice"].default
    assert default is secrets.choice, "codes must be unguessable: use secrets.choice, not random"


# ===========================================================================
# Milestone 2 · Storage
# ===========================================================================

def test_milestone2_connect_migrates(ex, conn):
    assert conn.execute("PRAGMA user_version").fetchone()[0] == len(ex.MIGRATIONS) == 2
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"links", "visits"} <= tables


def test_milestone2_connect_file_twice(ex, tmp_path):
    path = str(tmp_path / "links.db")
    first = ex.connect(path)
    ex.LinkRepository(first).add("abc", "https://a.com", "2026-11-01T09:30:00+00:00")
    first.close()
    second = ex.connect(path)                          # migrations do not run again
    assert ex.LinkRepository(second).get("abc").url == "https://a.com"
    second.close()


def test_milestone2_add_and_get(ex, repo):
    link = repo.add("abc", "https://a.com", "2026-11-01T09:30:00+00:00")
    assert link == ex.Link("abc", "https://a.com", "2026-11-01T09:30:00+00:00", 0)
    assert repo.get("abc") == link
    assert repo.get("nope") is None
    with pytest.raises(dataclasses.FrozenInstanceError):
        link.url = "x"


def test_milestone2_code_taken(ex, repo):
    repo.add("abc", "https://a.com", "t1")
    with pytest.raises(ex.CodeTaken) as info:
        repo.add("abc", "https://b.com", "t2")
    assert isinstance(info.value.__cause__, sqlite3.IntegrityError)
    assert repo.get("abc").url == "https://a.com"


def test_milestone2_visits(ex, repo):
    repo.add("abc", "https://a.com", "t0")
    repo.add("xyz", "https://x.com", "t0")
    assert repo.last_visit("abc") is None
    repo.record_visit("abc", "2026-11-01T10:00:00+00:00")
    repo.record_visit("abc", "2026-11-02T08:00:00+00:00")
    repo.record_visit("xyz", "2026-11-03T08:00:00+00:00")
    assert repo.get("abc").clicks == 2
    assert repo.last_visit("abc") == "2026-11-02T08:00:00+00:00"


def test_milestone2_visit_needs_an_existing_link(ex, repo):
    with pytest.raises(sqlite3.IntegrityError):
        repo.record_visit("ghost", "t")


def test_milestone2_recent(ex, repo):
    repo.add("old", "https://o.com", "2026-10-01T00:00:00+00:00")
    repo.add("new", "https://n.com", "2026-11-01T00:00:00+00:00")
    repo.add("mid", "https://m.com", "2026-10-15T00:00:00+00:00")
    repo.record_visit("mid", "2026-10-16T00:00:00+00:00")
    assert [(l.code, l.clicks) for l in repo.recent()] == [("new", 0), ("mid", 1), ("old", 0)]
    assert [l.code for l in repo.recent(limit=2)] == ["new", "mid"]


def test_milestone2_injection_safe(ex, repo):
    repo.add("abc", "https://a.com/?q=' OR 1=1 --", "t")
    assert repo.get("abc").url == "https://a.com/?q=' OR 1=1 --"
    assert repo.get("x' OR '1'='1") is None


# ===========================================================================
# Milestone 3 · The service
# ===========================================================================

def test_milestone3_shorten_with_generated_code(ex, service):
    link = service.shorten("HTTPS://Python.org/downloads")
    assert link == ex.Link("abc123", "https://python.org/downloads", "2026-11-01T09:30:00+00:00", 0)
    assert service.short_url(link.code) == "https://sho.rt/abc123"


def test_milestone3_shorten_with_custom_code(ex, service):
    assert service.shorten("https://a.com", "my-link").code == "my-link"
    with pytest.raises(ex.CodeTaken):
        service.shorten("https://b.com", "my-link")
    with pytest.raises(ex.InvalidInput):
        service.shorten("https://b.com", "no")


def test_milestone3_shorten_rejects_bad_urls_before_storing(ex, service, repo):
    with pytest.raises(ex.InvalidInput):
        service.shorten("ftp://x.com")
    assert repo.recent() == []


def test_milestone3_collisions_are_retried(ex, repo, clock):
    repo.add("taken1", "https://x.com", "t")
    repo.add("taken2", "https://x.com", "t")
    service = ex.ShortenerService(repo, base_url="https://sho.rt", clock=clock,
                                  make_code=codes("taken1", "taken2", "free99"))
    assert service.shorten("https://a.com").code == "free99"


def test_milestone3_gives_up_after_five_collisions(ex, repo, clock):
    repo.add("same", "https://x.com", "t")
    service = ex.ShortenerService(repo, base_url="https://sho.rt", clock=clock, make_code=lambda n: "same")
    with pytest.raises(ex.ShortenerError, match="could not find a free code"):
        service.shorten("https://a.com")


def test_milestone3_code_length_is_passed(ex, repo, clock):
    lengths = []
    service = ex.ShortenerService(repo, base_url="https://sho.rt", code_length=9, clock=clock,
                                  make_code=lambda n: (lengths.append(n), "abcdefghi")[1])
    service.shorten("https://a.com")
    assert lengths == [9]


def test_milestone3_default_code_generator(ex, repo):
    service = ex.ShortenerService(repo, base_url="https://sho.rt")
    link = service.shorten("https://a.com")
    assert len(link.code) == 6 and set(link.code) <= set(ex.ALPHABET)
    created = datetime.fromisoformat(link.created_at)
    assert created.tzinfo is not None and abs(datetime.now(timezone.utc) - created) < timedelta(minutes=1)


def test_milestone3_resolve_records_visits(ex, service, clock):
    service.shorten("https://a.com")
    clock.advance(hours=1)
    assert service.resolve("abc123") == "https://a.com"
    clock.advance(hours=1)
    service.resolve("abc123")
    stats = service.stats("abc123")
    assert stats == {
        "code": "abc123",
        "url": "https://a.com",
        "short_url": "https://sho.rt/abc123",
        "created_at": "2026-11-01T09:30:00+00:00",
        "clicks": 2,
        "last_visit": "2026-11-01T11:30:00+00:00",
    }


def test_milestone3_stats_do_not_count_as_visits(ex, service):
    service.shorten("https://a.com")
    service.stats("abc123")
    assert service.stats("abc123")["clicks"] == 0
    assert service.stats("abc123")["last_visit"] is None


def test_milestone3_unknown_code(ex, service):
    with pytest.raises(ex.NotFound):
        service.resolve("nothing")
    with pytest.raises(ex.NotFound):
        service.stats("nothing")


# ===========================================================================
# Milestone 4 · The web API and the command line
# ===========================================================================

def call(app, method, path, body=None, key=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else b"")
    environ = {"REQUEST_METHOD": method, "PATH_INFO": path, "wsgi.input": io.BytesIO(data)}
    if data:
        environ["CONTENT_LENGTH"] = str(len(data))
        environ["CONTENT_TYPE"] = "application/json"
    if key is not None:
        environ["HTTP_X_API_KEY"] = key
    setup_testing_defaults(environ)
    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"], captured["headers"] = status, dict(headers)

    payload = b"".join(app(environ, start_response))
    assert captured["headers"]["Content-Length"] == str(len(payload))
    code = int(captured["status"].split()[0])
    assert captured["status"] == f"{code} {HTTPStatus(code).phrase}"
    return code, captured["headers"], json.loads(payload) if payload else None


@pytest.fixture
def app(ex, service):
    return ex.create_app(service, KEY)


def test_milestone4_health(app):
    assert call(app, "GET", "/health")[::2] == (200, {"status": "ok"})


def test_milestone4_create_link(app):
    status, headers, body = call(app, "POST", "/links", {"url": "https://python.org"}, key=KEY)
    assert status == 201
    assert body == {"code": "abc123", "url": "https://python.org", "short_url": "https://sho.rt/abc123"}
    assert headers["Location"] == "https://sho.rt/abc123"
    assert headers["Content-Type"].startswith("application/json")


def test_milestone4_create_with_custom_code_and_conflict(app):
    assert call(app, "POST", "/links", {"url": "https://a.com", "code": "docs"}, key=KEY)[2]["code"] == "docs"
    status, _, body = call(app, "POST", "/links", {"url": "https://b.com", "code": "docs"}, key=KEY)
    assert status == 409 and "docs" in body["error"]


@pytest.mark.parametrize("key", [None, "", "wrong", KEY + "x"])
def test_milestone4_create_needs_the_api_key(app, key):
    status, _, body = call(app, "POST", "/links", {"url": "https://a.com"}, key=key)
    assert status == 401 and "error" in body


def test_milestone4_create_compares_keys_in_constant_time(ex, app, monkeypatch):
    calls = []
    real = ex.hmac.compare_digest
    monkeypatch.setattr(ex.hmac, "compare_digest", lambda a, b: (calls.append(1), real(a, b))[1])
    call(app, "POST", "/links", {"url": "https://a.com"}, key=KEY)
    assert calls


@pytest.mark.parametrize("body, raw, status", [
    (None, b"{oops", 400),
    (None, b"", 400),
    ({"link": "https://a.com"}, None, 422),
    (["https://a.com"], None, 422),
    ({"url": 42}, None, 422),
    ({"url": "https://a.com", "code": 7}, None, 422),
    ({"url": "ftp://a.com"}, None, 422),
    ({"url": "https://a.com", "code": "x"}, None, 422),
])
def test_milestone4_create_validation(app, body, raw, status):
    code, _, payload = call(app, "POST", "/links", body, key=KEY, raw=raw)
    assert code == status and isinstance(payload["error"], str)


def test_milestone4_links_only_accepts_post(app):
    status, headers, _ = call(app, "GET", "/links", key=KEY)
    assert status == 405 and headers["Allow"] == "POST"


def test_milestone4_redirect(app, service):
    call(app, "POST", "/links", {"url": "https://python.org/about"}, key=KEY)
    status, headers, body = call(app, "GET", "/abc123")
    assert (status, headers["Location"], body) == (302, "https://python.org/about", None)
    assert service.stats("abc123")["clicks"] == 1


def test_milestone4_redirect_unknown(app):
    status, _, body = call(app, "GET", "/nothing")
    assert status == 404 and "nothing" in body["error"]
    assert call(app, "GET", "/a/b/c")[0] == 404


def test_milestone4_stats(app):
    call(app, "POST", "/links", {"url": "https://a.com"}, key=KEY)
    call(app, "GET", "/abc123")
    status, _, body = call(app, "GET", "/links/abc123/stats", key=KEY)
    assert status == 200
    assert (body["clicks"], body["url"], body["last_visit"]) == (1, "https://a.com", "2026-11-01T09:30:00+00:00")
    assert call(app, "GET", "/links/abc123/stats")[0] == 401
    assert call(app, "GET", "/links/zzz999/stats", key=KEY)[0] == 404


def test_milestone4_unexpected_errors_are_500_and_logged(ex, repo, caplog):
    class Broken(ex.ShortenerService):
        def resolve(self, code):
            raise RuntimeError("disk on fire")

    app = ex.create_app(Broken(repo, base_url="https://sho.rt"), KEY)
    with caplog.at_level(logging.ERROR, logger="shortener"):
        status, _, body = call(app, "GET", "/abc")
    assert (status, body) == (500, {"error": "internal server error"})
    assert any(r.exc_info and "disk on fire" in str(r.exc_info[1]) for r in caplog.records)


def test_milestone4_requests_are_logged(app, caplog):
    with caplog.at_level(logging.INFO, logger="shortener"):
        call(app, "GET", "/health")
        call(app, "GET", "/nothing")
    messages = [r.getMessage() for r in caplog.records if r.name == "shortener"]
    assert any(m.startswith("GET /health 200") for m in messages)
    assert any(m.startswith("GET /nothing 404") for m in messages)


# --- the command line ----------------------------------------------------------

@pytest.fixture
def env(tmp_path):
    return {"SHORT_API_KEY": KEY, "SHORT_DATABASE": str(tmp_path / "links.db"), "SHORT_BASE_URL": "https://sho.rt"}


def test_milestone4_cli_shorten_and_stats(ex, env, capsys):
    assert ex.main(["shorten", "https://www.python.org", "--code", "pydocs"], env=env) == 0
    assert capsys.readouterr().out == "https://sho.rt/pydocs\n"
    assert ex.main(["stats", "pydocs"], env=env) == 0          # a second run: data was persisted
    out = capsys.readouterr().out
    assert "url:" in out and "https://www.python.org" in out
    assert "clicks:" in out and "last_visit:" in out


def test_milestone4_cli_random_code(ex, env, capsys):
    assert ex.main(["shorten", "https://a.com"], env=env) == 0
    url = capsys.readouterr().out.strip()
    assert url.startswith("https://sho.rt/") and len(url.rsplit("/", 1)[1]) == 6


def test_milestone4_cli_errors(ex, env, capsys):
    assert ex.main(["shorten", "ftp://a.com"], env=env) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err.startswith("shortener: error: ")
    assert ex.main(["stats", "missing"], env=env) == 1
    assert "missing" in capsys.readouterr().err


def test_milestone4_cli_config_error(ex, capsys):
    assert ex.main(["recent"], env={}) == 2
    assert "SHORT_API_KEY: missing" in capsys.readouterr().err


def test_milestone4_cli_recent(ex, env, capsys):
    ex.main(["shorten", "https://a.com", "--code", "first"], env=env)
    ex.main(["shorten", "https://b.com", "--code", "second"], env=env)
    capsys.readouterr()
    assert ex.main(["recent"], env=env) == 0
    out = capsys.readouterr().out
    assert "first" in out and "second" in out and "https://b.com" in out


def test_milestone4_cli_serve_uses_the_app(ex, env):
    seen = {}

    def fake_serve(app, host, port):
        seen.update(host=host, port=port, health=call(app, "GET", "/health")[2])

    assert ex.main(["serve", "--port", "9000"], env=env, serve=fake_serve) == 0
    assert seen == {"host": "127.0.0.1", "port": 9000, "health": {"status": "ok"}}


def test_milestone4_cli_usage_error(ex, env):
    with pytest.raises(SystemExit) as info:
        ex.main(["fly"], env=env)
    assert info.value.code == 2


# --- end to end ----------------------------------------------------------------

class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None                                    # we want to SEE the 302, not follow it


def test_milestone4_end_to_end_over_http(ex, tmp_path):
    conn = ex.connect(str(tmp_path / "e2e.db"))
    service = ex.ShortenerService(ex.LinkRepository(conn), base_url="http://sho.rt")
    httpd = make_server("127.0.0.1", 0, ex.create_app(service, KEY), handler_class=QuietHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_port}"
    try:
        request = urllib.request.Request(base + "/links", method="POST", data=b'{"url": "https://www.python.org", "code": "py-org"}',
                                         headers={"Content-Type": "application/json", "X-API-Key": KEY})
        with urllib.request.urlopen(request, timeout=5) as response:
            assert response.status == 201
            assert json.loads(response.read())["short_url"] == "http://sho.rt/py-org"
        opener = urllib.request.build_opener(NoRedirect)
        with pytest.raises(urllib.error.HTTPError) as info:
            opener.open(base + "/py-org", timeout=5)
        assert info.value.code == 302 and info.value.headers["Location"] == "https://www.python.org"
        info.value.close()
        assert service.stats("py-org")["clicks"] == 1
    finally:
        httpd.shutdown()
        httpd.server_close()
        conn.close()
