"""Tests for the capstone. Run one milestone: pytest intermediate/capstone-task-tracker -v -k milestone1"""

import dataclasses
import inspect
import json
from datetime import date

import pytest

TODAY = date(2026, 10, 31)          # a Saturday: every test uses this fixed "today"


# ---------------------------------------------------------------------------
# Milestone 1 · The model
# ---------------------------------------------------------------------------

def test_milestone1_priority(ex):
    assert [(p.name, p.value) for p in ex.Priority] == [("LOW", 1), ("NORMAL", 2), ("HIGH", 3)]


def test_milestone1_task_is_a_dataclass(ex):
    assert dataclasses.is_dataclass(ex.Task)
    assert [f.name for f in dataclasses.fields(ex.Task)] == ["id", "title", "priority", "due", "tags", "done"]


def test_milestone1_task_defaults(ex):
    task = ex.Task(1, "Buy milk")
    assert (task.priority, task.due, task.tags, task.done) == (ex.Priority.NORMAL, None, set(), False)
    other = ex.Task(2, "Other")
    task.tags.add("x")
    assert other.tags == set()


def test_milestone1_task_normalises(ex):
    task = ex.Task(1, "  Buy milk ", tags={"Home", "SHOP"})
    assert task.title == "Buy milk"
    assert task.tags == {"home", "shop"}


def test_milestone1_task_empty_title(ex):
    with pytest.raises(ValueError):
        ex.Task(1, "   ")


def test_milestone1_is_overdue(ex):
    assert ex.Task(1, "a", due=date(2026, 10, 30)).is_overdue(TODAY) is True
    assert ex.Task(1, "a", due=TODAY).is_overdue(TODAY) is False
    assert ex.Task(1, "a").is_overdue(TODAY) is False
    assert ex.Task(1, "a", due=date(2026, 10, 30), done=True).is_overdue(TODAY) is False


def test_milestone1_to_dict(ex):
    task = ex.Task(7, "Buy milk", ex.Priority.HIGH, date(2026, 11, 6), {"shop", "home"})
    assert task.to_dict() == {
        "id": 7, "title": "Buy milk", "priority": "high", "due": "2026-11-06", "tags": ["home", "shop"], "done": False,
    }
    assert ex.Task(1, "x").to_dict()["due"] is None


def test_milestone1_from_dict_round_trip(ex):
    task = ex.Task(7, "Buy milk", ex.Priority.LOW, date(2026, 11, 6), {"home"}, done=True)
    assert ex.Task.from_dict(task.to_dict()) == task
    assert ex.Task.from_dict(json.loads(json.dumps(task.to_dict()))) == task


def test_milestone1_from_dict_defaults(ex):
    assert ex.Task.from_dict({"id": 3, "title": "Minimal"}) == ex.Task(3, "Minimal")


@pytest.mark.parametrize("data", [
    None, [], {"title": "no id"}, {"id": 1}, {"id": 1, "title": " "}, {"id": "x", "title": "a"},
    {"id": 1, "title": "a", "priority": "urgent"}, {"id": 1, "title": "a", "due": "soon"},
])
def test_milestone1_from_dict_invalid(ex, data):
    with pytest.raises(ex.TaskError):
        ex.Task.from_dict(data)


def test_milestone1_exception_hierarchy(ex):
    assert issubclass(ex.TaskNotFound, ex.TaskError)
    assert issubclass(ex.TaskNotFound, KeyError)


# ---------------------------------------------------------------------------
# Milestone 2 · Parsing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("today", date(2026, 10, 31)),
    ("Tomorrow", date(2026, 11, 1)),
    ("mon", date(2026, 11, 2)),
    ("friday", date(2026, 11, 6)),
    ("sat", date(2026, 11, 7)),            # today is a Saturday: the NEXT one
    ("2026-12-24", date(2026, 12, 24)),
])
def test_milestone2_parse_due(ex, text, expected):
    assert ex.parse_due(text, TODAY) == expected


@pytest.mark.parametrize("text", ["soon", "24.12.2026", "2026-02-30", ""])
def test_milestone2_parse_due_invalid(ex, text):
    with pytest.raises(ValueError):
        ex.parse_due(text, TODAY)


def test_milestone2_parse_task_text(ex):
    assert ex.parse_task_text("Buy milk due:fri #home !high", TODAY) == (
        "Buy milk", ex.Priority.HIGH, date(2026, 11, 6), {"home"},
    )


def test_milestone2_markers_anywhere(ex):
    assert ex.parse_task_text("#Work !low Write   the report #urgent due:2026-11-20", TODAY) == (
        "Write the report", ex.Priority.LOW, date(2026, 11, 20), {"work", "urgent"},
    )


