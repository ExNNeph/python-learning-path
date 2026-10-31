"""Tests for assignment 11. Run: pytest intermediate/10-type-hints/assignments/11-typed-gradebook -v"""

import copy
import inspect
import typing

import pytest

FUNCTIONS = ["average", "letter_grade", "parse_record", "best_student", "report", "apply_curve", "grade_answers"]
METHODS = [("ExactScorer", "__init__"), ("ExactScorer", "score"), ("KeywordScorer", "__init__"), ("KeywordScorer", "score")]


def test_type_definitions(ex):
    assert typing.get_args(ex.Grade) == ("A", "B", "C", "D", "F")
    assert typing.get_type_hints(ex.StudentRecord) == {"name": str, "scores": list[float]}
    assert getattr(ex.Scorer, "_is_protocol", False), "Scorer must be a typing.Protocol"


def assert_fully_annotated(func):
    hints = typing.get_type_hints(func)
    params = [p for p in inspect.signature(func).parameters if p != "self"]
    missing = [p for p in params if p not in hints] + ([] if "return" in hints else ["return"])
    assert not missing, f"{func.__qualname__}: missing annotations for {missing}"


@pytest.mark.parametrize("name", FUNCTIONS)
def test_functions_are_annotated(ex, name):
    assert_fully_annotated(getattr(ex, name))


@pytest.mark.parametrize("cls, method", METHODS)
def test_methods_are_annotated(ex, cls, method):
    assert_fully_annotated(getattr(getattr(ex, cls), method))


def test_scorers_do_not_inherit_from_protocol(ex):
    assert ex.Scorer not in ex.ExactScorer.__mro__
    assert ex.Scorer not in ex.KeywordScorer.__mro__


def test_mypy_strict(ex, tmp_path):
    api = pytest.importorskip("mypy.api")
    stdout, stderr, status = api.run([ex.__file__, "--strict", "--no-error-summary", f"--cache-dir={tmp_path}"])
    assert status == 0, "mypy --strict found problems:\n" + stdout + stderr


def test_average(ex):
    assert ex.average([90, 80.5]) == 85.25
    assert ex.average(score for score in (1.0, 2.0, 3.0)) == 2.0


def test_average_empty(ex):
    with pytest.raises(ValueError, match="no scores"):
        ex.average([])


@pytest.mark.parametrize("score, grade", [
    (100, "A"), (90, "A"), (89.99, "B"), (80, "B"), (79.9, "C"), (70, "C"), (60, "D"), (59.9, "F"), (0, "F"),
])
def test_letter_grade(ex, score, grade):
    assert ex.letter_grade(score) == grade


def test_parse_record(ex):
    assert ex.parse_record("Ada: 91, 85.5, 78") == {"name": "Ada", "scores": [91.0, 85.5, 78.0]}
    assert ex.parse_record("  Grace Hopper :99") == {"name": "Grace Hopper", "scores": [99.0]}
    assert ex.parse_record("Linus:") == {"name": "Linus", "scores": []}


@pytest.mark.parametrize("line", ["Ada 91", ": 91", "Ada: 91, ninety", ""])
def test_parse_record_invalid(ex, line):
    with pytest.raises(ValueError):
        ex.parse_record(line)


@pytest.fixture
def records(ex):
    return [ex.parse_record("Ada: 91, 85.5, 78"), ex.parse_record("Grace: 99, 98"), ex.parse_record("Linus:")]


def test_best_student(ex, records):
    assert ex.best_student(records) == "Grace"
    assert ex.best_student([{"name": "Linus", "scores": []}]) is None
    assert ex.best_student([]) is None


def test_report(ex, records):
    assert ex.report(records) == {"Ada": "B", "Grace": "A"}


def test_apply_curve(ex, records):
    original = copy.deepcopy(records)
    curved = ex.apply_curve(records, lambda s: s + 5)
    assert curved == [
        {"name": "Ada", "scores": [96.0, 90.5, 83.0]},
        {"name": "Grace", "scores": [100.0, 100.0]},
        {"name": "Linus", "scores": []},
    ]
    assert records == original


def test_exact_scorer(ex):
    scorer = ex.ExactScorer("PARIS")
    assert scorer.score(" paris ") == 100.0
    assert scorer.score("Rome") == 0.0


def test_keyword_scorer(ex):
    scorer = ex.KeywordScorer(["loop", "Iterator", "next"])
    assert scorer.score("A for loop calls next() on an iterator") == 100.0
    assert scorer.score("A LOOP") == pytest.approx(100 / 3)
    assert scorer.score("") == 0.0


def test_grade_answers(ex):
    assert ex.grade_answers(["Paris", " paris ", "Rome"], ex.ExactScorer("PARIS")) == ["A", "A", "F"]
    keywords = ex.KeywordScorer(["a", "b", "c", "d", "e"])
    assert ex.grade_answers(["abcde", "abcd", "ab"], keywords) == ["A", "B", "F"]


def test_grade_answers_accepts_any_scorer(ex):
    class Always70:
        def score(self, answer: str) -> float:
            return 70.0

    assert ex.grade_answers(["x", "y"], Always70()) == ["C", "C"]
