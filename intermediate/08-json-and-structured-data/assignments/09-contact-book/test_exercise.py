"""Tests for assignment 09. Run: pytest intermediate/08-json-and-structured-data/assignments/09-contact-book -v"""

import json
from datetime import date

import pytest


@pytest.fixture
def ada(ex):
    return ex.Contact("Zoë Ada", "zoe@example.com", date(1990, 12, 10), {"math", "family"})


def test_encode(ex):
    text = json.dumps({"when": date(2026, 1, 1), "tags": {"b", "a"}}, default=ex.encode)
    assert text == '{"when": "2026-01-01", "tags": ["a", "b"]}'


def test_encode_rejects_other_types(ex):
    with pytest.raises(TypeError):
        ex.encode(object())
    with pytest.raises(TypeError):
        json.dumps({"x": 1j}, default=ex.encode)


def test_contact_to_dict(ex, ada):
    assert ex.contact_to_dict(ada) == {
        "name": "Zoë Ada",
        "email": "zoe@example.com",
        "birthday": "1990-12-10",
        "tags": ["family", "math"],
    }


def test_contact_to_dict_without_optional_fields(ex):
    assert ex.contact_to_dict(ex.Contact("Linus", "linus@example.org")) == {
        "name": "Linus", "email": "linus@example.org", "birthday": None, "tags": [],
    }


def test_contact_to_dict_is_json_ready(ex, ada):
    json.dumps(ex.contact_to_dict(ada))       # must not raise


def test_contact_from_dict_minimal(ex):
    contact = ex.contact_from_dict({"name": " Linus ", "email": "LINUS@Example.org"})
    assert contact == ex.Contact("Linus", "linus@example.org", None, set())


def test_contact_from_dict_full(ex, ada):
    data = {"name": "Zoë Ada", "email": "zoe@example.com", "birthday": "1990-12-10",
            "tags": ["math", "family"], "nickname": "ignored"}
    assert ex.contact_from_dict(data) == ada


def test_contact_from_dict_null_birthday(ex):
    assert ex.contact_from_dict({"name": "A", "email": "a@b", "birthday": None}).birthday is None


@pytest.mark.parametrize("data, field", [
    ({"email": "a@b"}, "name"),
    ({"name": "  ", "email": "a@b"}, "name"),
    ({"name": 42, "email": "a@b"}, "name"),
    ({"name": "A"}, "email"),
    ({"name": "A", "email": "no-at-sign"}, "email"),
    ({"name": "A", "email": ["a@b"]}, "email"),
    ({"name": "A", "email": "a@b", "birthday": "10.12.1990"}, "birthday"),
    ({"name": "A", "email": "a@b", "birthday": 19901210}, "birthday"),
    ({"name": "A", "email": "a@b", "tags": "math"}, "tags"),
    ({"name": "A", "email": "a@b", "tags": ["math", 7]}, "tags"),
])
def test_contact_from_dict_invalid(ex, data, field):
    with pytest.raises(ValueError, match=field):
        ex.contact_from_dict(data)


@pytest.mark.parametrize("data", [None, [], "Ada"])
def test_contact_from_dict_not_a_dict(ex, data):
    with pytest.raises(ValueError):
        ex.contact_from_dict(data)


def test_round_trip(ex, ada, tmp_path):
    path = tmp_path / "contacts.json"
    contacts = [ada, ex.Contact("Linus", "linus@example.org")]
    ex.save_contacts(path, contacts)
    assert ex.load_contacts(path) == contacts


def test_saved_file_format(ex, ada, tmp_path):
    path = tmp_path / "contacts.json"
    ex.save_contacts(str(path), [ada])
    text = path.read_text(encoding="utf-8")
    assert "Zoë" in text, "use ensure_ascii=False"
    assert '\n  "contacts"' in text, "use indent=2"
    assert json.loads(text) == {"version": 1, "contacts": [ex.contact_to_dict(ada)]}


def test_save_leaves_no_temporary_file(ex, ada, tmp_path):
    ex.save_contacts(tmp_path / "contacts.json", [ada])
    assert [p.name for p in tmp_path.iterdir()] == ["contacts.json"]


def test_save_replaces_existing_file(ex, ada, tmp_path):
    path = tmp_path / "contacts.json"
    ex.save_contacts(path, [ada])
    ex.save_contacts(path, [])
    assert ex.load_contacts(path) == []


def test_load_missing_file(ex, tmp_path):
    assert ex.load_contacts(tmp_path / "nope.json") == []


@pytest.mark.parametrize("content", [
    '{"version": 1, "contacts": [}',
    "",
    '[{"name": "A", "email": "a@b"}]',
    '{"version": 2, "contacts": []}',
    '{"contacts": []}',
    '{"version": 1, "contacts": {"name": "A"}}',
    '{"version": 1, "contacts": [{"name": "A"}]}',
])
def test_load_invalid_files(ex, tmp_path, content):
    path = tmp_path / "contacts.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        ex.load_contacts(path)
