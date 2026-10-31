"""Capstone · Task tracker.

Work through the four milestones in the README, in order. Each milestone has its own tests:
    pytest intermediate/capstone-task-tracker -v -k milestone1
Run the finished program:
    python intermediate/capstone-task-tracker/exercise.py --help
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).with_name("tasks.json")
FORMAT_VERSION = 1


# ---------------------------------------------------------------------------
# Milestone 1 · The model
# ---------------------------------------------------------------------------

class Priority(Enum):
    """TODO: LOW = 1, NORMAL = 2, HIGH = 3."""


class TaskError(Exception):
    """Base class for all errors of the task tracker."""


class TaskNotFound(TaskError, KeyError):
    """No task with the requested id."""

    def __str__(self) -> str:
        # KeyError's own __str__ adds quotes around the message; we want plain text.
        return str(self.args[0])


class Task:
    """TODO: a dataclass with the fields
    id: int, title: str, priority: Priority = Priority.NORMAL, due: date | None = None,
    tags: set[str] (a new empty set by default), done: bool = False.
    """

    def __post_init__(self) -> None:
        """Strip the title (empty: ValueError) and lower-case the tags."""
        raise NotImplementedError

    def is_overdue(self, today: date) -> bool:
        """True if the task is not done and its due date is before today."""
        raise NotImplementedError

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-ready dict (priority as lower-case name, due as ISO or None, tags sorted)."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: object) -> Task:
        """Build a Task from a dict loaded from JSON. Any problem: TaskError."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Milestone 2 · Parsing quick-add text
# ---------------------------------------------------------------------------

def parse_due(text: str, today: date) -> date:
    """'today', 'tomorrow', a weekday ('fri' / 'friday': the NEXT one) or YYYY-MM-DD."""
    raise NotImplementedError


def parse_task_text(text: str, today: date) -> tuple[str, Priority, date | None, set[str]]:
    """Split 'Buy milk due:fri #home !high' into (title, priority, due, tags)."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Milestone 3 · The task list and its storage
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Stats:
    total: int
    done: int
    open: int
    overdue: int
    tags: dict[str, int]       # open tasks per tag


class TaskList:
    def __init__(self, tasks: list[Task] | None = None) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Task]:
        raise NotImplementedError

    def next_id(self) -> int:
        """The highest id + 1 (1 for an empty list)."""
        raise NotImplementedError

    def add(self, text: str, today: date) -> Task:
        """Parse text, create a Task with the next id, store and return it."""
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        """Return the task. Unknown id: TaskNotFound("no task with id <id>")."""
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        raise NotImplementedError

    def filter(self, *, tag: str | None = None, done: bool | None = None) -> Iterator[Task]:
        """Lazily yield the tasks matching every given criterion (None = don't care)."""
        raise NotImplementedError

    def sorted(self, tasks: Iterator[Task] | None = None) -> list[Task]:
        """Return tasks (default: all) sorted: open first, then by due date (none last),
        then by priority (high first), then by id."""
        raise NotImplementedError

    def stats(self, today: date) -> Stats:
        raise NotImplementedError

    def save(self, path: Path | str) -> None:
        """Write {"version": 1, "tasks": [...]} (tasks in id order) atomically as pretty UTF-8 JSON."""
        raise NotImplementedError

    @classmethod
    def load(cls, path: Path | str) -> TaskList:
        """Load a task file. Missing file: empty list. Anything invalid: TaskError."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Milestone 4 · The command line
# ---------------------------------------------------------------------------

def format_task(task: Task, today: date) -> str:
    """'  1 [ ] Buy milk !high due:2026-11-06 #home (overdue)' (see the README)."""
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    """The command line is given, so you can concentrate on main()."""
    parser = argparse.ArgumentParser(prog="tasks", description="A tiny command-line task tracker.")
    parser.add_argument("--file", type=Path, default=DATA_FILE, help="task file (default: tasks.json next to this script)")
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug log messages")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a task: tasks add Buy milk due:fri #home !high")
    add.add_argument("text", nargs="+", help="title with optional due:DATE, #tags and !priority")

    show = sub.add_parser("list", help="list open tasks")
    show.add_argument("--all", action="store_true", help="include done tasks")
    show.add_argument("--tag", help="only tasks with this tag")

    for name, text in [("done", "mark a task as done"), ("remove", "delete a task")]:
        command = sub.add_parser(name, help=text)
        command.add_argument("id", type=int)

    sub.add_parser("stats", help="show a summary")
    return parser


def main(argv: list[str] | None = None, today: date | None = None) -> int:
    """Load, run one command, save if something changed, print. Return the exit code."""
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
