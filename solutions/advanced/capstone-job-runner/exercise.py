"""Capstone · Job runner: template solution.

Layers, from the inside out:
    Milestone 1  model      Job, Runner registration and container protocol
    Milestone 2  planning   plan() and levels(): dependency order, cycles, parallel waves
    Milestone 3  running    run(): waves on a thread pool, failures, skips, caching
    Milestone 4  CLI        format_report(), main() (the only layer that prints)
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable, Hashable, Iterator, MutableMapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, TypeVar, overload

F = TypeVar("F", bound=Callable[..., Any])
JobFunc = Callable[[dict[str, Any]], Any]


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


@dataclass(frozen=True)
class Job:
    name: str
    func: JobFunc
    deps: tuple[str, ...] = ()
    key: Callable[[], Hashable] | None = None


@dataclass(frozen=True)
class Result:
    name: str
    status: str                       # "ok", "cached", "failed" or "skipped"
    duration: float = 0.0
    value: Any = None
    error: BaseException | None = None

    @property
    def succeeded(self) -> bool:
        return self.status in ("ok", "cached")


class Runner:
    def __init__(
        self,
        cache: MutableMapping[str, tuple[Hashable, Any]] | None = None,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._jobs: dict[str, Job] = {}
        self.cache: MutableMapping[str, tuple[Hashable, Any]] = {} if cache is None else cache
        self.clock = clock

    @overload
    def job(
        self,
        func: F,
        *,
        name: str | None = None,
        deps: Sequence[str] = (),
        key: Callable[[], Hashable] | None = None,
    ) -> F: ...
    @overload
    def job(
        self,
        *,
        name: str | None = None,
        deps: Sequence[str] = (),
        key: Callable[[], Hashable] | None = None,
    ) -> Callable[[F], F]: ...
    def job(
        self,
        func: F | None = None,
        *,
        name: str | None = None,
        deps: Sequence[str] = (),
        key: Callable[[], Hashable] | None = None,
    ) -> Any:
        """Register a job. Works as @runner.job and as @runner.job(name=..., deps=..., key=...)."""

        def decorator(f: F) -> F:
            job_name = name or f.__name__
            if job_name in self._jobs:
                raise JobError(f"duplicate job {job_name!r}")
            self._jobs[job_name] = Job(job_name, f, tuple(deps), key)
            return f                  # registering, not wrapping: the function stays callable as it is

        if func is None:
            return decorator
        return decorator(func)

    def __len__(self) -> int:
        return len(self._jobs)

    def __iter__(self) -> Iterator[str]:
        return iter(self._jobs)

    def __contains__(self, name: object) -> bool:
        return name in self._jobs

    def __getitem__(self, name: str) -> Job:
        try:
            return self._jobs[name]
        except KeyError:
            raise UnknownJob(f"unknown job {name!r}") from None

    # -----------------------------------------------------------------------
    # Milestone 2 · Planning
    # -----------------------------------------------------------------------

    def plan(self, *targets: str) -> list[str]:
        """Dependency-first order of the targets (default: all jobs) and everything they need."""
        order: list[str] = []
        done: set[str] = set()
        visiting: list[str] = []      # the current DFS path, to report cycles

        def visit(name: str) -> None:
            if name in done:
                return
            if name in visiting:
                cycle = visiting[visiting.index(name):] + [name]
                raise CycleError("cycle: " + " -> ".join(cycle))
            job = self[name]          # UnknownJob for unknown targets and dependencies
            visiting.append(name)
            for dep in job.deps:
                visit(dep)
            visiting.pop()
            done.add(name)
            order.append(name)        # post-order: after all its dependencies

        for target in targets or tuple(self._jobs):
            visit(target)
        return order                  # O(jobs + dependencies): each job is expanded once

    def levels(self, *targets: str) -> list[list[str]]:
        """Group the plan into waves; a job's wave is one more than its deepest dependency's."""
        depth: dict[str, int] = {}
        waves: list[list[str]] = []
        for name in self.plan(*targets):
            level = max((depth[dep] + 1 for dep in self._jobs[name].deps), default=0)
            depth[name] = level
            if level == len(waves):
                waves.append([])
            waves[level].append(name)
        return waves

    # -----------------------------------------------------------------------
    # Milestone 3 · Running
    # -----------------------------------------------------------------------

    def _execute(self, job: Job, inputs: dict[str, Any]) -> Result:
        start = self.clock()
        try:
            value = job.func(inputs)
        except Exception as error:     # a failing job must not stop the others
            return Result(job.name, "failed", self.clock() - start, error=error)
        return Result(job.name, "ok", self.clock() - start, value)

    def run(self, *targets: str, workers: int = 1) -> dict[str, Result]:
        plan = self.plan(*targets)     # raises before anything runs
        results: dict[str, Result] = {}
        keys: dict[str, Hashable] = {}
        for wave in self.levels(*targets):
            runnable: list[Job] = []
            for name in wave:
                job = self._jobs[name]
                if any(not results[dep].succeeded for dep in job.deps):
                    results[name] = Result(name, "skipped")
                    continue
                if job.key is not None:
                    try:
                        keys[name] = job.key()
                    except Exception as error:
                        results[name] = Result(name, "failed", error=error)
                        continue
                    deps_changed = any(results[dep].status == "ok" for dep in job.deps)
                    cached = self.cache.get(name)
                    if not deps_changed and cached is not None and cached[0] == keys[name]:
                        results[name] = Result(name, "cached", value=cached[1])
                        continue
                runnable.append(job)
            # Jobs in one wave never depend on each other: run them side by side.
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = [
                    pool.submit(self._execute, job, {dep: results[dep].value for dep in job.deps})
                    for job in runnable
                ]
            for job, future in zip(runnable, futures):
                result = results[job.name] = future.result()
                if result.status == "ok" and job.key is not None:
                    self.cache[job.name] = (keys[job.name], result.value)
        return {name: results[name] for name in plan}


# ---------------------------------------------------------------------------
# Milestone 4 · The command line
# ---------------------------------------------------------------------------

def format_report(results: dict[str, Result]) -> list[str]:
    lines = []
    for result in results.values():
        match result:
            case Result(status="ok", name=name, duration=duration):
                lines.append(f"ok       {name} ({duration:.2f} s)")
            case Result(status="cached", name=name):
                lines.append(f"cached   {name}")
            case Result(status="failed", name=name, error=error):
                lines.append(f"FAILED   {name}: {type(error).__name__}: {error}")
            case Result(status="skipped", name=name):
                lines.append(f"skipped  {name}")
    statuses = [result.status for result in results.values()]
    counts = ", ".join(f"{statuses.count(s)} {s}" for s in ("ok", "cached", "failed", "skipped"))
    lines.append(f"{len(statuses)} jobs: {counts}")
    return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobs", description="Run jobs in dependency order.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list all jobs and their dependencies")
    plan = sub.add_parser("plan", help="show the order in which jobs would run")
    plan.add_argument("targets", nargs="*")
    run = sub.add_parser("run", help="run jobs and their dependencies")
    run.add_argument("targets", nargs="*")
    run.add_argument("-j", "--jobs", type=int, default=1, help="number of parallel workers")
    return parser


def main(argv: list[str] | None, runner: Runner) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "list":
            lines = [
                f"{name} <- {', '.join(runner[name].deps)}" if runner[name].deps else name
                for name in runner
            ]
            failed = False
        elif args.command == "plan":
            lines = runner.plan(*args.targets)
            failed = False
        else:
            results = runner.run(*args.targets, workers=args.jobs)
            lines = format_report(results)
            failed = any(result.status == "failed" for result in results.values())
    except JobError as error:
        print(f"jobs: error: {error}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    runner = Runner()

    @runner.job
    def fetch(deps: dict[str, Any]) -> list[int]:
        time.sleep(0.2)
        return [3, 1, 2]

    @runner.job(deps=["fetch"])
    def sort(deps: dict[str, Any]) -> list[int]:
        return sorted(deps["fetch"])

    @runner.job(deps=["fetch"])
    def total(deps: dict[str, Any]) -> int:
        return sum(deps["fetch"])

    @runner.job(name="report", deps=["sort", "total"])
    def make_report(deps: dict[str, Any]) -> str:
        return f"{deps['sort']} sum={deps['total']}"

    sys.exit(main(sys.argv[1:], runner))
