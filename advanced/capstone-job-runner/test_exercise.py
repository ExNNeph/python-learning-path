"""Tests for the Advanced capstone. Run one milestone at a time:

    pytest advanced/capstone-job-runner -v -k milestone1
"""

import dataclasses
import itertools
import threading
import time

import pytest


def noop(deps):
    return None


def make_runner(ex, spec, **kwargs):
    """Build a runner from {name: [deps]}; every job returns its own name."""
    runner = ex.Runner(**kwargs)
    for name, deps in spec.items():
        runner.job(lambda inputs, name=name: name, name=name, deps=deps)
    return runner


BUILD = {
    "fetch": [],
    "compile": ["fetch"],
    "assets": ["fetch"],
    "test": ["compile"],
    "package": ["compile", "assets"],
    "docs": [],
}


# ===========================================================================
# Milestone 1 · The model
# ===========================================================================

def test_milestone1_job_is_a_frozen_dataclass(ex):
    job = ex.Job("build", noop)
    assert dataclasses.is_dataclass(job)
    assert (job.name, job.func, job.deps, job.key) == ("build", noop, (), None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        job.name = "other"


def test_milestone1_jobs_compare_by_value(ex):
    assert ex.Job("a", noop, ("b",)) == ex.Job("a", noop, ("b",))


def test_milestone1_register_without_brackets(ex):
    runner = ex.Runner()

    def build(deps):
        return 1

    assert runner.job(build) is build
    assert runner["build"] == ex.Job("build", build, (), None)


def test_milestone1_register_with_options(ex):
    runner = ex.Runner()

    def key():
        return 1

    @runner.job(name="make-docs", deps=["build", "lint"], key=key)
    def docs(deps):
        return "docs"

    job = runner["make-docs"]
    assert (job.name, job.func, job.deps, job.key) == ("make-docs", docs, ("build", "lint"), key)
    assert docs({}) == "docs"


def test_milestone1_deps_become_a_tuple(ex):
    runner = ex.Runner()
    runner.job(name="a", deps=["b"])(noop)
    assert runner["a"].deps == ("b",)


def test_milestone1_empty_brackets(ex):
    runner = ex.Runner()

    @runner.job()
    def lint(deps):
        pass

    assert "lint" in runner


def test_milestone1_duplicate_name(ex):
    runner = ex.Runner()
    runner.job(name="x")(noop)
    with pytest.raises(ex.JobError, match="duplicate job 'x'"):
        runner.job(name="x")(noop)


def test_milestone1_container_protocol(ex):
    runner = make_runner(ex, BUILD)
    assert len(runner) == 6
    assert list(runner) == list(BUILD)
    assert "test" in runner and "deploy" not in runner
    assert len(ex.Runner()) == 0


def test_milestone1_unknown_job(ex):
    runner = make_runner(ex, BUILD)
    with pytest.raises(ex.UnknownJob) as info:
        runner["deploy"]
    assert str(info.value) == "unknown job 'deploy'"
    assert isinstance(info.value, KeyError) and isinstance(info.value, ex.JobError)


def test_milestone1_registration_order_is_kept(ex):
    runner = make_runner(ex, {"z": [], "a": [], "m": []})
    assert list(runner) == ["z", "a", "m"]


def test_milestone1_runners_are_independent(ex):
    one, two = ex.Runner(), ex.Runner()
    one.job(name="a")(noop)
    assert "a" not in two
    assert one.cache is not two.cache


def test_milestone1_cache_can_be_passed_in(ex):
    store = {}
    assert ex.Runner(cache=store).cache is store


# ===========================================================================
# Milestone 2 · Planning
# ===========================================================================

def test_milestone2_plan_all(ex):
    runner = make_runner(ex, BUILD)
    assert runner.plan() == ["fetch", "compile", "assets", "test", "package", "docs"]


def test_milestone2_plan_target(ex):
    runner = make_runner(ex, BUILD)
    assert runner.plan("package") == ["fetch", "compile", "assets", "package"]
    assert runner.plan("test") == ["fetch", "compile", "test"]
    assert runner.plan("docs") == ["docs"]


def test_milestone2_plan_several_targets_in_given_order(ex):
    runner = make_runner(ex, BUILD)
    assert runner.plan("docs", "test") == ["docs", "fetch", "compile", "test"]
    assert runner.plan("test", "package") == ["fetch", "compile", "test", "assets", "package"]


def test_milestone2_plan_each_job_once(ex):
    runner = make_runner(ex, {"a": [], "b": ["a"], "c": ["a", "b"], "d": ["c", "b", "a"]})
    assert runner.plan("d") == ["a", "b", "c", "d"]
    assert runner.plan("d", "d", "a") == ["a", "b", "c", "d"]


def test_milestone2_plan_respects_dependencies(ex):
    spec = {f"j{n}": [f"j{m}" for m in range(n) if (n * m) % 3 == 1] for n in range(12)}
    plan = make_runner(ex, spec).plan()
    assert sorted(plan) == sorted(spec)
    for name, deps in spec.items():
        assert all(plan.index(dep) < plan.index(name) for dep in deps)


def test_milestone2_plan_dependency_registered_later(ex):
    runner = make_runner(ex, {"deploy": ["build"], "build": []})
    assert runner.plan() == ["build", "deploy"]


def test_milestone2_unknown_target(ex):
    with pytest.raises(ex.UnknownJob, match="unknown job 'nope'"):
        make_runner(ex, BUILD).plan("nope")


def test_milestone2_unknown_dependency(ex):
    runner = make_runner(ex, {"a": ["ghost"]})
    with pytest.raises(ex.UnknownJob, match="unknown job 'ghost'"):
        runner.plan()


def test_milestone2_cycle(ex):
    runner = make_runner(ex, {"a": ["b"], "b": ["c"], "c": ["a"]})
    with pytest.raises(ex.CycleError) as info:
        runner.plan("a")
    assert str(info.value) == "cycle: a -> b -> c -> a"
    assert isinstance(info.value, ex.JobError)


def test_milestone2_cycle_reported_from_where_it_starts(ex):
    runner = make_runner(ex, {"start": ["x"], "x": ["y"], "y": ["x"]})
    with pytest.raises(ex.CycleError, match=r"^cycle: x -> y -> x$"):
        runner.plan()


def test_milestone2_self_dependency(ex):
    with pytest.raises(ex.CycleError, match=r"^cycle: a -> a$"):
        make_runner(ex, {"a": ["a"]}).plan()


def test_milestone2_diamond_is_not_a_cycle(ex):
    runner = make_runner(ex, {"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]})
    assert runner.plan() == ["a", "b", "c", "d"]


def test_milestone2_levels(ex):
    runner = make_runner(ex, BUILD)
    assert runner.levels() == [["fetch", "docs"], ["compile", "assets"], ["test", "package"]]


def test_milestone2_levels_use_the_deepest_dependency(ex):
    runner = make_runner(ex, {"a": [], "b": ["a"], "c": ["b"], "d": ["a", "c"], "e": []})
    assert runner.levels() == [["a", "e"], ["b"], ["c"], ["d"]]


def test_milestone2_levels_of_targets(ex):
    runner = make_runner(ex, BUILD)
    assert runner.levels("test") == [["fetch"], ["compile"], ["test"]]
    assert runner.levels("docs", "assets") == [["docs", "fetch"], ["assets"]]


def test_milestone2_levels_empty_runner(ex):
    assert ex.Runner().levels() == []
    assert ex.Runner().plan() == []


def test_milestone2_planning_is_fast(ex):
    spec = {f"j{n}": [f"j{n - 1}"] if n else [] for n in range(300)}
    spec.update({f"k{n}": [f"j{m}" for m in range(0, 300, 7)] for n in range(300)})
    runner = make_runner(ex, spec)
    start = time.perf_counter()
    assert len(runner.plan()) == 600
    assert len(runner.levels()) == 300
    assert time.perf_counter() - start < 1


# ===========================================================================
# Milestone 3 · Running
# ===========================================================================

def counting_clock():
    """A fake clock: 0.0, 1.0, 2.0, ... so every job lasts exactly 1.0 s (with one worker)."""
    return itertools.count().__next__


def test_milestone3_run_passes_dependency_values(ex):
    runner = ex.Runner()

    @runner.job
    def fetch(deps):
        assert deps == {}
        return [3, 1, 2]

    @runner.job(deps=["fetch"])
    def total(deps):
        return sum(deps["fetch"])

    @runner.job(name="report", deps=["fetch", "total"])
    def make_report(deps):
        return f"{sorted(deps['fetch'])} sum={deps['total']}"

    results = runner.run()
    assert list(results) == ["fetch", "total", "report"]
    assert results["report"].value == "[1, 2, 3] sum=6"
    assert all(r.status == "ok" and r.error is None for r in results.values())


def test_milestone3_results_are_result_objects(ex):
    results = make_runner(ex, {"a": []}).run()
    assert isinstance(results["a"], ex.Result)
    assert results["a"].value == "a"


def test_milestone3_run_only_the_plan(ex):
    ran = []
    runner = ex.Runner()
    for name, deps in BUILD.items():
        runner.job(lambda d, name=name: ran.append(name), name=name, deps=deps)
    results = runner.run("test")
    assert list(results) == ["fetch", "compile", "test"]
    assert sorted(ran) == ["compile", "fetch", "test"]


def test_milestone3_results_in_plan_order(ex):
    runner = make_runner(ex, BUILD)
    assert list(runner.run()) == runner.plan()


def test_milestone3_durations_use_the_clock(ex):
    runner = make_runner(ex, {"a": [], "b": ["a"]}, clock=counting_clock())
    results = runner.run()
    assert results["a"].duration == 1.0 and results["b"].duration == 1.0


def test_milestone3_real_durations(ex):
    runner = ex.Runner()
    runner.job(lambda d: time.sleep(0.05), name="nap")
    assert 0.04 <= runner.run()["nap"].duration < 1


def test_milestone3_failure_is_recorded(ex):
    runner = ex.Runner(clock=counting_clock())

    @runner.job
    def broken(deps):
        raise ValueError("bad input")

    result = runner.run()["broken"]
    assert result.status == "failed"
    assert isinstance(result.error, ValueError) and str(result.error) == "bad input"
    assert result.value is None
    assert result.duration == 1.0
    assert not result.succeeded


def test_milestone3_failure_skips_dependents_only(ex):
    ran = []
    runner = ex.Runner()
    spec = {"fetch": [], "compile": ["fetch"], "assets": ["fetch"], "test": ["compile"], "package": ["compile", "assets"], "docs": []}
    for name, deps in spec.items():
        def func(d, name=name):
            ran.append(name)
            if name == "compile":
                raise RuntimeError("compiler crashed")
            return name
        runner.job(func, name=name, deps=deps)

    results = runner.run()
    statuses = {name: result.status for name, result in results.items()}
    assert statuses == {"fetch": "ok", "compile": "failed", "assets": "ok", "test": "skipped", "package": "skipped", "docs": "ok"}
    assert "test" not in ran and "package" not in ran
    assert results["test"] == ex.Result("test", "skipped")


def test_milestone3_skips_propagate(ex):
    runner = ex.Runner()
    runner.job(lambda d: 1 / 0, name="a")
    runner.job(lambda d: "b", name="b", deps=["a"])
    runner.job(lambda d: "c", name="c", deps=["b"])
    statuses = [r.status for r in runner.run().values()]
    assert statuses == ["failed", "skipped", "skipped"]


def test_milestone3_errors_are_raised_before_running(ex):
    ran = []
    runner = ex.Runner()
    runner.job(lambda d: ran.append("a"), name="a")
    runner.job(lambda d: ran.append("b"), name="b", deps=["missing"])
    with pytest.raises(ex.UnknownJob):
        runner.run()
    assert ran == []


def test_milestone3_waves_run_in_parallel(ex):
    runner = ex.Runner()
    for n in range(4):
        runner.job(lambda d: time.sleep(0.3), name=f"slow{n}")
    start = time.perf_counter()
    results = runner.run(workers=4)
    assert time.perf_counter() - start < 0.9          # sequential: 1.2 s
    assert all(r.status == "ok" for r in results.values())


def test_milestone3_one_worker_is_sequential(ex):
    active, peak, lock = [0], [0], threading.Lock()

    def job(deps):
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        time.sleep(0.02)
        with lock:
            active[0] -= 1

    runner = ex.Runner()
    for n in range(4):
        runner.job(job, name=f"j{n}")
    runner.run()
    assert peak[0] == 1


def test_milestone3_dependencies_finish_first_in_parallel(ex):
    finished = []
    runner = ex.Runner()
    runner.job(lambda d: (time.sleep(0.2), finished.append("slow-dep")), name="slow-dep")
    runner.job(lambda d: finished.append("fast"), name="fast")
    runner.job(lambda d: finished.append("after"), name="after", deps=["slow-dep"])
    runner.run(workers=3)
    assert finished.index("slow-dep") < finished.index("after")


# --- caching ---------------------------------------------------------------

class Source:
    """A fake input file: the key is its version, the job counts how often it builds."""

    def __init__(self):
        self.version = 1
        self.builds = 0

    def key(self):
        return self.version

    def build(self, deps):
        self.builds += 1
        return f"built v{self.version}"


def test_milestone3_cached_when_key_unchanged(ex):
    src = Source()
    runner = ex.Runner()
    runner.job(src.build, name="compile", key=src.key)
    first = runner.run()["compile"]
    second = runner.run()["compile"]
    assert (first.status, second.status) == ("ok", "cached")
    assert second.value == "built v1" and second.succeeded
    assert src.builds == 1
    assert runner.cache["compile"] == (1, "built v1")


def test_milestone3_rebuilt_when_key_changes(ex):
    src = Source()
    runner = ex.Runner()
    runner.job(src.build, name="compile", key=src.key)
    runner.run()
    src.version = 2
    result = runner.run()["compile"]
    assert result.status == "ok" and result.value == "built v2"
    assert src.builds == 2


def test_milestone3_jobs_without_key_always_run(ex):
    src = Source()
    runner = ex.Runner()
    runner.job(src.build, name="compile")
    runner.run(), runner.run()
    assert src.builds == 2
    assert "compile" not in runner.cache


def test_milestone3_rebuilt_when_a_dependency_ran(ex):
    upstream, downstream = Source(), Source()
    runner = ex.Runner()
    runner.job(upstream.build, name="up", key=upstream.key)
    runner.job(downstream.build, name="down", deps=["up"], key=downstream.key)
    runner.run()
    upstream.version = 2
    results = runner.run()
    assert (results["up"].status, results["down"].status) == ("ok", "ok")
    statuses = [r.status for r in runner.run().values()]
    assert statuses == ["cached", "cached"]
    assert downstream.builds == 2


def test_milestone3_failed_jobs_are_not_cached(ex):
    calls = []
    runner = ex.Runner()

    def flaky(deps):
        calls.append(1)
        if len(calls) == 1:
            raise OSError("disk full")
        return "ok now"

    runner.job(flaky, name="flaky", key=lambda: "same")
    assert runner.run()["flaky"].status == "failed"
    assert runner.run()["flaky"].value == "ok now"
    assert runner.run()["flaky"].status == "cached"


def test_milestone3_cached_value_reaches_dependents(ex):
    src = Source()
    runner = ex.Runner()
    runner.job(src.build, name="compile", key=src.key)
    runner.job(lambda d: d["compile"].upper(), name="shout", deps=["compile"])
    runner.run()
    results = runner.run()
    assert results["compile"].status == "cached"
    assert results["shout"].value == "BUILT V1"


def test_milestone3_shared_cache(ex):
    src = Source()
    store = {}
    for _ in range(2):
        runner = ex.Runner(cache=store)
        runner.job(src.build, name="compile", key=src.key)
        runner.run()
    assert src.builds == 1


def test_milestone3_failing_key_fails_the_job(ex):
    runner = ex.Runner()
    runner.job(noop, name="a", key=lambda: 1 / 0)
    result = runner.run()["a"]
    assert result.status == "failed" and isinstance(result.error, ZeroDivisionError)


# ===========================================================================
# Milestone 4 · The command line
# ===========================================================================

def test_milestone4_format_report(ex):
    results = {
        "fetch": ex.Result("fetch", "ok", 1.234, value=[1]),
        "compile": ex.Result("compile", "cached", value="x"),
        "test": ex.Result("test", "failed", 0.5, error=AssertionError("2 tests failed")),
        "package": ex.Result("package", "skipped"),
    }
    assert ex.format_report(results) == [
        "ok       fetch (1.23 s)",
        "cached   compile",
        "FAILED   test: AssertionError: 2 tests failed",
        "skipped  package",
        "4 jobs: 1 ok, 1 cached, 1 failed, 1 skipped",
    ]


def test_milestone4_format_report_empty(ex):
    assert ex.format_report({}) == ["0 jobs: 0 ok, 0 cached, 0 failed, 0 skipped"]


@pytest.fixture
def demo(ex):
    runner = ex.Runner(clock=counting_clock())

    @runner.job
    def fetch(deps):
        return [3, 1, 2]

    @runner.job(deps=["fetch"])
    def total(deps):
        return sum(deps["fetch"])

    @runner.job(deps=["fetch"])
    def check(deps):
        raise ValueError("data is not sorted")

    @runner.job(deps=["check", "total"])
    def publish(deps):
        return "published"

    return runner


def test_milestone4_list(ex, demo, capsys):
    assert ex.main(["list"], demo) == 0
    assert capsys.readouterr().out == "fetch\ntotal <- fetch\ncheck <- fetch\npublish <- check, total\n"


def test_milestone4_plan(ex, demo, capsys):
    assert ex.main(["plan", "total"], demo) == 0
    assert capsys.readouterr().out == "fetch\ntotal\n"


def test_milestone4_run_success(ex, demo, capsys):
    assert ex.main(["run", "total"], demo) == 0
    assert capsys.readouterr().out == (
        "ok       fetch (1.00 s)\n"
        "ok       total (1.00 s)\n"
        "2 jobs: 2 ok, 0 cached, 0 failed, 0 skipped\n"
    )


def test_milestone4_run_failure_exit_code(ex, demo, capsys):
    assert ex.main(["run"], demo) == 1
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "ok       fetch (1.00 s)",
        "ok       total (1.00 s)",
        "FAILED   check: ValueError: data is not sorted",
        "skipped  publish",
        "4 jobs: 2 ok, 0 cached, 1 failed, 1 skipped",
    ]


def test_milestone4_run_with_workers(ex, capsys):
    runner = ex.Runner()
    for n in range(3):
        runner.job(lambda d: time.sleep(0.3), name=f"slow{n}")
    start = time.perf_counter()
    assert ex.main(["run", "-j", "3"], runner) == 0
    assert time.perf_counter() - start < 0.8
    assert capsys.readouterr().out.endswith("3 jobs: 3 ok, 0 cached, 0 failed, 0 skipped\n")


def test_milestone4_unknown_job(ex, demo, capsys):
    assert ex.main(["run", "deploy"], demo) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "jobs: error: unknown job 'deploy'\n"


def test_milestone4_cycle(ex, capsys):
    runner = make_runner(ex, {"a": ["b"], "b": ["a"]})
    assert ex.main(["plan"], runner) == 1
    assert capsys.readouterr().err == "jobs: error: cycle: a -> b -> a\n"


def test_milestone4_usage_error(ex, demo):
    with pytest.raises(SystemExit) as info:
        ex.main(["explode"], demo)
    assert info.value.code == 2


def test_milestone4_report_uses_pattern_matching(ex):
    import inspect
    assert ex.format_report({}) is not None
    source = inspect.getsource(ex.format_report)
    assert "match " in source and "case Result(" in source
