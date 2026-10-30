"""Checks that every assignment is complete: task, starter file, tests and a solution."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
LEVELS = ("beginner", "intermediate", "advanced", "professional")

TASKS = sorted(
    test.parent
    for level in LEVELS
    for test in (ROOT / level).glob("**/test_exercise.py")
)
IDS = [task.relative_to(ROOT).as_posix() for task in TASKS]


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_assignment_is_complete(task):
    assert (task / "README.md").is_file(), "task description missing"
    assert (task / "exercise.py").is_file(), "starter file missing"
    solution = ROOT / "solutions" / task.relative_to(ROOT) / "exercise.py"
    assert solution.is_file(), f"solution missing: {solution.relative_to(ROOT)}"


@pytest.mark.parametrize("task", TASKS, ids=IDS)
def test_starter_file_is_not_the_solution(task):
    solution = ROOT / "solutions" / task.relative_to(ROOT) / "exercise.py"
    assert (task / "exercise.py").read_bytes() != solution.read_bytes()
