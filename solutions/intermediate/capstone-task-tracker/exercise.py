"""Capstone · Task tracker: template solution.

Layers, from the inside out:
    Milestone 1  model       Priority, Task                    (pure data + rules)
    Milestone 2  parsing     parse_task_text                   (text -> values, regex)
    Milestone 3  TaskList    add / complete / filter / save    (collection + JSON storage)
    Milestone 4  CLI         build_parser, main                (the only layer that prints)
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
    # Int values make priorities comparable by .value; names are what users type.
    LOW = 1
    NORMAL = 2
    HIGH = 3


class TaskError(Exception):
    """Base class for all errors of the task tracker."""


class TaskNotFound(TaskError, KeyError):
    """No task with the requested id."""

    def __str__(self) -> str:
        # KeyError's own __str__ adds quotes around the message; we want plain text.
        return str(self.args[0])


@dataclass
class Task:
    id: int
    title: str
    priority: Priority = Priority.NORMAL
    due: date | None = None
    tags: set[str] = field(default_factory=set)
    done: bool = False

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title must not be empty")
        # Normalise tags once, here, so no other code has to care about case.
        self.tags = {tag.lower() for tag in self.tags}

    def is_overdue(self, today: date) -> bool:
        return not self.done and self.due is not None and self.due < today

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.name.lower(),
            "due": self.due.isoformat() if self.due else None,
            "tags": sorted(self.tags),
            "done": self.done,
        }

    @classmethod
    def from_dict(cls, data: object) -> Task:
        # The boundary for data from the file: every problem becomes a TaskError that
        # says what is wrong, instead of a KeyError or AttributeError somewhere later.
        if not isinstance(data, dict):
            raise TaskError("task must be an object")
        try:
            due = data.get("due")
            return cls(
                id=int(data["id"]),
                title=str(data["title"]),
                priority=Priority[str(data.get("priority", "normal")).upper()],
                due=date.fromisoformat(due) if due else None,
                tags=set(data.get("tags", [])),
                done=bool(data.get("done", False)),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise TaskError(f"invalid task {data!r}: {error}") from None


# ---------------------------------------------------------------------------
# Milestone 2 · Parsing quick-add text
# ---------------------------------------------------------------------------

TAG = re.compile(r"#(\w+)")
DUE = re.compile(r"\bdue:(\S+)")
PRIORITY = re.compile(r"(?<!\S)!(\w+)")


def parse_due(text: str, today: date) -> date:
    """'today', 'tomorrow', a weekday name ('fri'/'friday': the next one) or YYYY-MM-DD."""
    text = text.lower()
    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for number, name in enumerate(weekdays):
        if text in (name, name[:3]):
            # 1..7 days ahead: "fri" on a Friday means NEXT Friday, never today.
            return today + timedelta(days=(number - today.weekday() - 1) % 7 + 1)
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ValueError(f"invalid due date: {text!r}") from None


def parse_task_text(text: str, today: date) -> tuple[str, Priority, date | None, set[str]]:
    """Split 'Buy milk due:fri #home !high' into (title, priority, due, tags)."""
    tags = {tag.lower() for tag in TAG.findall(text)}

    due_values = DUE.findall(text)
    if len(due_values) > 1:
        raise ValueError("more than one due date")
    due = parse_due(due_values[0], today) if due_values else None

    priority_values = PRIORITY.findall(text)
    if len(priority_values) > 1:
        raise ValueError("more than one priority")
    priority = Priority.NORMAL
    if priority_values:
        try:
            priority = Priority[priority_values[0].upper()]
        except KeyError:
            raise ValueError(f"unknown priority: {priority_values[0]!r}") from None

    # The title is whatever is left after removing the markers, with spaces squashed.
    rest = PRIORITY.sub(" ", DUE.sub(" ", TAG.sub(" ", text)))
    title = " ".join(rest.split())
    if not title:
        raise ValueError("title must not be empty")
    return title, priority, due, tags


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
        self._tasks: dict[int, Task] = {task.id: task for task in tasks or []}

    def __len__(self) -> int:
        return len(self._tasks)

    def __iter__(self) -> Iterator[Task]:
        return iter(self._tasks.values())

    def next_id(self) -> int:
        # Ids are never reused while the highest task exists: max + 1.
        return max(self._tasks, default=0) + 1

    def add(self, text: str, today: date) -> Task:
        title, priority, due, tags = parse_task_text(text, today)
        task = Task(self.next_id(), title, priority, due, tags)
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError:
            raise TaskNotFound(f"no task with id {task_id}") from None

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.done = True
        return task

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        del self._tasks[task_id]
        return task

    def filter(self, *, tag: str | None = None, done: bool | None = None) -> Iterator[Task]:
        """Lazily yield the tasks matching every given criterion (None = don't care)."""
        for task in self._tasks.values():
            if tag is not None and tag.lower() not in task.tags:
                continue
            if done is not None and task.done != done:
                continue
            yield task

    @staticmethod
    def sort_key(task: Task) -> tuple[bool, bool, date, int, int]:
        # Open before done; tasks with a due date before those without; earlier due first;
        # higher priority first (negated); then by id for a stable, predictable order.
        return (task.done, task.due is None, task.due or date.max, -task.priority.value, task.id)

    def sorted(self, tasks: Iterator[Task] | None = None) -> list[Task]:
        return sorted(self if tasks is None else tasks, key=self.sort_key)

    def stats(self, today: date) -> Stats:
        tasks = list(self)
        tag_counts = Counter(tag for task in tasks if not task.done for tag in task.tags)
        return Stats(
            total=len(tasks),
            done=sum(task.done for task in tasks),          # True counts as 1
            open=sum(not task.done for task in tasks),
            overdue=sum(task.is_overdue(today) for task in tasks),
            # most open tasks first, ties alphabetically
            tags=dict(sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))),
        )

    def save(self, path: Path | str) -> None:
        path = Path(path)
        document = {"version": FORMAT_VERSION, "tasks": [task.to_dict() for task in sorted(self, key=lambda task: task.id)]}
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as file:
            json.dump(document, file, indent=2, ensure_ascii=False)
        os.replace(tmp, path)          # atomic: a crash never leaves a half-written file
        logger.debug("saved %d tasks to %s", len(self), path)

    @classmethod
    def load(cls, path: Path | str) -> TaskList:
        path = Path(path)
        try:
            with open(path, encoding="utf-8") as file:
                document = json.load(file)
        except FileNotFoundError:
            logger.debug("%s does not exist yet: starting empty", path)
            return cls()
        except json.JSONDecodeError as error:
            raise TaskError(f"{path.name} is not valid JSON: {error}") from None
        if not isinstance(document, dict) or document.get("version") != FORMAT_VERSION:
            raise TaskError(f"{path.name} is not a version {FORMAT_VERSION} task file")
        items = document.get("tasks")
        if not isinstance(items, list):
            raise TaskError(f"{path.name}: 'tasks' must be a list")
        tasks = [Task.from_dict(item) for item in items]
        if len({task.id for task in tasks}) != len(tasks):
            raise TaskError(f"{path.name}: duplicate task ids")
        logger.debug("loaded %d tasks from %s", len(tasks), path)
        return cls(tasks)


