"""Tests for assignment 17. Run: pytest beginner/13-venv-and-pip/assignments/17-requirements-parser -v"""

import pytest


@pytest.mark.parametrize(
    "line, expected",
    [
        ("requests>=2.31", ("requests", ">=2.31")),
        ("Flask_Login == 0.6.3   # auth", ("flask-login", "==0.6.3")),
        ("rich", ("rich", "")),
        ("  NumPy<2\n", ("numpy", "<2")),
        ("django>=4.2, <5", ("django", ">=4.2,<5")),
        ("urllib3!=2.0.0", ("urllib3", "!=2.0.0")),
        ("requests ~= 2.32", ("requests", "~=2.32")),
        ("python_dateutil", ("python-dateutil", "")),
    ],
)
def test_parse_requirement(ex, line, expected):
    assert ex.parse_requirement(line) == expected


@pytest.mark.parametrize("line", ["", "\n", "   ", "# just a comment", "   # indented comment"])
def test_parse_requirement_ignored_lines(ex, line):
    assert ex.parse_requirement(line) is None


def test_parse_requirements(ex):
    text = "# web\nrequests~=2.32\nflask==3.0.3\n\n# tests\npytest>=7  # runner\n"
    assert ex.parse_requirements(text) == {"requests": "~=2.32", "flask": "==3.0.3", "pytest": ">=7"}


def test_parse_requirements_windows_line_endings(ex):
    assert ex.parse_requirements("rich\r\npytest>=7\r\n") == {"rich": "", "pytest": ">=7"}


def test_parse_requirements_empty(ex):
    assert ex.parse_requirements("") == {}


def test_pinned(ex):
    reqs = {"requests": "~=2.32", "flask": "==3.0.3", "black": "==24.8.0", "rich": ""}
    assert ex.pinned(reqs) == ["black", "flask"]


def test_pinned_none(ex):
    assert ex.pinned({"rich": "", "pytest": ">=7"}) == []


def test_diff_requirements(ex):
    old = "flask==2.3\nrequests\npytest>=7\n"
    new = "Flask==3.0.3\nrich\npytest >= 7\n"
    assert ex.diff_requirements(old, new) == {"added": ["rich"], "removed": ["requests"], "changed": ["flask"]}


def test_diff_requirements_no_change(ex):
    text = "rich\npytest>=7\n"
    assert ex.diff_requirements(text, text) == {"added": [], "removed": [], "changed": []}


def test_diff_lists_are_sorted(ex):
    result = ex.diff_requirements("", "zeta\nalpha\nmid\n")
    assert result["added"] == ["alpha", "mid", "zeta"]
