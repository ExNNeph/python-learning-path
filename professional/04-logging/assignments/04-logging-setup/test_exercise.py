"""Tests for assignment 04. Run: pytest professional/04-logging/assignments/04-logging-setup -v"""

import io
import json
import logging
import re
import sys
import threading
from datetime import datetime, timezone

import pytest


@pytest.fixture(autouse=True)
def restore_root_logger():
    """configure_logging changes the global root logger: put it back after every test."""
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers[:] = handlers
    root.setLevel(level)


@pytest.fixture
def stream():
    return io.StringIO()


def lines(stream):
    return stream.getvalue().splitlines()


def records(stream):
    return [json.loads(line) for line in lines(stream)]


def make_record(msg="hello %s", args=("world",), level=logging.INFO, name="shop", exc_info=None, **extra):
    record = logging.LogRecord(name, level, "shop.py", 10, msg, args, exc_info)
    record.__dict__.update(extra)
    return record


# --- JsonFormatter -------------------------------------------------------------

def test_json_formatter_basic_fields(ex):
    record = make_record()
    record.created = datetime(2026, 11, 1, 9, 30, 0, 123000, tzinfo=timezone.utc).timestamp()
    line = ex.JsonFormatter().format(record)
    assert "\n" not in line
    assert json.loads(line) == {
        "time": "2026-11-01T09:30:00.123+00:00",
        "level": "INFO",
        "logger": "shop",
        "message": "hello world",
    }
    assert list(json.loads(line)) == ["time", "level", "logger", "message"]


def test_json_formatter_extra_fields_follow_the_message(ex):
    record = make_record(order_id=1042, amount_cents=2495)
    data = json.loads(ex.JsonFormatter().format(record))
    assert list(data) == ["time", "level", "logger", "message", "order_id", "amount_cents"]
    assert (data["order_id"], data["amount_cents"]) == (1042, 2495)


def test_json_formatter_unencodable_values_become_strings(ex):
    record = make_record(when=datetime(2026, 1, 2, tzinfo=timezone.utc), tags={"a"})
    data = json.loads(ex.JsonFormatter().format(record))
    assert data["when"] == "2026-01-02 00:00:00+00:00"
    assert data["tags"] == "{'a'}"


def test_json_formatter_exception(ex):
    try:
        1 / 0
    except ZeroDivisionError:
        record = make_record("failed", (), logging.ERROR, exc_info=sys.exc_info())
    data = json.loads(ex.JsonFormatter().format(record))
    assert list(data)[-1] == "exception"
    assert data["exception"].startswith("Traceback (most recent call last):")
    assert data["exception"].endswith("ZeroDivisionError: division by zero")


# --- RedactFilter --------------------------------------------------------------

def test_redact_message(ex):
    record = make_record("login user=%s password=%s TOKEN=%s", ("ada", "hunter2", "abc.def"))
    assert ex.RedactFilter().filter(record) is True
    assert record.getMessage() == "login user=ada password=*** TOKEN=***"


def test_redact_leaves_clean_messages_alone(ex):
    record = make_record("order %s placed", (1042,))
    assert ex.RedactFilter().filter(record) is True
    assert record.getMessage() == "order 1042 placed"
    assert (record.msg, record.args) == ("order %s placed", (1042,))


def test_redact_extra_fields(ex):
    record = make_record(api_key="sk-123", Password="x", user="ada")
    ex.RedactFilter().filter(record)
    assert (record.api_key, record.Password, record.user) == ("***", "***", "ada")


def test_redact_custom_keys(ex):
    record = make_record("pin=%s password=%s", ("1234", "visible"), pin_code="9")
    ex.RedactFilter(keys=("pin", "pin_code")).filter(record)
    assert record.getMessage() == "pin=*** password=visible"
    assert record.pin_code == "***"


def test_redact_whole_words_only(ex):
    record = make_record("mytoken=abc token=def", ())
    ex.RedactFilter().filter(record)
    assert record.getMessage() == "mytoken=abc token=***"


# --- request ids ---------------------------------------------------------------

def test_request_id_filter(ex):
    record = make_record()
    assert ex.RequestIdFilter().filter(record) is True
    assert record.request_id == "-"
    with ex.request_context("abc"):
        record = make_record()
        ex.RequestIdFilter().filter(record)
        assert record.request_id == "abc"


def test_request_context_restores_and_nests(ex):
    with ex.request_context("outer") as outer:
        assert outer == "outer"
        with ex.request_context("inner"):
            assert ex.request_id.get() == "inner"
        assert ex.request_id.get() == "outer"
    assert ex.request_id.get() == "-"


