"""Tests for assignment 08. Run: pytest professional/08-calling-http-apis/assignments/08-api-client -v"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

BASE = "https://api.example.com/v1"


class FakeTransport:
    """Returns scripted responses in order and records every request."""

    def __init__(self, ex, *responses):
        self.ex = ex
        self.responses = list(responses)
        self.requests = []

    def __call__(self, method, url, headers, body):
        self.requests.append({"method": method, "url": url, "headers": dict(headers), "body": body})
        status, payload, *extra = self.responses.pop(0)
        headers = extra[0] if extra else {}
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload).encode()
        return self.ex.Response(status, headers, payload)


def client_with(ex, *responses, **kwargs):
    transport = FakeTransport(ex, *responses)
    sleeps = []
    client = ex.ApiClient(BASE, transport=transport, sleep=sleeps.append, **kwargs)
    return client, transport, sleeps


# --- errors --------------------------------------------------------------------

def test_error_classes(ex):
    error = ex.ApiError(500, "boom")
    assert (error.status, error.message, str(error)) == (500, "boom", "HTTP 500: boom")
    assert issubclass(ex.NotFoundError, ex.ApiError)
    limited = ex.RateLimited(429, "slow down", 2.5)
    assert isinstance(limited, ex.ApiError)
    assert (limited.retry_after, str(limited)) == (2.5, "HTTP 429: slow down")


# --- building requests ---------------------------------------------------------

def test_get_builds_url_and_headers(ex):
    client, transport, _ = client_with(ex, (200, {"id": 42}), token="t0ken")
    assert client.get("/books/42") == {"id": 42}
    [request] = transport.requests
    assert request["method"] == "GET"
    assert request["url"] == BASE + "/books/42"
    assert request["headers"] == {"Accept": "application/json", "Authorization": "Bearer t0ken"}
    assert request["body"] is None


def test_trailing_slash_and_no_token(ex):
    transport = FakeTransport(ex, (200, []))
    ex.ApiClient(BASE + "/", transport=transport).get("/books")
    assert transport.requests[0]["url"] == BASE + "/books"
    assert "Authorization" not in transport.requests[0]["headers"]


def test_query_string_is_encoded(ex):
    client, transport, _ = client_with(ex, (200, []), (200, []))
    client.get("/search", q="Terry Pratchett & co", page=2)
    client.request("GET", "/search?sort=year", params={"q": "ü"})
    assert transport.requests[0]["url"] == BASE + "/search?q=Terry+Pratchett+%26+co&page=2"
    assert transport.requests[1]["url"] == BASE + "/search?sort=year&q=%C3%BC"


def test_post_sends_json(ex):
    client, transport, _ = client_with(ex, (201, {"id": 7, "title": "Mort"}))
    assert client.post("/books", {"title": "Mort", "year": 1987}) == {"id": 7, "title": "Mort"}
    request = transport.requests[0]
    assert request["method"] == "POST"
    assert request["headers"]["Content-Type"] == "application/json"
    assert json.loads(request["body"]) == {"title": "Mort", "year": 1987}
    assert isinstance(request["body"], bytes)


def test_empty_body_returns_none(ex):
    client, _, _ = client_with(ex, (204, b""))
    assert client.request("DELETE", "/books/7") is None


# --- errors from responses -----------------------------------------------------

def test_404_raises_not_found(ex):
    client, _, sleeps = client_with(ex, (404, {"error": "no such book"}))
    with pytest.raises(ex.NotFoundError) as info:
        client.get("/books/999")
    assert (info.value.status, info.value.message) == (404, "no such book")
    assert sleeps == []


@pytest.mark.parametrize("status, payload, message", [
    (422, {"error": "title is required"}, "title is required"),
    (500, b"  Internal Server Error\n", "Internal Server Error"),
    (400, {"detail": "x"}, '{"detail": "x"}'),
    (401, [1, 2], "[1, 2]"),
])
def test_other_errors(ex, status, payload, message):
    client, transport, sleeps = client_with(ex, (status, payload))
    with pytest.raises(ex.ApiError) as info:
        client.get("/x")
    assert type(info.value) is ex.ApiError
    assert (info.value.status, info.value.message) == (status, message)
    assert len(transport.requests) == 1 and sleeps == []           # 4xx and 500 are not retried


# --- retries -------------------------------------------------------------------

def test_retries_429_with_retry_after(ex):
    client, transport, sleeps = client_with(
        ex,
        (429, {"error": "slow down"}, {"retry-after": "2"}),
        (503, b"busy", {"retry-after": "0.5"}),
        (200, {"ok": True}),
    )
    assert client.get("/x") == {"ok": True}
    assert len(transport.requests) == 3
    assert sleeps == [2.0, 0.5]


def test_retry_after_missing_or_invalid_means_one_second(ex):
    client, _, sleeps = client_with(
        ex, (503, b""), (429, b"", {"retry-after": "Wed, 21 Oct 2026 07:28:00 GMT"}), (200, [])
    )
    client.get("/x")
    assert sleeps == [1, 1]


def test_gives_up_after_max_retries(ex):
    responses = [(429, {"error": "slow down"}, {"retry-after": "3"})] * 3
    client, transport, sleeps = client_with(ex, *responses, max_retries=2)
    with pytest.raises(ex.RateLimited) as info:
        client.get("/x")
    assert (info.value.retry_after, info.value.message) == (3.0, "slow down")
    assert len(transport.requests) == 3                            # 1 try + 2 retries
    assert sleeps == [3.0, 3.0]


def test_503_after_retries_is_api_error(ex):
    client, _, _ = client_with(ex, *[(503, b"down")] * 4)
    with pytest.raises(ex.ApiError) as info:
        client.get("/x")
    assert type(info.value) is ex.ApiError and info.value.status == 503


def test_no_retries(ex):
    client, transport, sleeps = client_with(ex, (503, b"down"), max_retries=0)
    with pytest.raises(ex.ApiError):
        client.get("/x")
    assert len(transport.requests) == 1 and sleeps == []


# --- pagination ----------------------------------------------------------------

def test_iter_items_follows_next_links(ex):
    client, transport, _ = client_with(
        ex,
        (200, {"items": [1, 2], "next": "/books?cursor=b"}),
        (200, {"items": [], "next": "/books?cursor=c"}),
        (200, {"items": [3], "next": None}),
    )
    assert list(client.iter_items("/books", author="pratchett")) == [1, 2, 3]
    assert [r["url"] for r in transport.requests] == [
        BASE + "/books?author=pratchett",
        BASE + "/books?cursor=b",
        BASE + "/books?cursor=c",
    ]


def test_iter_items_is_lazy(ex):
    client, transport, _ = client_with(
        ex, (200, {"items": [1, 2], "next": "/p2"}), (200, {"items": [3]})
    )
    items = client.iter_items("/books")
    assert transport.requests == []                                # nothing fetched before iterating
    assert next(items) == 1 and next(items) == 2
    assert len(transport.requests) == 1                            # page 2 not needed yet
    assert list(items) == [3]                                      # "next" missing ends it too


def test_iter_items_raises_errors(ex):
    client, _, _ = client_with(ex, (200, {"items": [1], "next": "/p2"}), (404, {"error": "gone"}))
    items = client.iter_items("/books")
    assert next(items) == 1
    with pytest.raises(ex.NotFoundError):
        next(items)


# --- the real transport, against a local server --------------------------------

class Handler(BaseHTTPRequestHandler):
    def _reply(self, status, payload, headers=()):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/echo":
            self._reply(200, {"query": parse_qs(url.query), "auth": self.headers.get("Authorization")},
                        [("X-Request-Id", "abc")])
        elif url.path == "/busy":
            self._reply(503, {"error": "busy"}, [("Retry-After", "0")])
        else:
            self._reply(404, {"error": f"no route {url.path}"})

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        data = json.loads(self.rfile.read(length))
        self._reply(201, {"received": data, "type": self.headers.get("Content-Type")})

    def log_message(self, *args):
        pass                                                       # keep the test output clean


@pytest.fixture(scope="module")
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def test_urllib_transport_success(ex, server):
    response = ex.urllib_transport("GET", server + "/echo?a=1", {"Accept": "application/json"}, None)
    assert response.status == 200
    assert response.headers["x-request-id"] == "abc"
    assert response.headers["content-type"] == "application/json"
    assert json.loads(response.body) == {"query": {"a": ["1"]}, "auth": None}


def test_urllib_transport_error_status_is_a_response(ex, server):
    response = ex.urllib_transport("GET", server + "/missing", {}, None)
    assert response.status == 404
    assert json.loads(response.body) == {"error": "no route /missing"}


def test_urllib_transport_passes_the_timeout(ex, monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout=None):
        seen["timeout"] = timeout
        raise OSError("stop here")

    monkeypatch.setattr(ex.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(OSError):
        ex.urllib_transport("GET", "http://example.invalid/", {}, None, timeout=3)
    assert seen["timeout"] == 3


def test_client_end_to_end(ex, server):
    client = ex.ApiClient(server, token="t0ken", sleep=lambda s: None, max_retries=1)
    assert client.get("/echo", q="a b") == {"query": {"q": ["a b"]}, "auth": "Bearer t0ken"}
    assert client.post("/books", {"title": "Mort"}) == {"received": {"title": "Mort"}, "type": "application/json"}
    with pytest.raises(ex.NotFoundError, match="no route /nope"):
        client.get("/nope")
    with pytest.raises(ex.ApiError, match="HTTP 503: busy"):
        client.get("/busy")
