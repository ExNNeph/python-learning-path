"""Assignment 08 · API client.

Replace each `raise NotImplementedError` with your code. Response is given.
Check your work:  pytest professional/08-calling-http-apis/assignments/08-api-client -v
"""

import json
import time
import urllib.request
from dataclasses import dataclass, field
from urllib.error import HTTPError
from urllib.parse import urlencode

RETRY_STATUSES = {429, 503}


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict = field(default_factory=dict)      # keys in lower case
    body: bytes = b""


class ApiError(Exception):
    """Attributes: status, message. str(): 'HTTP <status>: <message>'."""

    def __init__(self, status, message):
        raise NotImplementedError


class NotFoundError(ApiError):
    pass


class RateLimited(ApiError):
    """An ApiError with the extra attribute retry_after (seconds)."""

    def __init__(self, status, message, retry_after):
        raise NotImplementedError


def urllib_transport(method, url, headers, body, timeout=10):
    """Send one request with urllib; return a Response, also for 4xx and 5xx statuses."""
    raise NotImplementedError


class ApiClient:
    def __init__(self, base_url, *, token=None, transport=urllib_transport, sleep=time.sleep, max_retries=3):
        raise NotImplementedError

    def request(self, method, path, *, params=None, json_body=None):
        """Send a request; return the decoded JSON body, retry 429/503, raise ApiError subclasses."""
        raise NotImplementedError

    def get(self, path, **params):
        raise NotImplementedError

    def post(self, path, data):
        raise NotImplementedError

    def iter_items(self, path, **params):
        """Yield every item of every page, following the "next" links."""
        raise NotImplementedError


if __name__ == "__main__":
    pages = {
        "https://api.example.com/v1/books?author=pratchett": b'{"items": [1, 2], "next": "/books?cursor=b"}',
        "https://api.example.com/v1/books?cursor=b": b'{"items": [3], "next": null}',
    }

    def fake(method, url, headers, body):
        print(method, url)
        return Response(200, {"content-type": "application/json"}, pages[url])

    client = ApiClient("https://api.example.com/v1/", token="t0ken", transport=fake)
    print(list(client.iter_items("/books", author="pratchett")))