def test_request_context_restores_after_an_error(ex):
    with pytest.raises(KeyError):
        with ex.request_context("x"):
            raise KeyError
    assert ex.request_id.get() == "-"


def test_request_context_generates_ids(ex):
    with ex.request_context() as first:
        assert re.fullmatch(r"[0-9a-f]{8}", first)
        assert ex.request_id.get() == first
    with ex.request_context() as second:
        assert second != first


def test_request_ids_are_per_thread(ex):
    seen = {}

    def work(name):
        with ex.request_context(name):
            barrier.wait()                       # both threads are inside their context now
            seen[name] = ex.request_id.get()

    barrier = threading.Barrier(2)
    threads = [threading.Thread(target=work, args=(n,)) for n in ("a", "b")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert seen == {"a": "a", "b": "b"}


# --- configure_logging ---------------------------------------------------------

def test_configure_json(ex, stream):
    ex.configure_logging("INFO", stream=stream)
    log = logging.getLogger("shop.orders")
    with ex.request_context("7f3a"):
        log.info("login user=ada password=hunter2")
    log.debug("hidden")
    log.warning("low stock", extra={"sku": "B-1"})
    assert [(r["level"], r["logger"], r["message"], r["request_id"]) for r in records(stream)] == [
        ("INFO", "shop.orders", "login user=ada password=***", "7f3a"),
        ("WARNING", "shop.orders", "low stock", "-"),
    ]
    assert records(stream)[1]["sku"] == "B-1"


def test_configure_text(ex, stream):
    ex.configure_logging("DEBUG", stream=stream, json=False)
    log = logging.getLogger("shop.cache")
    log.debug("cache miss for %s", "rates", extra={"token": "abc123"})
    with ex.request_context("r1"):
        log.error("token=%s rejected", "abc123")
    assert lines(stream) == [
        "DEBUG shop.cache [-] cache miss for rates",
        "ERROR shop.cache [r1] token=*** rejected",
    ]


def test_configure_keeps_existing_loggers(ex, stream):
    early = logging.getLogger("created.before.configuration")
    ex.configure_logging(stream=stream, json=False)
    early.info("still here")
    assert lines(stream) == ["INFO created.before.configuration [-] still here"]


def test_configure_twice_does_not_duplicate(ex, stream):
    ex.configure_logging(stream=io.StringIO())
    ex.configure_logging(stream=stream, json=False)
    logging.getLogger("x").warning("once")
    assert lines(stream) == ["WARNING x [-] once"]


def test_configure_uses_dictconfig_on_the_root_logger(ex, stream, monkeypatch):
    calls = []
    real = logging.config.dictConfig
    monkeypatch.setattr(logging.config, "dictConfig", lambda config: (calls.append(config), real(config)))
    ex.configure_logging("WARNING", stream=stream)
    assert len(calls) == 1
    root = logging.getLogger()
    assert root.level == logging.WARNING
    assert len(root.handlers) == 1
    handler = root.handlers[0]
    assert isinstance(handler, logging.StreamHandler) and handler.stream is stream
    assert [type(f).__name__ for f in handler.filters] == ["RequestIdFilter", "RedactFilter"]
    assert isinstance(handler.formatter, ex.JsonFormatter)


# --- log_duration --------------------------------------------------------------

class FakeClock:
    def __init__(self, *times):
        self.times = list(times)

    def __call__(self):
        return self.times.pop(0)


def test_log_duration_success(ex, stream):
    ex.configure_logging(stream=stream)
    log = logging.getLogger("shop")
    with ex.log_duration(log, "checkout", clock=FakeClock(10.0, 10.052)):
        pass
    [record] = records(stream)
    assert record["level"] == "INFO"
    assert record["message"] == "checkout finished in 52 ms"
    assert (record["action"], record["duration_ms"]) == ("checkout", 52)


def test_log_duration_failure(ex, stream):
    ex.configure_logging(stream=stream)
    log = logging.getLogger("shop")
    with pytest.raises(ValueError, match="bad card"):
        with ex.log_duration(log, "payment", clock=FakeClock(1.0, 1.2)):
            raise ValueError("bad card")
    [record] = records(stream)
    assert record["level"] == "ERROR"
    assert record["message"] == "payment failed after 200 ms"
    assert (record["action"], record["duration_ms"]) == ("payment", 200)
    assert record["exception"].endswith("ValueError: bad card")


def test_log_duration_real_clock(ex, caplog):
    with caplog.at_level(logging.INFO):
        with ex.log_duration(logging.getLogger("t"), "noop"):
            pass
    assert re.fullmatch(r"noop finished in \d+ ms", caplog.records[0].getMessage())
