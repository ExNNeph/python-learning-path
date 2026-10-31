"""Tests for assignment 02. Run: pytest professional/02-code-quality-tools/assignments/02-mini-linter -v"""

import dataclasses
import textwrap

import pytest


def codes(ex, source, **kwargs):
    return [(f.line, f.col, f.code) for f in ex.lint(textwrap.dedent(source), **kwargs)]


DEMO = '''
import os, sys
def add(item, items=[]):
    try:
        items.append(item)
    except:
        print("failed")
    return items if sys.argv != None else None
'''


# --- Finding -------------------------------------------------------------------

def test_finding_is_frozen_and_ordered(ex):
    a = ex.Finding(2, 5, "PLP004", "print found")
    b = ex.Finding(2, 1, "PLP002", "bare except")
    c = ex.Finding(1, 9, "PLP001", "x")
    assert sorted([a, b, c]) == [c, b, a]
    with pytest.raises(dataclasses.FrozenInstanceError):
        a.line = 3


# --- the whole demo ------------------------------------------------------------

def test_demo(ex):
    assert ex.lint(DEMO) == [
        ex.Finding(2, 1, "PLP001", "'os' imported but unused"),
        ex.Finding(3, 21, "PLP003", "mutable default argument in 'add'"),
        ex.Finding(6, 5, "PLP002", "bare except"),
        ex.Finding(7, 9, "PLP004", "print found"),
        ex.Finding(8, 21, "PLP005", "comparison to None: use 'is' or 'is not'"),
    ]


def test_clean_code_has_no_findings(ex):
    source = """
    import json
    from pathlib import Path

    def load(path, default=None, *, keys=()):
        try:
            return json.loads(Path(path).read_text())
        except (OSError, ValueError):
            return default if default is not None else {}
    """
    assert codes(ex, source) == []


# --- PLP001 unused imports -----------------------------------------------------

def test_unused_import_forms(ex):
    source = """
    import os.path
    import numpy as np
    from collections import OrderedDict as OD, Counter
    from typing import Any
    Counter()
    """
    messages = [f.message for f in ex.lint(textwrap.dedent(source))]
    assert messages == [
        "'os' imported but unused",
        "'np' imported but unused",
        "'OD' imported but unused",
        "'Any' imported but unused",
    ]


def test_import_used_as_attribute_root_or_inside_function(ex):
    source = """
    import os
    import sys
    def where():
        return os.getcwd()
    print_to = sys.stderr
    """
    assert codes(ex, source) == []


def test_import_listed_in_all_is_used(ex):
    source = """
    from .text import slugify, word_count
    from .stats import top_words
    __all__ = ["slugify", "top_words"]
    """
    assert [f.message for f in ex.lint(textwrap.dedent(source))] == ["'word_count' imported but unused"]


def test_future_imports_are_never_reported(ex):
    assert codes(ex, "from __future__ import annotations\n") == []


def test_unused_import_position_is_the_statement(ex):
    assert codes(ex, "x = 1\nif x:\n    import re\n") == [(3, 5, "PLP001")]


# --- PLP002 bare except --------------------------------------------------------

def test_bare_except(ex):
    source = """
    try:
        pass
    except ValueError:
        pass
    except:
        pass
    """
    assert codes(ex, source) == [(6, 1, "PLP002")]


def test_bare_except_nested(ex):
    source = """
    def f():
        try:
            pass
        except Exception:
            try:
                pass
            except:
                pass
    """
    assert codes(ex, source) == [(8, 9, "PLP002")]


# --- PLP003 mutable defaults ---------------------------------------------------

def test_mutable_defaults(ex):
    source = """
    def f(a, b=[], c={}, d={1}, e=list(), f=dict(), g=set(), h=(), i=None, j=frozenset()):
        pass
    """
    found = ex.lint(textwrap.dedent(source))
    assert [(f.col, f.code) for f in found] == [(12, "PLP003"), (18, "PLP003"), (24, "PLP003"),
                                               (31, "PLP003"), (41, "PLP003"), (51, "PLP003")]
    assert {f.message for f in found} == {"mutable default argument in 'f'"}


