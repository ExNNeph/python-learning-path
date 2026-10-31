"""Capstone · Job runner.

Work through the four milestones in the README, in order. Each milestone has its own tests:
    pytest advanced/capstone-job-runner -v -k milestone1
Run the demo at the bottom of this file:
    python advanced/capstone-job-runner/exercise.py run -j 2
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable, Hashable, Iterator, MutableMapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Milestone 1 · The model
# ---------------------------------------------------------------------------

class JobError(Exception):
    """Base class for all errors of the job runner."""


class UnknownJob(JobError, KeyError):
    """A job name that is not registered."""

    def __str__(self) -> str:
        # KeyError's own __str__ adds quotes around the message; we want plain text.
        return str(self.args[0])


class CycleError(JobError):
    """The dependencies contain a cycle."""


class Job:
    """TODO: a frozen dataclass with name, func, deps (a tuple, default ()) and key (default None)."""


@dataclass(frozen=True)
class Result:
    """The outcome of one job (given)."""

    name: str
    status: str                       # "ok", "cached", "failed" or "skipped"
    duration: float = 0.0
    value: Any = None
    error: BaseException | None = None

    @property
    def succeeded(self) -> bool:
        return self.status in ("ok", "cached")


class Runner:
    def __init__(self, cache=None, clock=time.perf_counter):
        raise NotImplementedError

    def job(self, func=None, *, name=None, deps=(), key=None):
        """Register a job. Works as @runner.job and as @runner.job(name=..., deps=..., key=...)."""
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __contains__(self, name):
        raise NotImplementedError

    def __getitem__(self, name):
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Milestone 2 · Planning
    # -----------------------------------------------------------------------

    def plan(self, *targets):
        """Dependency-first order of the targets (default: all jobs) and everything they need."""
        raise NotImplementedError

    def levels(self, *targets):
        """The plan grouped into waves of jobs that can run at the same time."""
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Milestone 3 · Running
    # -----------------------------------------------------------------------

    def run(self, *targets, workers=1):
        """Run the plan wave by wave; return {name: Result} in plan order."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Milestone 4 · The command line
# ---------------------------------------------------------------------------

def format_report(results):
    """One line per result (use match on the Result), plus a summary line."""
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    """The command line is given, so you can concentrate on main()."""
    parser = argparse.ArgumentParser(prog="jobs", description="Run jobs in dependency order.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list all jobs and their dependencies")
    plan = sub.add_parser("plan", help="show the order in which jobs would run")
    plan.add_argument("targets", nargs="*")
    run = sub.add_parser("run", help="run jobs and their dependencies")
    run.add_argument("targets", nargs="*")
    run.add_argument("-j", "--jobs", type=int, default=1, help="number of parallel workers")
    return parser


def main(argv, runner):
    """Parse argv, run the command against runner, print, return the exit code."""
    raise NotImplementedError


if __name__ == "__main__":
    runner = Runner()

    @runner.job
    def fetch(deps):
        time.sleep(0.2)
        return [3, 1, 2]

    @runner.job(deps=["fetch"])
    def sort(deps):
        return sorted(deps["fetch"])

    @runner.job(deps=["fetch"])
    def total(deps):
        return sum(deps["fetch"])

    @runner.job(name="report", deps=["sort", "total"])
    def make_report(deps):
        return f"{deps['sort']} sum={deps['total']}"

    sys.exit(main(sys.argv[1:], runner))