# ---------------------------------------------------------------------------
# Milestone 4 · The command line
# ---------------------------------------------------------------------------

def format_task(task: Task, today: date) -> str:
    parts = [f"{task.id:>3} [{'x' if task.done else ' '}] {task.title}"]
    if task.priority is not Priority.NORMAL:
        parts.append(f"!{task.priority.name.lower()}")
    if task.due:
        parts.append(f"due:{task.due.isoformat()}")
    parts.extend(f"#{tag}" for tag in sorted(task.tags))
    if task.is_overdue(today):
        parts.append("(overdue)")
    return " ".join(parts)


def build_parser() -> argparse.ArgumentParser:
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


def run(args: argparse.Namespace, tasks: TaskList, today: date) -> tuple[list[str], bool]:
    """Execute one command. Return the output lines and whether the list changed."""
    if args.command == "add":
        task = tasks.add(" ".join(args.text), today)
        return [f"Added task {task.id}: {task.title}"], True
    if args.command == "done":
        task = tasks.complete(args.id)
        return [f"Completed task {task.id}: {task.title}"], True
    if args.command == "remove":
        task = tasks.remove(args.id)
        return [f"Removed task {task.id}: {task.title}"], True
    if args.command == "list":
        selected = tasks.filter(tag=args.tag, done=None if args.all else False)
        lines = [format_task(task, today) for task in tasks.sorted(selected)]
        return lines or ["No tasks."], False
    stats = tasks.stats(today)
    lines = [f"{stats.total} tasks: {stats.done} done, {stats.open} open, {stats.overdue} overdue"]
    if stats.tags:
        lines.append("open by tag: " + ", ".join(f"#{tag} {count}" for tag, count in stats.tags.items()))
    return lines, False


def main(argv: list[str] | None = None, today: date | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
    today = today or date.today()           # injectable, so tests do not depend on the clock
    try:
        tasks = TaskList.load(args.file)
        lines, changed = run(args, tasks, today)
        if changed:
            tasks.save(args.file)
    except (TaskError, ValueError) as error:
        print(f"tasks: error: {error}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
