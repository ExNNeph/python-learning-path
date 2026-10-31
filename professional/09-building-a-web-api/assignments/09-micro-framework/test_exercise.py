"""Tests for assignment 09. Run: pytest professional/09-building-a-web-api/assignments/09-micro-framework -v"""

import io
import json
import logging
import threading
import urllib.request
from http import HTTPStatus
from urllib.error import HTTPError
from wsgiref.simple_server import WSGIRequestHandler, make_server
from wsgiref.util import setup_testing_defaults

import pytest


def environ_for(method="GET", path="/", query="", body=b"", headers=None, content_type="application/json"):
    environ = {"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query, "wsgi.input": io.BytesIO(body)}
    if body:
        environ["CONTENT_LENGTH"] = str(len(body))
        environ["CONTENT_TYPE"] = content_type
    for name, value in (headers or {}).items():
        environ["HTTP_" + name.upper().replace("-", "_")] = value
    setup_testing_defaults(environ)
    return environ


def call(app, method="GET", path="/", **kwargs):
    """Call a WSGI app like a server would; return (status, headers dict, decoded body or None)."""
    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"], captured["headers"] = status, dict(headers)

    body = b"".join(app(environ_for(method, path, **kwargs), start_response))
    headers = captured["headers"]
    assert headers["Content-Length"] == str(len(body))
    return captured["status"], headers, json.loads(body) if body else None


# --- HttpError and Request -----------------------------------------------------

def test_http_error(ex):
    error = ex.HttpError(422, "title is required")
    assert isinstance(error, Exception)
    assert (error.status, error.message, str(error)) == (422, "title is required", "title is required")


def test_request_basics(ex):
    request = ex.Request(environ_for("post", "/books", query="sort=year&tag=a&tag=b&empty=",
                                     body=b'{"title": "Mort"}', headers={"Authorization": "Bearer t", "X-Request-Id": "r1"}))
    assert request.method == "POST"
    assert request.path == "/books"
    assert request.query == {"sort": "year", "tag": "a", "empty": ""}
    assert request.headers["authorization"] == "Bearer t"
    assert request.headers["x-request-id"] == "r1"
    assert request.headers["content-type"] == "application/json"
    assert request.headers["content-length"] == "17"
    assert request.body == b'{"title": "Mort"}'
    assert request.body == b'{"title": "Mort"}'                # reading twice works (cached)
    assert request.json() == {"title": "Mort"}


def test_request_without_body_or_query(ex):
    environ = environ_for("GET", "/")
    environ.pop("QUERY_STRING")
    request = ex.Request(environ)
    assert request.query == {}
    assert request.body == b""
    assert "content-length" not in request.headers


def test_request_reads_only_content_length(ex):
    environ = environ_for("POST", "/x", body=b"[1, 2]")
    environ["wsgi.input"] = io.BytesIO(b"[1, 2]GARBAGE AFTER THE BODY")
    assert ex.Request(environ).json() == [1, 2]


@pytest.mark.parametrize("body", [b"", b"{oops", b"\xff\xfe"])
def test_request_invalid_json(ex, body):
    environ = environ_for("POST", "/x", body=body)
    with pytest.raises(ex.HttpError) as info:
        ex.Request(environ).json()
    assert (info.value.status, info.value.message) == (400, "invalid JSON")


# --- compile_pattern -----------------------------------------------------------

def test_compile_pattern(ex):
    regex, converters = ex.compile_pattern("/users/<name>/books/<int:book_id>")
    match = regex.fullmatch("/users/ada/books/42")
    assert match.groupdict() == {"name": "ada", "book_id": "42"}
    assert converters == {"name": str, "book_id": int}
    assert regex.fullmatch("/users/ada/books/x") is None
    assert regex.fullmatch("/users/a/b/books/1") is None


def test_compile_pattern_escapes_literals(ex):
    regex, converters = ex.compile_pattern("/v1.0/items")
    assert converters == {}
    assert regex.fullmatch("/v1.0/items")
    assert regex.fullmatch("/v1x0/items") is None


# --- routing and responses -----------------------------------------------------

@pytest.fixture
def app(ex):
    app = ex.App()
    seen = {}

    @app.route("GET", "/books/<int:book_id>")
    def get_book(request, book_id):
        seen["book_id"] = book_id
        return {"id": book_id}

    @app.route("delete", "/books/<int:book_id>")
    def delete_book(request, book_id):
        return None

    @app.route("PUT", "/books/<int:book_id>")
    def put_book(request, book_id):
        return request.json(), 200

    @app.route("POST", "/books")
    def create(request):
        data = request.json()
        if not data.get("title"):
            raise ex.HttpError(422, "title is required")
        return {"id": 7, "title": data["title"]}, 201

    @app.route("GET", "/users/<name>")
    def user(request, name):
        return {"name": name, "query": request.query}

    @app.route("GET", "/crash")
    def crash(request):
        raise RuntimeError("database password is hunter2")

    app.seen = seen
    app.handlers = (get_book, create)
    return app


def test_route_returns_handler_unchanged(ex, app):
    get_book, create = app.handlers
    assert get_book.__name__ == "get_book"
    assert get_book(None, 3) == {"id": 3}


def test_get_with_int_parameter(app):
    status, headers, body = call(app, "GET", "/books/42")
    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert body == {"id": 42}
    assert app.seen["book_id"] == 42 and type(app.seen["book_id"]) is int


def test_string_parameter_and_query(app):
    assert call(app, "GET", "/users/ada", query="x=1")[2] == {"name": "ada", "query": {"x": "1"}}


def test_created(app):
    status, _, body = call(app, "POST", "/books", body=b'{"title": "Mort"}')
    assert (status, body) == ("201 Created", {"id": 7, "title": "Mort"})


def test_no_content(app):
    status, headers, body = call(app, "DELETE", "/books/1")
    assert status == "204 No Content"
    assert body is None and headers["Content-Length"] == "0"
    assert "Content-Type" not in headers


def test_http_errors(app):
    assert call(app, "POST", "/books", body=b'{"year": 1987}')[::2] == (f"422 {HTTPStatus(422).phrase}", {"error": "title is required"})  # "Unprocessable Content" on 3.13+
    assert call(app, "POST", "/books", body=b"{oops")[::2] == ("400 Bad Request", {"error": "invalid JSON"})


def test_not_found(app):
    assert call(app, "GET", "/nothing")[::2] == ("404 Not Found", {"error": "not found"})
    assert call(app, "GET", "/books/abc")[0] == "404 Not Found"        # <int:...> does not match letters
    assert call(app, "GET", "/books/1/extra")[0] == "404 Not Found"    # the whole path must match


def test_method_not_allowed(app):
    status, headers, body = call(app, "PATCH", "/books/1")
    assert status == "405 Method Not Allowed"
    assert headers["Allow"] == "DELETE, GET, PUT"
    assert body == {"error": "method not allowed"}
    assert call(app, "GET", "/books")[1]["Allow"] == "POST"


def test_unexpected_error_is_500_and_logged(app, caplog):
    with caplog.at_level(logging.ERROR):
        status, _, body = call(app, "GET", "/crash")
    assert (status, body) == ("500 Internal Server Error", {"error": "internal server error"})
    assert "hunter2" not in json.dumps(body)                          # nothing leaks to the client
    assert any(record.exc_info and "hunter2" in str(record.exc_info[1]) for record in caplog.records)


def test_first_matching_route_wins(ex):
    app = ex.App()

    @app.route("GET", "/items/<int:item_id>")
    def by_id(request, item_id):
        return "by id"

    @app.route("GET", "/items/<slug>")
    def by_slug(request, slug):
        return "by slug"

    assert call(app, "GET", "/items/5")[2] == "by id"
    assert call(app, "GET", "/items/five")[2] == "by slug"


# --- middleware ----------------------------------------------------------------

def test_request_id_middleware(ex, app):
    seen = []

    @app.route("GET", "/whoami")
    def whoami(request):
        seen.append(request.environ["request_id"])
        return "ok"

    wrapped = ex.request_id_middleware(app, make_id=lambda: "gen123")
    _, headers, _ = call(wrapped, "GET", "/whoami")
    assert headers["X-Request-Id"] == "gen123"
    _, headers, _ = call(wrapped, "GET", "/whoami", headers={"X-Request-Id": "client-7"})
    assert headers["X-Request-Id"] == "client-7"
    assert seen == ["gen123", "client-7"]
    assert call(wrapped, "GET", "/nothing")[1]["X-Request-Id"] == "gen123"    # on errors too


def test_request_id_default_generator(ex, app):
    _, headers, _ = call(ex.request_id_middleware(app), "GET", "/books/1")
    assert len(headers["X-Request-Id"]) == 8
    int(headers["X-Request-Id"], 16)


# --- the example app over a real server ----------------------------------------

class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture
def server(ex):
    httpd = make_server("127.0.0.1", 0, ex.create_app(), handler_class=QuietHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def http(method, url, data=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None, response.headers["X-Request-Id"]
    except HTTPError as error:
        with error:
            return error.code, json.loads(error.read()), error.headers["X-Request-Id"]


def test_example_app_end_to_end(server):
    assert http("GET", server + "/books")[:2] == (200, [{"id": 1, "title": "Mort"}])
    assert http("POST", server + "/books", {"title": "  Dune "})[:2] == (201, {"id": 2, "title": "Dune"})
    assert http("POST", server + "/books", {"title": ""})[:2] == (422, {"error": "title is required"})
    assert http("GET", server + "/books/9")[:2] == (404, {"error": "book 9 not found"})
    assert http("DELETE", server + "/books/1")[:2] == (204, None)
    status, body, request_id = http("GET", server + "/books")
    assert (status, body) == (200, [{"id": 2, "title": "Dune"}])
    assert request_id and len(request_id) == 8
