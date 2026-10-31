# Assignment 04 · Logging setup

> **Lesson:** [04 · Logging](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Build the logging setup that a real service would use: JSON lines for a log service, a request id on
every line, a filter that keeps secrets out of the log, one `dictConfig` call that wires it all together,
and a context manager that logs how long an operation took.

## What to write

| Name | Specification |
|---|---|
| `JsonFormatter` | a `logging.Formatter` whose `format(record)` returns **one line** of JSON (`json.dumps(..., default=str)`) with the keys, in this order: `time` (the record's creation time in UTC, ISO 8601 with milliseconds: `2026-11-01T09:30:00.123+00:00`), `level` (`"INFO"`), `logger` (the logger name), `message` (the formatted message), then every **extra** field of the record (attributes not in `STANDARD_ATTRIBUTES`, which is given), and finally `exception` (the formatted traceback) if the record has `exc_info` |
| `RedactFilter(keys=("password", "token", "api_key"))` | a `logging.Filter` that **never drops** a record, but cleans it: in the formatted message, every `key=value` for one of the keys (case-insensitive, the value runs up to the next whitespace) becomes `key=***`; every record attribute named like one of the keys (from `extra`) becomes `"***"` |
| `request_id` | a `ContextVar` with the default `"-"` (given) |
| `RequestIdFilter` | sets `record.request_id` to the current value of `request_id`; never drops a record |
| `request_context(rid=None)` | a context manager that sets `request_id` to `rid` (or a new random 8-character hex id if `None`) for the duration of the block, yields the id, and restores the previous value afterwards, also after an exception |
| `configure_logging(level="INFO", *, stream=None, json=True)` | configures the **root** logger with `logging.config.dictConfig`: level `level`, one `StreamHandler` writing to `stream` (default `sys.stderr`) that has **both filters** (request id first, then redact) and either the `JsonFormatter` or the text format `"%(levelname)s %(name)s [%(request_id)s] %(message)s"`. Loggers that already exist keep working. Calling it again replaces the setup (no duplicate lines) |
| `log_duration(logger, action, *, clock=time.perf_counter)` | a context manager that measures the block with `clock`. Success: `logger.info("<action> finished in <ms> ms")`. Exception: `logger.error("<action> failed after <ms> ms")` **with the traceback**, then the exception propagates. Both records carry the extra fields `action` and `duration_ms` (ms = `round(seconds * 1000)`) |

## Examples

```python
>>> configure_logging("INFO", stream=sys.stdout)
>>> log = logging.getLogger("shop.orders")
>>> with request_context("7f3a"):
...     log.info("login user=ada password=hunter2")
...     with log_duration(log, "checkout"):
...         time.sleep(0.05)
{"time": "2026-11-01T09:30:00.012+00:00", "level": "INFO", "logger": "shop.orders", "message": "login user=ada password=***", "request_id": "7f3a"}
{"time": "2026-11-01T09:30:00.064+00:00", "level": "INFO", "logger": "shop.orders", "message": "checkout finished in 52 ms", "action": "checkout", "duration_ms": 52, "request_id": "7f3a"}

>>> configure_logging("DEBUG", stream=sys.stdout, json=False)
>>> log.debug("cache miss for %s", "rates", extra={"token": "abc123"})
DEBUG shop.orders [-] cache miss for rates
```

## Hints

<details>
<summary>Hint 1: the formatter</summary>

`datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds")` gives the time.
`vars(record)` is the dict of all record attributes; keep those whose name is not in
`STANDARD_ATTRIBUTES`. `self.formatException(record.exc_info)` formats a traceback.
</details>

<details>
<summary>Hint 2: redacting the message</summary>

Format first: `message = record.getMessage()` (template + arguments). Replace with a regular expression
like `rf"\b({names})=\S+"` and `re.IGNORECASE`, then store the result as `record.msg` and set
`record.args = None`, because the arguments are already inside the message.
</details>

<details>
<summary>Hint 3: dictConfig</summary>

Use `"()"` to create your classes: `"filters": {"redact": {"()": RedactFilter}}` and
`"formatters": {"json": {"()": JsonFormatter}}`. A stream object can be passed directly as
`"stream": stream`. Do not forget `"disable_existing_loggers": False`.
</details>

## Check your work

```bash
pytest professional/04-logging/assignments/04-logging-setup -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/04-logging/assignments/04-logging-setup/exercise.py),
then tick off assignment 04 in the [progress checklist](../../../../README.md#progress-checklist).
