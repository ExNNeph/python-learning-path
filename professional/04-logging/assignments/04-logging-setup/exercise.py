"""Assignment 04 · Logging setup.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest professional/04-logging/assignments/04-logging-setup -v
"""

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
        """One line of JSON: time, level, logger, message, extra fields, exception."""
        raise NotImplementedError


class RedactFilter(logging.Filter):
    def __init__(self, keys=("password", "token", "api_key")):
        super().__init__()
        raise NotImplementedError

    def filter(self, record):
        """Mask key=value secrets in the message and secret extra fields; keep the record."""
        raise NotImplementedError


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        """Copy the current request id onto the record."""
        raise NotImplementedError


@contextmanager
def request_context(rid=None):
    """Set the request id (a new 8-character id if None) for the duration of the block."""
    raise NotImplementedError
    yield


def configure_logging(level="INFO", *, stream=None, json=True):
    """Configure the root logger with dictConfig: one stream handler, both filters, JSON or text."""
    raise NotImplementedError


@contextmanager
def log_duration(logger, action, *, clock=time.perf_counter):
    """Log how long the block took (INFO), or that it failed (ERROR with traceback, re-raised)."""
    raise NotImplementedError
    yield


if __name__ == "__main__":
    configure_logging("DEBUG")
    log = logging.getLogger("shop.orders")
    with request_context("7f3a"):
        log.info("login user=ada password=hunter2")
        with log_duration(log, "checkout"):
            time.sleep(0.05)
