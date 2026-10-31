# Assignment 09 · Micro framework

> **Lesson:** [09 · Building a web API](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~3 h

## Goal

Build a tiny web framework on plain WSGI, the core of what Flask does: a router with typed path
parameters, a request object, JSON responses with correct status codes, error handling that never leaks a
traceback, and a middleware. The example app at the bottom of `exercise.py` (given) uses your framework;
when you are done, run the file and talk to your API with a browser or `curl`.

## What to write

| Name | Specification |
|---|---|
| `HttpError(status, message)` | an exception with the attributes `status` and `message`; `str()` is the message |
| `Request(environ)` | see below |
| `compile_pattern(pattern)` | returns `(regex, converters)`. In the pattern, `<name>` matches one path segment (no `/`) as a string, `<int:name>` matches digits and converts them to `int`. Everything else matches **literally** (a `.` is a dot). `converters` maps each name to `str` or `int`. The regex is used with `fullmatch` |
| `App()` | a WSGI application with a router, see below |
| `request_id_middleware(app, make_id=...)` | returns a WSGI app that wraps `app`: the request id is the client's `X-Request-Id` header, or `make_id()` if there is none. It is stored in `environ["request_id"]` and added as an `X-Request-Id` header to **every** response |

### `Request`

| Attribute | Value |
|---|---|
| `method` | `REQUEST_METHOD`, in capitals |
| `path` | `PATH_INFO` (`"/"` if empty) |
| `query` | the query string as a dict, the **first** value of each key; blank values are kept (`"a="` → `{"a": ""}`); `{}` without a query string |
| `headers` | a dict with lower-case names: every `HTTP_X_REQUEST_ID` becomes `"x-request-id"`; `CONTENT_TYPE` and `CONTENT_LENGTH` are included as `"content-type"` and `"content-length"` when present and not empty |
| `environ` | the environ dict |
| `body` | a property: exactly `CONTENT_LENGTH` bytes read from `environ["wsgi.input"]` (`b""` if missing), read once and remembered |
| `json()` | the decoded body. Invalid JSON (including an empty body) raises `HttpError(400, "invalid JSON")` |

### `App`

| Method | Specification |
|---|---|
| `route(method, pattern)` | a decorator that registers the handler for `method` (any case) and `pattern`, and returns the handler **unchanged** |
| `app(environ, start_response)` | finds the **first** route (in registration order) whose pattern matches the whole path and whose method is the request's, and calls `handler(request, **params)` with the converted parameters |

| The handler... | The response |
|---|---|
| returns data | `200`, the data as JSON |
| returns `(data, status)` | that status, the data as JSON |
| returns `None` | `204`, empty body, no `Content-Type` |
| raises `HttpError` | its status, `{"error": message}` |
| raises anything else | `500`, `{"error": "internal server error"}`; log it with `log.exception(...)` (with the traceback) |
| (no pattern matches the path) | `404`, `{"error": "not found"}` |
| (patterns match, but not for this method) | `405`, `{"error": "method not allowed"}`, header `Allow` with those methods, sorted, joined by `", "` |

Every response has a `Content-Length` header; JSON responses also have
`Content-Type: application/json; charset=utf-8`. The status line is `"<code> <phrase>"` with the phrase
from `http.HTTPStatus(code).phrase`, for example `"404 Not Found"`.

## Examples

```python
>>> app = App()
>>> @app.route("GET", "/books/<int:book_id>")
... def get_book(request, book_id):
...     return {"id": book_id, "type": type(book_id).__name__}
```

```text
GET /books/42            → 200 OK                  {"id": 42, "type": "int"}
GET /books/abc           → 404 Not Found           {"error": "not found"}
DELETE /books/42         → 405 Method Not Allowed  {"error": "method not allowed"}    Allow: GET
```

Try the example app for real:

```bash
python professional/09-building-a-web-api/assignments/09-micro-framework/exercise.py
```

```bash
curl -i -X POST http://127.0.0.1:8000/books -d '{"title": "Dune"}'
```

## Hints

<details>
<summary>Hint 1: compile_pattern</summary>

Walk over the matches of `PARAM_RE` (given) with `finditer`. Escape the literal text between parameters
with `re.escape`, and insert `(?P<name>\d+)` or `(?P<name>[^/]+)` for each parameter.
</details>

<details>
<summary>Hint 2: 404 or 405?</summary>

While looping over the routes, collect the methods of routes whose pattern matches but whose method does
not. If no route was called: a non-empty set means `405`, an empty one `404`.
</details>

<details>
<summary>Hint 3: one function for every response</summary>

A helper `_respond(start_response, status, data=None, headers=())` that encodes the body, builds the
headers, calls `start_response` and returns `[body]` keeps `__call__` short. The middleware passes its own
`start_response` that appends the header and calls the real one.
</details>

## Check your work

```bash
pytest professional/09-building-a-web-api/assignments/09-micro-framework -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/09-building-a-web-api/assignments/09-micro-framework/exercise.py),
then tick off assignment 09 in the [progress checklist](../../../../README.md#progress-checklist).
