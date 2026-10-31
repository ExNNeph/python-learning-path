"""Assignment 11 · Typed gradebook.

1. Define Grade, StudentRecord and Scorer (see the README).
2. Implement every function and class below, and annotate ALL parameters and return types.
Check your work:  pytest intermediate/10-type-hints/assignments/11-typed-gradebook -v
Type check:       mypy intermediate/10-type-hints/assignments/11-typed-gradebook/exercise.py --strict
"""

from collections.abc import Callable, Iterable
from typing import Literal, Protocol, TypedDict

# TODO: Grade = ...
# TODO: class StudentRecord(TypedDict): ...
# TODO: class Scorer(Protocol): ...


def average(scores):
    """Return the mean of the scores. Empty: ValueError("no scores")."""
    raise NotImplementedError


def letter_grade(score):
    """Return 'A' (>= 90), 'B' (>= 80), 'C' (>= 70), 'D' (>= 60) or 'F'."""
    raise NotImplementedError


def parse_record(line):
    """Parse 'Ada: 91, 85.5, 78' into a StudentRecord."""
    raise NotImplementedError


def best_student(records):
    """Return the name with the highest average, or None if nobody has scores."""
    raise NotImplementedError


def report(records):
    """Return name -> Grade for every student with scores."""
    raise NotImplementedError


def apply_curve(records, curve):
    """Return new records with curve applied to every score, capped at 100.0."""
    raise NotImplementedError


class ExactScorer:
    def __init__(self, expected):
        raise NotImplementedError

    def score(self, answer):
        """100.0 if answer equals expected (case-insensitive, stripped), else 0.0."""
        raise NotImplementedError


class KeywordScorer:
    def __init__(self, keywords):
        raise NotImplementedError

    def score(self, answer):
        """The percentage of keywords that appear in the lower-cased answer."""
        raise NotImplementedError


def grade_answers(answers, scorer):
    """Return the Grade for each answer, scored by any Scorer."""
    raise NotImplementedError


if __name__ == "__main__":
    lines = ["Ada: 91, 85.5, 78", "Grace: 99, 98", "Linus: 55, 71"]
    records = [parse_record(line) for line in lines]
    print(report(records))
    print("Best:", best_student(records))
    print("Curved:", report(apply_curve(records, lambda score: score * 1.1)))
