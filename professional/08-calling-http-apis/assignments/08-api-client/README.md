# Assignment 08 · API client

> **Lesson:** [08 · Calling HTTP APIs](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Write a client for a JSON API the way professional teams do: the client builds URLs, headers and JSON
bodies, turns error statuses into typed exceptions, waits and retries when the server asks for it, and
hides pagination behind a generator. The network itself sits behind a small, replaceable **transport**
function, so almost every test runs offline. One test checks the real transport against a local server.

## Given

`Response(status, headers, body)`: a frozen dataclass; `headers` is a dict with **lower-case** keys,
`body` is `bytes`.

A **transport** is any function `transport(method, url, headers, body) -> Response`.

## What to write

| Name | Specification |
|---|---|
| `ApiError(status, message)` | an exception with the attributes `status` and `message`; `str()` is `"HTTP <status>: <message>"` |
| `NotFoundError` | a subclass of `ApiError`, for status `404` |
| `RateLimited(status, message, retry_after)` | a subclass of `ApiError` with the extra attribute `retry_after` |
| `urllib_transport(method, url, headers, body, timeout=10)` | sends the request with `urllib.request` (with the timeout) and returns a `Response` with the status, the headers (keys in lower case) and the body. **Error statuses are responses too**: catch `HTTPError` and return its status, headers and body |
| `ApiClient(base_url, *, token=None, transport=urllib_transport, sleep=time.sleep, max_retries=3)` | stores its settings; a trailing `/` of `base_url` is removed |

### `ApiClient` methods

| Method | Specification |
|---|---|
| `request(method, path, *, params=None, json_body=None)` | sends `method` to `base_url + path`. `params` (a dict) are added as a query string with `urlencode` (with `&` if the path already has a `?`). Headers: always `Accept: application/json`; `Authorization: Bearer <token>` if there is a token; with a `json_body`, the body is `json.dumps(json_body).encode()` and `Content-Type: application/json` is set (without one, the body is `None`) |
| ... retries | a `429` or `503` response is retried up to `max_retries` times: before each retry call `sleep(seconds)` with the response's `Retry-After` header as a number (missing or not a number: `1`) |
| ... result | a `2xx` returns the decoded JSON body (`None` for an empty body). Otherwise raise: `NotFoundError` for `404`, `RateLimited` (with `retry_after`) for a `429` that is still there after all retries, `ApiError` for everything else. The message is the `"error"` field if the body is a JSON object with one, else the body text, stripped |
| `get(path, **params)` | `request("GET", path, params=params)` |
| `post(path, data)` | `request("POST", path, json_body=data)` |
| `iter_items(path, **params)` | a **generator** over all items of a paginated list. Every page is `{"items": [...], "next": <path or null>}`. Request the first page with `params`, yield its items, then follow `next` (a path that already contains its query string) until it is `null` or missing. Pages are fetched only when needed |

## Examples

```python
>>> pages = {
...     "https://api.example.com/v1/books?author=pratchett": b'{"items": [1, 2], "next": "/books?cursor=b"}',
...     "https://api.example.com/v1/books?cursor=b": b'{"items": [3], "next": null}',
... }
>>> def fake(method, url, headers, body):
...     print(method, url)
...     return Response(200, {"content-type": "application/json"}, pages[url])
>>> client = ApiClient("https://api.example.com/v1/", token="t0ken", transport=fake)
>>> list(client.iter_items("/books", author="pratchett"))
GET https://api.example.com/v1/books?author=pratchett
GET https://api.example.com/v1/books?cursor=b
[1, 2, 3]

>>> client.get("/books/999")          # the server answers 404 {"error": "no such book"}
Traceback (most recent call last):
NotFoundError: HTTP 404: no such book
```

## Hints

<details>
<summary>Hint 1: the retry loop</summary>

`for attempt in range(self.max_retries + 1):` send the request; `break` if the status is not 429/503
or if this was the last attempt; otherwise sleep. After the loop, `response` is the final answer: decide
between returning and raising once, there.
</details>

<details>
<summary>Hint 2: the error message</summary>

`json.loads(response.body)` may fail (`ValueError`) or return something that is not a dict. Fall back to
`response.body.decode("utf-8", errors="replace").strip()`.
</details>

<details>
<summary>Hint 3: urllib</summary>

`urllib.request.Request(url, data=body, headers=headers, method=method)`; the response of `urlopen` has
`.status`, `.headers.items()` and `.read()`. An `HTTPError` has `.code`, `.headers` and `.read()`.
</details>

## Check your work

```bash
pytest professional/08-calling-http-apis/assignments/08-api-client -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/08-calling-http-apis/assignments/08-api-client/exercise.py),
then tick off assignment 08 in the [progress checklist](../../../../README.md#progress-checklist).
