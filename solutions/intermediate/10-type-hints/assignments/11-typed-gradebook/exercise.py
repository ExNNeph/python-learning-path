"""Assignment 11 · Typed gradebook: template solution."""

from collections.abc import Callable, Iterable
from typing import Literal, Protocol, TypedDict

# A type alias: one name for the five allowed strings. mypy rejects any other string
# wherever a Grade is expected.
Grade = Literal["A", "B", "C", "D", "F"]


class StudentRecord(TypedDict):
    """The shape of one student's data. At runtime it is a plain dict."""
    name: str
    scores: list[float]


class Scorer(Protocol):
    """Anything with a matching score() method is a Scorer: no inheritance needed."""
    def score(self, answer: str) -> float: ...


def average(scores: Iterable[float]) -> float:
    """Return the mean of the scores. Empty: ValueError("no scores")."""
    # Iterable accepts lists, tuples and generators. A generator has no len() and can be
    # read only once, so materialise it first.
    values = list(scores)
    if not values:
        raise ValueError("no scores")
    return sum(values) / len(values)


def letter_grade(score: float) -> Grade:
    """Return 'A' (>= 90), 'B' (>= 80), 'C' (>= 70), 'D' (>= 60) or 'F'."""
    # Returning literal strings lets mypy prove that every path returns a valid Grade.
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def parse_record(line: str) -> StudentRecord:
    """Parse 'Ada: 91, 85.5, 78' into a StudentRecord."""
    name, separator, rest = line.partition(":")
    if not separator or not name.strip():
        raise ValueError(f"expected 'name: score, score, ...', got {line!r}")
    # float() raises ValueError for non-numbers, which is exactly what we want to pass on.
    scores = [float(part) for part in rest.split(",") if part.strip()]
    return {"name": name.strip(), "scores": scores}


def best_student(records: Iterable[StudentRecord]) -> str | None:
    """Return the name with the highest average, or None if nobody has scores."""
    graded = [record for record in records if record["scores"]]
    if not graded:
        return None
    best = max(graded, key=lambda record: average(record["scores"]))
    return best["name"]


def report(records: Iterable[StudentRecord]) -> dict[str, Grade]:
    """Return name -> Grade for every student with scores."""
    return {record["name"]: letter_grade(average(record["scores"]))
            for record in records if record["scores"]}


def apply_curve(records: Iterable[StudentRecord], curve: Callable[[float], float]) -> list[StudentRecord]:
    """Return new records with curve applied to every score, capped at 100.0."""
    # New dicts and lists: the caller's records stay unchanged.
    return [{"name": record["name"], "scores": [min(100.0, curve(score)) for score in record["scores"]]}
            for record in records]


class ExactScorer:
    def __init__(self, expected: str) -> None:
        self.expected = expected.strip().lower()

    def score(self, answer: str) -> float:
        """100.0 if answer equals expected (case-insensitive, stripped), else 0.0."""
        return 100.0 if answer.strip().lower() == self.expected else 0.0


class KeywordScorer:
    def __init__(self, keywords: list[str]) -> None:
        self.keywords = [keyword.lower() for keyword in keywords]

    def score(self, answer: str) -> float:
        """The percentage of keywords that appear in the lower-cased answer."""
        if not self.keywords:
            return 0.0
        text = answer.lower()
        found = sum(keyword in text for keyword in self.keywords)   # True counts as 1
        return 100.0 * found / len(self.keywords)


def grade_answers(answers: Iterable[str], scorer: Scorer) -> list[Grade]:
    """Return the Grade for each answer, scored by any Scorer."""
    # Neither scorer class inherits from Scorer; mypy accepts them because their
    # score() method matches the protocol (structural typing).
    return [letter_grade(scorer.score(answer)) for answer in answers]


if __name__ == "__main__":
    lines = ["Ada: 91, 85.5, 78", "Grace: 99, 98", "Linus: 55, 71"]
    records = [parse_record(line) for line in lines]
    print(report(records))
    print("Best:", best_student(records))
    print("Curved:", report(apply_curve(records, lambda score: score * 1.1)))
