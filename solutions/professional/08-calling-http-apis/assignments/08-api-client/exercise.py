"""Assignment 08 · API client: template solution."""

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
    def __init__(self, status, message):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


class NotFoundError(ApiError):
    pass


class RateLimited(ApiError):
    def __init__(self, status, message, retry_after):
        super().__init__(status, message)
        self.retry_after = retry_after


def urllib_transport(method, url, headers, body, timeout=10):
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return Response(response.status, {k.lower(): v for k, v in response.headers.items()}, response.read())
    except HTTPError as error:
        # urllib raises for 4xx/5xx, but for an API client those are ordinary responses.
        with error:
            return Response(error.code, {k.lower(): v for k, v in error.headers.items()}, error.read())


def _error_message(response):
    try:
        data = json.loads(response.body)
        if isinstance(data, dict) and "error" in data:
            return str(data["error"])
    except ValueError:
        pass
    return response.body.decode("utf-8", errors="replace").strip()


def _retry_after(response):
    try:
        return float(response.headers.get("retry-after", 1))
    except ValueError:
        return 1.0


class ApiClient:
    def __init__(self, base_url, *, token=None, transport=urllib_transport, sleep=time.sleep, max_retries=3):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.transport = transport
        self.sleep = sleep
        self.max_retries = max_retries

    def request(self, method, path, *, params=None, json_body=None):
        url = self.base_url + path
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params)
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        body = None
        if json_body is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(json_body).encode()

        for attempt in range(self.max_retries + 1):
            response = self.transport(method, url, headers, body)
            if response.status not in RETRY_STATUSES or attempt == self.max_retries:
                break
            self.sleep(_retry_after(response))       # the server says how long to wait

        if 200 <= response.status < 300:
            return json.loads(response.body) if response.body else None
        message = _error_message(response)
        if response.status == 404:
            raise NotFoundError(404, message)
        if response.status == 429:
            raise RateLimited(429, message, _retry_after(response))
        raise ApiError(response.status, message)

    def get(self, path, **params):
        return self.request("GET", path, params=params)

    def post(self, path, data):
        return self.request("POST", path, json_body=data)

    def iter_items(self, path, **params):
        page = self.request("GET", path, params=params)
        while True:
            yield from page["items"]
            if not page.get("next"):
                return
            page = self.request("GET", page["next"])     # the next link already has its query


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