def test_milestone2_plain_title(ex):
    assert ex.parse_task_text("  Call Grace ", TODAY) == ("Call Grace", ex.Priority.NORMAL, None, set())


def test_milestone2_exclamation_inside_title_is_kept(ex):
    assert ex.parse_task_text("Say hi!", TODAY)[0] == "Say hi!"


@pytest.mark.parametrize("text", [
    "", "#home !high", "Task !urgent", "Task due:someday", "Task due:fri due:mon", "Task !low !high",
])
def test_milestone2_invalid_text(ex, text):
    with pytest.raises(ValueError):
        ex.parse_task_text(text, TODAY)


# ---------------------------------------------------------------------------
# Milestone 3 · TaskList and storage
# ---------------------------------------------------------------------------

@pytest.fixture
def tasks(ex):
    task_list = ex.TaskList()
    task_list.add("Buy milk due:fri #home !high", TODAY)            # 1
    task_list.add("Write report due:2026-10-01 #work", TODAY)       # 2  overdue
    task_list.add("Call Grace #home", TODAY)                        # 3
    task_list.add("Plan trip !low", TODAY)                          # 4
    task_list.add("Water plants due:fri #home", TODAY)              # 5
    return task_list


def test_milestone3_add_assigns_ids(ex, tasks):
    assert len(tasks) == 5
    assert [task.id for task in tasks] == [1, 2, 3, 4, 5]
    assert tasks.get(1).title == "Buy milk"
    assert tasks.next_id() == 6


def test_milestone3_ids_continue_after_highest(ex):
    task_list = ex.TaskList([ex.Task(4, "a"), ex.Task(9, "b")])
    assert task_list.add("c", TODAY).id == 10
    assert ex.TaskList().next_id() == 1


def test_milestone3_add_invalid_text_changes_nothing(ex, tasks):
    with pytest.raises(ValueError):
        tasks.add("!high", TODAY)
    assert len(tasks) == 5


def test_milestone3_get_unknown(ex, tasks):
    with pytest.raises(ex.TaskNotFound, match="no task with id 42"):
        tasks.get(42)


def test_milestone3_complete_and_remove(ex, tasks):
    assert tasks.complete(3).done is True
    assert tasks.get(3).done is True
    removed = tasks.remove(4)
    assert removed.title == "Plan trip"
    assert len(tasks) == 4
    with pytest.raises(ex.TaskNotFound):
        tasks.remove(4)
    with pytest.raises(ex.TaskNotFound):
        tasks.complete(99)


def test_milestone3_filter(ex, tasks):
    tasks.complete(3)
    assert [t.id for t in tasks.filter(tag="home")] == [1, 3, 5]
    assert [t.id for t in tasks.filter(tag="HOME", done=False)] == [1, 5]
    assert [t.id for t in tasks.filter(done=True)] == [3]
    assert [t.id for t in tasks.filter()] == [1, 2, 3, 4, 5]


def test_milestone3_filter_is_a_generator(ex, tasks):
    assert inspect.isgenerator(tasks.filter())


def test_milestone3_sorted(ex, tasks):
    tasks.complete(2)
    # open first; due date earliest first, none last; high priority first; then id
    assert [t.id for t in tasks.sorted()] == [1, 5, 3, 4, 2]


def test_milestone3_sorted_subset(ex, tasks):
    assert [t.id for t in tasks.sorted(tasks.filter(tag="home"))] == [1, 5, 3]


def test_milestone3_stats(ex, tasks):
    tasks.complete(1)
    stats = tasks.stats(TODAY)
    assert (stats.total, stats.done, stats.open, stats.overdue) == (5, 1, 4, 1)
    assert stats.tags == {"home": 2, "work": 1}
    assert list(stats.tags) == ["home", "work"]


def test_milestone3_save_and_load(ex, tasks, tmp_path):
    path = tmp_path / "tasks.json"
    tasks.complete(3)
    tasks.save(path)
    loaded = ex.TaskList.load(path)
    assert sorted(loaded, key=lambda t: t.id) == sorted(tasks, key=lambda t: t.id)
    assert [p.name for p in tmp_path.iterdir()] == ["tasks.json"]


def test_milestone3_file_format(ex, tasks, tmp_path):
    path = tmp_path / "tasks.json"
    tasks.save(str(path))
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["version"] == 1
    assert document["tasks"][0] == tasks.get(1).to_dict()
    assert '\n  "tasks"' in path.read_text(encoding="utf-8"), "use indent=2"


def test_milestone3_load_missing_file(ex, tmp_path):
    assert len(ex.TaskList.load(tmp_path / "nope.json")) == 0


