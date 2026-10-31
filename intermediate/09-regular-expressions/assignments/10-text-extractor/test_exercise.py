"""Tests for assignment 10. Run: pytest intermediate/09-regular-expressions/assignments/10-text-extractor -v"""

import pytest


def test_find_emails(ex):
    text = "Mail ada.l+news@math.example.org or grace@navy.mil, not bob@localhost."
    assert ex.find_emails(text) == ["ada.l+news@math.example.org", "grace@navy.mil"]


@pytest.mark.parametrize("text, expected", [
    ("", []),
    ("no addresses here", []),
    ("at the end: linus@kernel.org.", ["linus@kernel.org"]),
    ("<ken_t@bell-labs.com>", ["ken_t@bell-labs.com"]),
    ("a@b.c is too short a TLD", []),
    ("first@one.de,second@two.io", ["first@one.de", "second@two.io"]),
])
def test_find_emails_edge_cases(ex, text, expected):
    assert ex.find_emails(text) == expected


@pytest.mark.parametrize("name", ["ada", "ada_1815", "Grace_Hopper", "a" * 16, "x__"])
def test_valid_usernames(ex, name):
    assert ex.is_valid_username(name) is True


@pytest.mark.parametrize("name", ["", "ad", "1ada", "_ada", "a" * 17, "ada lovelace", "ada!", "ada-l", " ada"])
def test_invalid_usernames(ex, name):
    assert ex.is_valid_username(name) is False


def test_dates_to_iso(ex):
    assert ex.dates_to_iso("Born 10.12.1815, died 27.11.1852") == "Born 1815-12-10, died 1852-11-27"


@pytest.mark.parametrize("text", ["no dates", "version 1.2.3", "1.12.2026 has one digit", "10.12.18150"])
def test_dates_to_iso_leaves_other_text(ex, text):
    assert ex.dates_to_iso(text) == text


def test_parse_log_line(ex):
    assert ex.parse_log_line("2026-10-31 14:30:05 [ERROR] db: connection lost") == {
        "date": "2026-10-31", "time": "14:30:05", "level": "ERROR",
        "source": "db", "message": "connection lost",
    }


def test_parse_log_line_message_keeps_colons(ex):
    result = ex.parse_log_line("2026-01-01 00:00:00 [INFO] web: GET /a: 200 OK\n")
    assert result["source"] == "web"
    assert result["message"] == "GET /a: 200 OK"


@pytest.mark.parametrize("line", [
    "",
    "just text",
    "2026-10-31 14:30 [ERROR] db: short time",
    "2026-10-31 14:30:05 ERROR db: no brackets",
    "2026-10-31 14:30:05 [error] db: lower-case level",
    "2026-10-31 14:30:05 [ERROR] no source here",
])
def test_parse_log_line_no_match(ex, line):
    assert ex.parse_log_line(line) is None


def test_hashtags(ex):
    assert ex.hashtags("Learning #Python! #regex is fun. #python #Py3") == ["python", "regex", "py3"]
    assert ex.hashtags("no tags # here") == []


def test_squash_whitespace(ex):
    assert ex.squash_whitespace("  too   many\n\tspaces ") == "too many spaces"
    assert ex.squash_whitespace("") == ""
    assert ex.squash_whitespace("one") == "one"


def test_mask_card_numbers(ex):
    text = "Card 4111-1111-1111-1234, backup 5500000000000004."
    assert ex.mask_card_numbers(text) == "Card **** **** **** 1234, backup **** **** **** 0004."
    assert ex.mask_card_numbers("4111 1111 1111 9876") == "**** **** **** 9876"


@pytest.mark.parametrize("text", [
    "order 123456789012345",          # 15 digits
    "id 12345678901234567",           # 17 digits
    "4111  1111 1111 1234",           # two spaces
    "phone 0176 1234 5678",
])
def test_mask_card_numbers_leaves_other_numbers(ex, text):
    assert ex.mask_card_numbers(text) == text
