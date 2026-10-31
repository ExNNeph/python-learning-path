"""Tests for assignment 13. Run: pytest professional/13-code-review-and-documentation/assignments/13-review-fixes -v"""

import ast
import datetime
import doctest
import inspect
import time
import warnings

import pytest

PUBLIC = ["add_line", "total", "find_duplicates", "parse_amount", "due_date", "calc"]


def line(description, price_cents=100, qty=1):
    return {"description": description, "price_cents": price_cents, "qty": qty}


# --- 1 · add_line --------------------------------------------------------------

def test_add_line_signature(ex):
    parameters = inspect.signature(ex.add_line).parameters
    assert list(parameters) == ["lines", "description", "price_cents", "qty"]
    assert [p.default for p in parameters.values()][:3] == [inspect.Parameter.empty] * 3
    assert parameters["qty"].default == 1


def test_add_line_returns_a_new_list(ex):
    original = [line("Mort", 1250)]
    result = ex.add_line(original, "Dune", 990, qty=2)
    assert result == [line("Mort", 1250), line("Dune", 990, 2)]
    assert original == [line("Mort", 1250)]                  # unchanged
    assert result is not original


def test_add_line_calls_do_not_share_state(ex):
    a = ex.add_line([], "A", 1)
    b = ex.add_line([], "B", 2)
    assert a == [line("A", 1)] and b == [line("B", 2)]


# --- 2 · total -----------------------------------------------------------------

@pytest.mark.parametrize("lines, tax, expected", [
    ([line("Mort", 1000, 2)], 19, 2380),
    ([line("Pen", 50)], 7, 54),                              # 53.5 rounds up
    ([line("Pen", 1000)], 7, 1070),
    ([line("A", 10), line("B", 20)], 0, 30),
    ([], 19, 0),
    ([line("X", 1)], 50, 2),                                 # 1.5 rounds up
    ([line("X", 1)], 49, 1),                                 # 1.49 rounds down
    ([line("Coffee", 333, 3)], 19, 1189),                    # 999 * 1.19 = 1188.81
])
def test_total_in_cents(ex, lines, tax, expected):
    result = ex.total(lines, tax_percent=tax)
    assert result == expected and type(result) is int


def test_total_default_tax(ex):
    assert ex.total([line("Mort", 1000)]) == 1190


def test_total_is_exact_for_large_amounts(ex):
    lines = [line("Server", 10**15 + 1, 3)]                  # floats lose cents at this size
    assert ex.total(lines, tax_percent=19) == ((3 * (10**15 + 1)) * 119 + 50) // 100


# --- 3 · find_duplicates -------------------------------------------------------

def test_find_duplicates_first_appearance_order(ex):
    lines = [line(d) for d in ["Pen", "Mort", "Pen", "Dune", "Mort", "Pen", "Ink"]]
    assert ex.find_duplicates(lines) == ["Pen", "Mort"]


def test_find_duplicates_none(ex):
    assert ex.find_duplicates([line("A"), line("B")]) == []
    assert ex.find_duplicates([]) == []


def test_find_duplicates_order_is_by_first_appearance_not_by_second(ex):
    lines = [line(d) for d in ["A", "B", "B", "A"]]
    assert ex.find_duplicates(lines) == ["A", "B"]


def test_find_duplicates_is_fast(ex):
    # Small enough that the O(n²) starter finishes (in a few seconds), big enough to tell them apart.
    lines = [line(f"item {i % 3_000}") for i in range(6_000)]
    start = time.perf_counter()
    result = ex.find_duplicates(lines)
    assert time.perf_counter() - start < 0.5
    assert len(result) == 3_000 and result[:2] == ["item 0", "item 1"]


# --- 4 · parse_amount ----------------------------------------------------------

@pytest.mark.parametrize("text, cents", [
    ("12", 1200), ("12.5", 1250), ("12,50", 1250), ("0.05", 5), (" 7.5 ", 750), ("1234.99", 123499), ("0", 0),
])
def test_parse_amount(ex, text, cents):
    result = ex.parse_amount(text)
    assert result == cents and type(result) is int


@pytest.mark.parametrize("text", ["", "twelve", "-5", "12.505", "1.234,50", "12.", ".5", "12 50", "1e3", "١٢"])
def test_parse_amount_rejects(ex, text):
    with pytest.raises(ValueError) as info:
        ex.parse_amount(text)
    assert str(info.value) == f"not an amount: {text!r}"


def test_parse_amount_has_no_bare_except(ex):
    tree = ast.parse(inspect.getsource(ex.parse_amount))
    assert not any(isinstance(n, ast.ExceptHandler) and n.type is None for n in ast.walk(tree))


# --- 5 · due_date --------------------------------------------------------------

D = datetime.date


@pytest.mark.parametrize("issued, days, expected", [
    (D(2026, 11, 2), 30, D(2026, 12, 2)),                    # Wednesday: unchanged
    (D(2026, 11, 1), 13, D(2026, 11, 16)),                   # Saturday → Monday
    (D(2026, 11, 1), 14, D(2026, 11, 16)),                   # Sunday → Monday
    (D(2026, 11, 1), 12, D(2026, 11, 13)),                   # Friday: unchanged
    (D(2026, 11, 1), 0, D(2026, 11, 2)),                     # issued on a Sunday, due at once
    (D(2026, 12, 26), 0, D(2026, 12, 28)),                   # Saturday, across into the next week
])
def test_due_date(ex, issued, days, expected):
    assert ex.due_date(issued, days=days) == expected


def test_due_date_default(ex):
    assert ex.due_date(D(2026, 11, 2)) == D(2026, 12, 2)


def test_due_date_negative(ex):
    with pytest.raises(ValueError):
        ex.due_date(D(2026, 11, 2), days=-1)


# --- 6 · calc ------------------------------------------------------------------

def test_calc_still_works_but_warns(ex):
    with pytest.warns(DeprecationWarning, match=r"calc\(\) is deprecated, use total\(\)") as record:
        assert ex.calc([line("Mort", 1000)]) == 1190
    assert record[0].filename == __file__                    # stacklevel=2: points at THIS line


def test_total_does_not_warn(ex):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        ex.total([line("Mort", 1000)])


# --- 7 · documentation ---------------------------------------------------------

def test_module_docstring(ex):
    assert ex.__doc__ and ex.__doc__.strip()
    assert "seven review comments" not in ex.__doc__, "replace the assignment text with your own module docstring"


@pytest.mark.parametrize("name", PUBLIC)
def test_public_functions_have_docstrings(ex, name):
    doc = getattr(ex, name).__doc__
    assert doc and len(doc.strip()) >= 10, f"{name} needs a docstring"


def test_doctests_exist_and_pass(ex):
    finder = doctest.DocTestFinder()
    with_examples = {
        test.name.rsplit(".", 1)[-1]
        for test in finder.find(ex)
        if test.examples
    }
    assert len(with_examples & set(PUBLIC)) >= 5, f"doctest examples found only in: {sorted(with_examples)}"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = doctest.testmod(ex, verbose=False, report=False)
    assert result.failed == 0
