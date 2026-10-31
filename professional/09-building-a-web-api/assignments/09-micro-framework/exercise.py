"""Assignment 09 · Micro framework.

Replace each `raise NotImplementedError` with your code. create_app() at the bottom is a given example
that uses your framework.
Check your work:  pytest professional/09-building-a-web-api/assignments/09-micro-framework -v
Try it for real:  python professional/09-building-a-web-api/assignments/09-micro-framework/exercise.py
"""

import json
import logging
import re
import uuid
from http import HTTPStatus
from urllib.parse import parse_qs

log = logging.getLogger(__name__)

PARAM_RE = re.compile(r"<(?:(int):)?([A-Za-z_]\w*)>")


class HttpError(Exception):
    """An error with an HTTP status; the framework turns it into {"error": message}."""

    def __init__(self, status, message):
        raise NotImplementedError


class Request:
    """method, path, query, headers, body and json(), read from a WSGI environ."""

    def __init__(self, environ):
        raise NotImplementedError

    @property
    def body(self):
        raise NotImplementedError

    def json(self):
        raise NotImplementedError


def compile_pattern(pattern):
    """'/books/<int:book_id>' -> (compiled regex, {"book_id": int})."""
    raise NotImplementedError


class App:
    """A WSGI application with a router."""

    def __init__(self):
        raise NotImplementedError

    def route(self, method, pattern):
        raise NotImplementedError

    def __call__(self, environ, start_response):
        raise NotImplementedError


def request_id_middleware(app, make_id=lambda: uuid.uuid4().hex[:8]):
    """Wrap a WSGI app: put a request id into environ["request_id"] and the X-Request-Id header."""
    raise NotImplementedError


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
