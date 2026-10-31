"""Tests for assignment 13. Run: pytest advanced/12-packaging/assignments/13-package-split -v

These tests do not use the `ex` fixture: they import the package `wordtools` from the assignment
folder (or from the solution folder when PLP_SOLUTIONS=1) and look at its files.
"""

import importlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROJECT = ROOT / "solutions" / HERE.relative_to(ROOT) if os.environ.get("PLP_SOLUTIONS") == "1" else HERE
PACKAGE = PROJECT / "wordtools"
SAMPLE = "the cat and the hat. The bat sat on the cat!"


@pytest.fixture
def wordtools(monkeypatch):
    """Import wordtools fresh from the project folder."""
    for name in list(sys.modules):
        if name == "wordtools" or name.startswith("wordtools."):
            monkeypatch.delitem(sys.modules, name)
    monkeypatch.syspath_prepend(str(PROJECT))
    assert (PACKAGE / "__init__.py").is_file(), f"create the package: {PACKAGE.relative_to(ROOT)}/__init__.py"
    return importlib.import_module("wordtools")


def source(name):
    return (PACKAGE / name).read_text(encoding="utf-8")


def run_module(*args):
    return subprocess.run(
        [sys.executable, "-m", "wordtools", *args],
        cwd=PROJECT, capture_output=True, text=True, timeout=60,
    )


# --- structure -------------------------------------------------------------------

@pytest.mark.parametrize("name", ["__init__.py", "__main__.py", "text.py", "stats.py", "cli.py"])
def test_module_exists(name):
    assert (PACKAGE / name).is_file(), f"missing wordtools/{name}"


def test_text_is_the_lowest_layer(wordtools):
    text = source("text.py")
    assert "from ." not in text and "import wordtools" not in text and "from wordtools" not in text
    assert callable(importlib.import_module("wordtools.text").words)


def test_stats_imports_text_relatively(wordtools):
    stats = source("stats.py")
    assert "from .text import" in stats or "from . import text" in stats
    assert "def words" not in stats


def test_functions_live_in_their_modules(wordtools):
    assert wordtools.slugify.__module__ == "wordtools.text"
    assert wordtools.word_count.__module__ == "wordtools.text"
    assert wordtools.top_words.__module__ == "wordtools.stats"
    assert importlib.import_module("wordtools.cli").main.__module__ == "wordtools.cli"


# --- public API ----------------------------------------------------------------------

def test_public_api(wordtools):
    assert sorted(wordtools.__all__) == ["slugify", "top_words", "word_count"]
    assert wordtools.__version__ == "1.0.0"


def test_functions_still_work(wordtools):
    assert wordtools.slugify("Hello, World! It's me") == "hello-world-its-me"
    assert wordtools.word_count(SAMPLE) == 11
    assert wordtools.top_words(SAMPLE, 2) == [("the", 4), ("cat", 2)]


# --- running ----------------------------------------------------------------------------

def test_python_m_slug(wordtools):
    result = run_module("slug", "Packaging", "is", "fun!")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "packaging-is-fun\n"


def test_python_m_top(wordtools, tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text(SAMPLE, encoding="utf-8")
    result = run_module("top", str(sample), "-n", "2")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "the 4\ncat 2\n"


def test_python_m_error_exit_code(wordtools, tmp_path):
    result = run_module("count", str(tmp_path / "missing.txt"))
    assert result.returncode == 1
    assert result.stderr.startswith("wordtools: error:")


def test_python_m_version(wordtools):
    assert run_module("--version").stdout.strip() == "wordtools 1.0.0"


def test_cli_main_is_testable(wordtools, capsys):
    cli = importlib.import_module("wordtools.cli")
    assert cli.main(["slug", "A", "B"]) == 0
    assert capsys.readouterr().out == "a-b\n"


# --- pyproject.toml ---------------------------------------------------------------------

@pytest.fixture
def pyproject():
    tomllib = pytest.importorskip("tomllib")
    path = PROJECT / "pyproject.toml"
    assert path.is_file(), "create pyproject.toml next to exercise.py"
    with open(path, "rb") as file:
        return tomllib.load(file)


def test_pyproject_build_system(pyproject):
    build = pyproject["build-system"]
    assert build["build-backend"] == "setuptools.build_meta"
    assert any(req.startswith("setuptools") for req in build["requires"])


def test_pyproject_metadata(pyproject, wordtools):
    project = pyproject["project"]
    assert project["name"] == "wordtools"
    assert project["version"] == wordtools.__version__
    assert project["requires-python"].replace(" ", "") == ">=3.10"


def test_pyproject_entry_point(pyproject, wordtools):
    target = pyproject["project"]["scripts"]["wordtools"]
    module_name, _, function_name = target.partition(":")
    assert (module_name, function_name) == ("wordtools.cli", "main")
    assert callable(getattr(importlib.import_module(module_name), function_name))


def test_pyproject_packages(pyproject):
    assert pyproject["tool"]["setuptools"]["packages"] == ["wordtools"]


# --- the shim ------------------------------------------------------------------------------

def load_shim():
    spec = importlib.util.spec_from_file_location("exercise_shim", PROJECT / "exercise.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shim_reexports_the_same_objects(wordtools):
    with pytest.warns(DeprecationWarning):
        shim = load_shim()
    assert shim.slugify is wordtools.slugify
    assert shim.word_count is wordtools.word_count
    assert shim.top_words is wordtools.top_words
    assert shim.__version__ == "1.0.0"


def test_shim_warns(wordtools):
    with pytest.warns(DeprecationWarning, match="use 'wordtools' instead"):
        load_shim()


def test_shim_has_no_code_of_its_own(wordtools):
    text = (PROJECT / "exercise.py").read_text(encoding="utf-8")
    assert "def " not in text and "import argparse" not in text