def test_mutable_keyword_only_and_async_and_methods(ex):
    source = """
    async def fetch(url, *, headers={}, retries=3):
        pass

    class Cart:
        def add(self, item, into=[]):
            pass
    """
    found = ex.lint(textwrap.dedent(source))
    assert [(f.line, f.message) for f in found] == [
        (2, "mutable default argument in 'fetch'"),
        (6, "mutable default argument in 'add'"),
    ]


# --- PLP004 print --------------------------------------------------------------

def test_print_calls_only(ex):
    source = """
    print("a")
    logger.print("b")
    p = print
    def f():
        return print(1, 2)
    """
    assert codes(ex, source) == [(2, 1, "PLP004"), (6, 12, "PLP004")]


# --- PLP005 None comparison ----------------------------------------------------

def test_none_comparisons(ex):
    source = """
    if a == None: pass
    if b != None: pass
    if c is None: pass
    if d == 0: pass
    if 1 < e == None: pass
    """
    assert codes(ex, source) == [(2, 4, "PLP005"), (3, 4, "PLP005"), (6, 4, "PLP005")]


def test_nested_comparisons_are_found(ex):
    assert codes(ex, "result = f(x == None)\n") == [(1, 12, "PLP005")]


# --- select and noqa -----------------------------------------------------------

def test_select(ex):
    assert [f.code for f in ex.lint(DEMO, select=["PLP004", "PLP002"])] == ["PLP002", "PLP004"]
    assert [f.code for f in ex.lint(DEMO, select={"PLP001"})] == ["PLP001"]
    assert ex.lint(DEMO, select=[]) == []


def test_bare_noqa_silences_the_whole_line(ex):
    assert codes(ex, "print(x == None)  # noqa\nprint(1)\n") == [(2, 1, "PLP004")]


def test_noqa_with_codes(ex):
    source = "print(x == None)  # noqa: PLP004\nprint(2)  # noqa: PLP001, PLP004\nprint(3)  #noqa:PLP002\n"
    assert codes(ex, source) == [(1, 7, "PLP005"), (3, 1, "PLP004")]


def test_noqa_on_import_line(ex):
    source = "import os  # noqa: PLP001\nimport sys\n"
    assert codes(ex, source) == [(2, 1, "PLP001")]


# --- syntax errors -------------------------------------------------------------

def test_syntax_error_gives_one_finding(ex):
    source = "x = 1\ndef f(:\n    pass\n"
    try:
        compile(source, "<test>", "exec")
    except SyntaxError as error:
        expected = ex.Finding(error.lineno, error.offset, "PLP000", f"syntax error: {error.msg}")
    assert ex.lint(source) == [expected]
    assert expected.line == 2


# --- formatting and the command line -------------------------------------------

def test_format_finding(ex):
    finding = ex.Finding(7, 9, "PLP004", "print found")
    assert ex.format_finding("src/app.py", finding) == "src/app.py:7:9: PLP004 print found"


def test_main_reports_and_returns_1(ex, tmp_path, capsys):
    demo = tmp_path / "demo.py"
    demo.write_text(DEMO, encoding="utf-8")
    clean = tmp_path / "clean.py"
    clean.write_text("x = 1\n", encoding="utf-8")
    assert ex.main([str(clean), str(demo)]) == 1
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 6
    assert lines[0] == f"{demo}:2:1: PLP001 'os' imported but unused"
    assert lines[-1] == "Found 5 problem(s)."


def test_main_select(ex, tmp_path, capsys):
    demo = tmp_path / "demo.py"
    demo.write_text(DEMO, encoding="utf-8")
    assert ex.main(["--select", "PLP004", str(demo)]) == 1
    assert capsys.readouterr().out.splitlines() == [f"{demo}:7:9: PLP004 print found", "Found 1 problem(s)."]


def test_main_clean_returns_0(ex, tmp_path, capsys):
    clean = tmp_path / "clean.py"
    clean.write_text("import os\nprint(os.sep)  # noqa: PLP004\n", encoding="utf-8")
    assert ex.main([str(clean)]) == 0
    assert capsys.readouterr().out == "All checks passed.\n"


def test_main_usage_error(ex, capsys):
    with pytest.raises(SystemExit) as exit_info:
        ex.main([])
    assert exit_info.value.code == 2
