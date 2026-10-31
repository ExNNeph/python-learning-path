"""Assignment 04 · Logging setup: template solution."""

import contextvars
import json
import logging
import logging.config
import re
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

# Every attribute a plain LogRecord has; anything else on a record came from `extra` or a filter.
STANDARD_ATTRIBUTES = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}

request_id = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        data.update({k: v for k, v in vars(record).items() if k not in STANDARD_ATTRIBUTES})
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        # default=str: an odd value (a Path, a datetime) must never crash the logging call.
        return json.dumps(data, default=str)


class RedactFilter(logging.Filter):
    def __init__(self, keys=("password", "token", "api_key")):
        super().__init__()
        self.keys = {key.lower() for key in keys}
        names = "|".join(map(re.escape, keys))
        self.pattern = re.compile(rf"\b({names})=\S+", re.IGNORECASE)

    def filter(self, record):
        message = record.getMessage()
        redacted = self.pattern.sub(r"\1=***", message)
        if redacted != message:
            # The message is already formatted: replace the template, drop the arguments.
            record.msg, record.args = redacted, None
        for name in vars(record):
            if name.lower() in self.keys:
                setattr(record, name, "***")
        return True                       # never drop a record, only clean it


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get()
        return True


@contextmanager
def request_context(rid=None):
    rid = rid or uuid.uuid4().hex[:8]
    token = request_id.set(rid)
    try:
        yield rid
    finally:
        request_id.reset(token)           # back to whatever was set before, even after an error


def configure_logging(level="INFO", *, stream=None, json=True):
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {"()": RequestIdFilter},
            "redact": {"()": RedactFilter},
        },
        "formatters": {
            "json": {"()": JsonFormatter},
            "text": {"format": "%(levelname)s %(name)s [%(request_id)s] %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": stream or sys.stderr,
                "formatter": "json" if json else "text",
                # On the handler, so records propagating from every logger pass through them.
                "filters": ["request_id", "redact"],
            },
        },
        "root": {"level": level, "handlers": ["console"]},
    })


@contextmanager
def log_duration(logger, action, *, clock=time.perf_counter):
    start = clock()
    try:
        yield
    except BaseException:
        ms = round((clock() - start) * 1000)
        logger.error("%s failed after %d ms", action, ms, exc_info=True,
                     extra={"action": action, "duration_ms": ms})
        raise
    ms = round((clock() - start) * 1000)
    logger.info("%s finished in %d ms", action, ms, extra={"action": action, "duration_ms": ms})


if __name__ == "__main__":
    configure_logging("DEBUG")
    log = logging.getLogger("shop.orders")
    with request_context("7f3a"):
        log.info("login user=ada password=hunter2")
        with log_duration(log, "checkout"):
            time.sleep(0.05)