@pytest.mark.parametrize("content", [
    "{not json", "[]", '{"version": 2, "tasks": []}', '{"version": 1, "tasks": {}}',
    '{"version": 1, "tasks": [{"id": 1}]}',
    '{"version": 1, "tasks": [{"id": 1, "title": "a"}, {"id": 1, "title": "b"}]}',
])
def test_milestone3_load_invalid(ex, tmp_path, content):
    path = tmp_path / "tasks.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ex.TaskError):
        ex.TaskList.load(path)


# ---------------------------------------------------------------------------
# Milestone 4 · The command line
# ---------------------------------------------------------------------------

def test_milestone4_format_task(ex):
    task = ex.Task(1, "Buy milk", ex.Priority.HIGH, date(2026, 11, 6), {"shop", "home"})
    assert ex.format_task(task, TODAY) == "  1 [ ] Buy milk !high due:2026-11-06 #home #shop"
    late = ex.Task(12, "Write report", due=date(2026, 10, 1))
    assert ex.format_task(late, TODAY) == " 12 [ ] Write report due:2026-10-01 (overdue)"
    done = ex.Task(3, "Call Grace", ex.Priority.LOW, done=True)
    assert ex.format_task(done, TODAY) == "  3 [x] Call Grace !low"


@pytest.fixture
def cli(ex, tmp_path, capsys):
    """Run the CLI on a temporary task file: cli("add", "Buy milk") -> (exit code, stdout, stderr)."""
    path = tmp_path / "tasks.json"

    def run(*args):
        code = ex.main(["--file", str(path), *args], today=TODAY)
        captured = capsys.readouterr()
        return code, captured.out, captured.err
    run.path = path
    return run


def test_milestone4_add(cli):
    assert cli("add", "Buy", "milk", "due:fri", "#home", "!high") == (0, "Added task 1: Buy milk\n", "")
    assert cli("add", "Call Grace") == (0, "Added task 2: Call Grace\n", "")
    assert cli.path.exists()


def test_milestone4_list(cli):
    cli("add", "Buy milk due:fri #home !high")
    cli("add", "Write report due:2026-10-01 #work")
    cli("add", "Call Grace #home")
    cli("done", "3")
    code, out, _ = cli("list")
    assert code == 0
    assert out == "  2 [ ] Write report due:2026-10-01 #work (overdue)\n  1 [ ] Buy milk !high due:2026-11-06 #home\n"
    assert cli("list", "--all")[1].splitlines()[-1] == "  3 [x] Call Grace #home"
    assert cli("list", "--tag", "home")[1] == "  1 [ ] Buy milk !high due:2026-11-06 #home\n"


def test_milestone4_list_empty(cli):
    assert cli("list") == (0, "No tasks.\n", "")
    assert not cli.path.exists(), "listing must not create the file"


def test_milestone4_done_and_remove(cli):
    cli("add", "Call Grace")
    assert cli("done", "1") == (0, "Completed task 1: Call Grace\n", "")
    assert cli("remove", "1") == (0, "Removed task 1: Call Grace\n", "")
    assert cli("list", "--all")[1] == "No tasks.\n"


def test_milestone4_stats(cli):
    cli("add", "Buy milk #home !high")
    cli("add", "Write report due:2026-10-01 #work")
    cli("add", "Water plants #home")
    cli("done", "1")
    assert cli("stats") == (0, "3 tasks: 1 done, 2 open, 1 overdue\nopen by tag: #home 1, #work 1\n", "")


def test_milestone4_changes_are_saved(ex, cli):
    cli("add", "Persist me")
    assert ex.TaskList.load(cli.path).get(1).title == "Persist me"


@pytest.mark.parametrize("args, message", [
    (("done", "9"), "tasks: error: no task with id 9\n"),
    (("remove", "9"), "tasks: error: no task with id 9\n"),
    (("add", "!high"), "tasks: error: title must not be empty\n"),
    (("add", "Task", "due:someday"), "tasks: error: invalid due date: 'someday'\n"),
])
def test_milestone4_errors(cli, args, message):
    assert cli(*args) == (1, "", message)


def test_milestone4_corrupt_file(cli):
    cli.path.write_text("{oops", encoding="utf-8")
    code, out, err = cli("list")
    assert (code, out) == (1, "")
    assert err.startswith("tasks: error: tasks.json is not valid JSON")


def test_milestone4_failed_command_does_not_save(ex, cli):
    cli("add", "Keep me")
    before = cli.path.read_text(encoding="utf-8")
    cli("done", "9")
    assert cli.path.read_text(encoding="utf-8") == before


def test_milestone4_usage_errors(ex, cli):
    for args in (["done", "one"], ["frobnicate"], []):
        with pytest.raises(SystemExit) as exit_info:
            ex.main(["--file", str(cli.path), *args], today=TODAY)
        assert exit_info.value.code == 2
