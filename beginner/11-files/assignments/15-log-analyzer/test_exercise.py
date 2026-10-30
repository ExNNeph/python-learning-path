"""Tests for assignment 15. Run: pytest beginner/11-files/assignments/15-log-analyzer -v"""

import pytest

LOG = """\
2026-10-30 08:00:01 INFO Server started on port 8080
2026-10-30 08:16:10 ERROR Database timeout after 30 s

#### corrupted ####
2026-10-30 08:20:00 WARNING Disk usage at 85%
2026-10-30 09:02:33 ERROR Payment provider returned 503
2026-10-30 10:00:00 INFO Nightly report sent
"""


@pytest.fixture
def log_file(tmp_path):
    path = tmp_path / "app.log"
    path.write_text(LOG, encoding="utf-8")
    return path


def test_parse_line(ex):
    assert ex.parse_line("2026-10-30 08:16:10 ERROR Database timeout after 30 s\n") == (
        "2026-10-30",
        "08:16:10",
        "ERROR",
        "Database timeout after 30 s",
    )


@pytest.mark.parametrize("line", ["", "\n", "   \n", "#### corrupted ####", "2026-10-30 08:00:00 INFO"])
def test_parse_line_invalid(ex, line):
    assert ex.parse_line(line) is None


def test_count_levels(ex, log_file):
    assert ex.count_levels(log_file) == {"INFO": 2, "ERROR": 2, "WARNING": 1}


def test_count_levels_accepts_string_path(ex, log_file):
    assert ex.count_levels(str(log_file)) == {"INFO": 2, "ERROR": 2, "WARNING": 1}


def test_count_levels_empty_file(ex, tmp_path):
    path = tmp_path / "empty.log"
    path.write_text("", encoding="utf-8")
    assert ex.count_levels(path) == {}


def test_error_messages(ex, log_file):
    assert ex.error_messages(log_file) == ["Database timeout after 30 s", "Payment provider returned 503"]


def test_missing_file_raises(ex, tmp_path):
    with pytest.raises(FileNotFoundError):
        ex.count_levels(tmp_path / "does-not-exist.log")


def test_write_summary(ex, log_file, tmp_path):
    summary = tmp_path / "summary.txt"
    assert ex.write_summary(log_file, summary) is None
    assert summary.read_text(encoding="utf-8") == (
        "ERROR: 2\n"
        "INFO: 2\n"
        "WARNING: 1\n"
        "\n"
        "- Database timeout after 30 s\n"
        "- Payment provider returned 503\n"
    )


def test_write_summary_overwrites(ex, log_file, tmp_path):
    summary = tmp_path / "summary.txt"
    summary.write_text("old content\n", encoding="utf-8")
    ex.write_summary(log_file, summary)
    assert "old content" not in summary.read_text(encoding="utf-8")


def test_unicode_messages(ex, tmp_path):
    path = tmp_path / "unicode.log"
    path.write_text("2026-10-30 08:00:00 ERROR Größe überschritten ✗\n", encoding="utf-8")
    assert ex.error_messages(path) == ["Größe überschritten ✗"]
