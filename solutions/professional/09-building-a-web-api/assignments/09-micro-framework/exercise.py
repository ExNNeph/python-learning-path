"""Assignment 09 · Micro framework: template solution."""

import json
import logging
import re
import uuid
from http import HTTPStatus
from urllib.parse import parse_qs

log = logging.getLogger(__name__)

PARAM_RE = re.compile(r"<(?:(int):)?([A-Za-z_]\w*)>")


class HttpError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.path = environ.get("PATH_INFO") or "/"
        query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        self.query = {key: values[0] for key, values in query.items()}
        self.headers = {
            key[5:].replace("_", "-").lower(): value
            for key, value in environ.items()
            if key.startswith("HTTP_")
        }
        for key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            if environ.get(key):
                self.headers[key.replace("_", "-").lower()] = environ[key]
        self._body = None

    @property
    def body(self):
        if self._body is None:
            try:
                length = int(self.environ.get("CONTENT_LENGTH") or 0)
            except ValueError:
                length = 0
            # Read exactly CONTENT_LENGTH bytes: reading "until the end" can block on a live socket.
            self._body = self.environ["wsgi.input"].read(length) if length > 0 else b""
        return self._body

    def json(self):
        try:
            return json.loads(self.body)
        except ValueError:                          # JSONDecodeError and UnicodeDecodeError
            raise HttpError(400, "invalid JSON") from None


def compile_pattern(pattern):
    """'/books/<int:book_id>' -> (regex, {"book_id": int})."""
    converters, parts, position = {}, [], 0
    for match in PARAM_RE.finditer(pattern):
        kind, name = match.groups()
        parts.append(re.escape(pattern[position:match.start()]))
        parts.append(rf"(?P<{name}>\d+)" if kind == "int" else rf"(?P<{name}>[^/]+)")
        converters[name] = int if kind == "int" else str
        position = match.end()
    parts.append(re.escape(pattern[position:]))
    return re.compile("".join(parts)), converters


def _respond(start_response, status, data=None, headers=()):
    body = b"" if status == 204 else json.dumps(data).encode()
    all_headers = [("Content-Length", str(len(body)))] + list(headers)
    if status != 204:
        all_headers.insert(0, ("Content-Type", "application/json; charset=utf-8"))
    start_response(f"{status} {HTTPStatus(status).phrase}", all_headers)
    return [body]


class App:
    def __init__(self):
        self.routes = []                            # (method, regex, converters, handler), in order

    def route(self, method, pattern):
        regex, converters = compile_pattern(pattern)

        def decorator(handler):
            self.routes.append((method.upper(), regex, converters, handler))
            return handler                          # unchanged: still callable and testable directly
        return decorator

    def __call__(self, environ, start_response):
        request = Request(environ)
        allowed = set()
        for method, regex, converters, handler in self.routes:
            match = regex.fullmatch(request.path)
            if not match:
                continue
            if method != request.method:
                allowed.add(method)
                continue
            params = {name: converters[name](value) for name, value in match.groupdict().items()}
            try:
                result = handler(request, **params)
            except HttpError as error:
                return _respond(start_response, error.status, {"error": error.message})
            except Exception:
                # The boundary: the client learns nothing about our code, the log gets everything.
                log.exception("unhandled error in %s %s", request.method, request.path)
                return _respond(start_response, 500, {"error": "internal server error"})
            if result is None:
                return _respond(start_response, 204)
            if isinstance(result, tuple):
                data, status = result
                return _respond(start_response, status, data)
            return _respond(start_response, 200, result)
        if allowed:
            return _respond(start_response, 405, {"error": "method not allowed"},
                            [("Allow", ", ".join(sorted(allowed)))])
        return _respond(start_response, 404, {"error": "not found"})


def request_id_middleware(app, make_id=lambda: uuid.uuid4().hex[:8]):
    def wrapped(environ, start_response):
        rid = environ.get("HTTP_X_REQUEST_ID") or make_id()
        environ["request_id"] = rid                 # handlers can read it: request.environ["request_id"]

        def start_with_id(status, headers, exc_info=None):
            return start_response(status, list(headers) + [("X-Request-Id", rid)], exc_info)

        return app(environ, start_with_id)
    return wrapped


# --- a small example app -------------------------------------------------------

def create_app():
    app = App()
    books = {1: {"id": 1, "title": "Mort"}}

    @app.route("GET", "/books")
    def list_books(request):
        return sorted(books.values(), key=lambda b: b["id"])

    @app.route("GET", "/books/<int:book_id>")
    def get_book(request, book_id):
        if book_id not in books:
            raise HttpError(404, f"book {book_id} not found")
        return books[book_id]

    @app.route("POST", "/books")
    def create_book(request):
        data = request.json()
        if not isinstance(data, dict) or not isinstance(data.get("title"), str) or not data["title"].strip():
            raise HttpError(422, "title is required")
        book_id = max(books, default=0) + 1
        books[book_id] = {"id": book_id, "title": data["title"].strip()}
        return books[book_id], 201

    @app.route("DELETE", "/books/<int:book_id>")
    def delete_book(request, book_id):
        books.pop(book_id, None)

    return request_id_middleware(app)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    print("serving on http://127.0.0.1:8000/books  (Ctrl+C to stop)")
    make_server("127.0.0.1", 8000, create_app()).serve_forever()
