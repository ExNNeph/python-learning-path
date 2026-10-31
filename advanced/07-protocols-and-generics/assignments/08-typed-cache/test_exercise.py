"""Tests for assignment 08. Run: pytest advanced/07-protocols-and-generics/assignments/08-typed-cache -v"""

import re
import shutil
import textwrap

import pytest


# --- behaviour: LRUCache -------------------------------------------------------

def test_cache_get_and_put(ex):
    cache = ex.LRUCache(2)
    cache.put("a", 1)
    assert cache.get("a") == 1
    assert cache.get("missing") is None
    assert len(cache) == 1


def test_cache_evicts_least_recently_used(ex):
    cache = ex.LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.items() == [("a", 1), ("c", 3)]
    assert "b" not in cache
    assert cache.get("b") is None


def test_cache_put_existing_key_updates_and_refreshes(ex):
    cache = ex.LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 10)
    cache.put("c", 3)
    assert cache.items() == [("a", 10), ("c", 3)]
    assert len(cache) == 2


def test_cache_contains_is_not_a_use(ex):
    cache = ex.LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert "a" in cache
    cache.put("c", 3)
    assert "a" not in cache


def test_cache_capacity_one(ex):
    cache = ex.LRUCache(1)
    cache.put(1, "x")
    cache.put(2, "y")
    assert cache.items() == [(2, "y")]


def test_cache_invalid_capacity(ex):
    with pytest.raises(ValueError):
        ex.LRUCache(0)


def test_cache_stores_falsy_values(ex):
    cache = ex.LRUCache(3)
    cache.put("zero", 0)
    assert cache.get("zero") == 0
    assert "zero" in cache


# --- behaviour: the rest -------------------------------------------------------

def test_total_area(ex):
    class Square:
        def __init__(self, side):
            self.side = side

        def area(self):
            return self.side ** 2

    class Circle:
        def area(self):
            return 3.0

    assert ex.total_area([Square(2), Circle(), Square(1)]) == 8.0
    assert ex.total_area(Square(n) for n in range(3)) == 5
    assert ex.total_area([]) == 0


def test_largest(ex):
    assert ex.largest([3, 9, 1]) == 9
    assert ex.largest(["pear", "fig", "plum"]) == "plum"
    assert ex.largest(x for x in (2.5, 1.0)) == 2.5


def test_largest_empty(ex):
    with pytest.raises(ValueError):
        ex.largest([])


def test_logged(ex):
    entries = []

    @ex.logged(entries)
    def add(a, b=0):
        """Add."""
        return a + b

    assert add(1, b=2) == 3
    assert add(5) == 5
    assert add("x", "y") == "xy"
    assert entries == ["add(1, b=2) -> 3", "add(5) -> 5", "add('x', 'y') -> 'xy'"]
    assert (add.__name__, add.__doc__) == ("add", "Add.")


def test_logged_separate_logs(ex):
    first, second = [], []

    @ex.logged(first)
    def one():
        return 1

    @ex.logged(second)
    def two():
        return None

    one(), two(), one()
    assert first == ["one() -> 1", "one() -> 1"]
    assert second == ["two() -> None"]


def test_convert(ex):
    assert ex.convert("42", "int") == 42
    assert isinstance(ex.convert("42", "int"), int)
    assert ex.convert("2.5", "float") == 2.5
    with pytest.raises(ValueError):
        ex.convert("x", "int")


# --- types -----------------------------------------------------------------------

def run_mypy(*args):
    api = pytest.importorskip("mypy.api")
    stdout, stderr, status = api.run(["--strict", "--no-error-summary", *map(str, args)])
    return stdout + stderr, status


def test_mypy_strict(ex, tmp_path):
    output, status = run_mypy(ex.__file__, f"--cache-dir={tmp_path / 'cache'}")
    assert status == 0, "mypy --strict found problems:\n" + output


USAGE = """
    from typedcache import LRUCache, convert, largest, logged, total_area

    cache: LRUCache[str, int] = LRUCache(2)
    reveal_type(cache.get("a"))
    reveal_type(cache.items())
    reveal_type(largest([3, 1]))
    reveal_type(largest(["a", "b"]))
    reveal_type(convert("1", "int"))
    reveal_type(convert("1", "float"))
    entries: list[str] = []

    @logged(entries)
    def add(a: int, b: int = 0) -> int:
        return a + b

    reveal_type(add)

    class Square:
        def area(self) -> float:
            return 4.0

    reveal_type(total_area([Square()]))
"""

EXPECTED = [
    "int | None",
    "list[tuple[str, int]]",
    "int",
    "str",
    "int",
    "float",
    "def (a: int, b: int =) -> int",
    "float",
]

MISUSE = """
    from typedcache import LRUCache, largest, logged, total_area

    cache: LRUCache[str, int] = LRUCache(2)
    cache.put("a", "one")
    cache.put(1, 1)
    largest([object()])
    entries: list[str] = []

    @logged(entries)
    def add(a: int, b: int = 0) -> int:
        return a + b

    add("x")
    total_area([1, 2])
"""


def normalise(revealed):
    revealed = revealed.replace("builtins.", "")
    revealed = re.sub(r"Union\[(.+), None\]", r"\1 | None", revealed)
    return re.sub(r"Optional\[(.+)\]", r"\1 | None", revealed)


@pytest.fixture
def project(ex, tmp_path):
    shutil.copy(ex.__file__, tmp_path / "typedcache.py")
    return tmp_path


def test_users_get_precise_types(project):
    (project / "usage.py").write_text(textwrap.dedent(USAGE))
    output, status = run_mypy(project / "usage.py", f"--cache-dir={project / 'cache'}")
    revealed = [normalise(m) for m in re.findall(r'Revealed type is "(.*)"', output)]
    assert revealed == EXPECTED, output


def test_users_get_errors_for_misuse(project):
    (project / "misuse.py").write_text(textwrap.dedent(MISUSE))
    output, status = run_mypy(project / "misuse.py", f"--cache-dir={project / 'cache'}")
    error_lines = {int(n) for n in re.findall(r"misuse\.py:(\d+): error", output)}
    assert error_lines >= {5, 6, 7, 14, 15}, "mypy should reject every misuse line:\n" + output
