"""Tests for assignment 02. Run: pytest advanced/02-context-managers/assignments/02-resource-guards -v"""

import os

import pytest


class FakeClock:
    def __init__(self, *times):
        self.times = list(times)

    def __call__(self):
        return self.times.pop(0)


# --- Timer -------------------------------------------------------------------

def test_timer_measures_with_the_clock(ex):
    with ex.Timer(clock=FakeClock(10.0, 12.5)) as t:
        pass
    assert t.elapsed == 2.5


def test_timer_enter_returns_the_timer(ex):
    timer = ex.Timer(clock=FakeClock(0, 1))
    with timer as t:
        assert t is timer


def test_timer_does_not_start_before_with(ex):
    clock = FakeClock(1.0, 4.0)
    timer = ex.Timer(clock=clock)
    assert len(clock.times) == 2
    with timer:
        pass
    assert timer.elapsed == 3.0


def test_timer_measures_on_error_and_does_not_swallow(ex):
    with pytest.raises(ZeroDivisionError):
        with ex.Timer(clock=FakeClock(0.0, 0.25)) as t:
            1 / 0
    assert t.elapsed == 0.25


def test_timer_real_clock(ex):
    with ex.Timer() as t:
        sum(range(1000))
    assert 0 <= t.elapsed < 5


# --- Suppress ----------------------------------------------------------------

def test_suppress_swallows_listed_exception(ex):
    with ex.Suppress(KeyError) as s:
        {}["missing"]
    assert isinstance(s.error, KeyError)


def test_suppress_swallows_subclasses(ex):
    with ex.Suppress(LookupError, ValueError) as s:
        [][1]
    assert isinstance(s.error, IndexError)


def test_suppress_stops_the_block(ex):
    reached = []
    with ex.Suppress(ValueError):
        int("x")
        reached.append(1)
    assert reached == []


def test_suppress_lets_others_through(ex):
    with pytest.raises(TypeError):
        with ex.Suppress(KeyError):
            len(5)


def test_suppress_no_error(ex):
    with ex.Suppress(KeyError) as s:
        pass
    assert s.error is None


# --- temp_env ----------------------------------------------------------------

@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("PLP_KEEP", "original")
    monkeypatch.delenv("PLP_NEW", raising=False)
    return monkeypatch


def test_temp_env_sets_and_restores(ex, env):
    with ex.temp_env(PLP_KEEP="changed", PLP_NEW="added"):
        assert os.environ["PLP_KEEP"] == "changed"
        assert os.environ["PLP_NEW"] == "added"
    assert os.environ["PLP_KEEP"] == "original"
    assert "PLP_NEW" not in os.environ


def test_temp_env_none_removes(ex, env):
    with ex.temp_env(PLP_KEEP=None, PLP_NEW=None):
        assert "PLP_KEEP" not in os.environ
        assert "PLP_NEW" not in os.environ
    assert os.environ["PLP_KEEP"] == "original"
    assert "PLP_NEW" not in os.environ


def test_temp_env_restores_after_error(ex, env):
    with pytest.raises(KeyError):
        with ex.temp_env(PLP_KEEP="changed", PLP_NEW="added"):
            assert os.environ["PLP_NEW"] == "added"
            raise KeyError
    assert os.environ["PLP_KEEP"] == "original"
    assert "PLP_NEW" not in os.environ


def test_temp_env_restores_changes_made_in_the_block(ex, env):
    with ex.temp_env(PLP_NEW="added"):
        os.environ["PLP_NEW"] = "changed inside"
    assert "PLP_NEW" not in os.environ


# --- transaction -------------------------------------------------------------

def test_transaction_commits(ex):
    account = {"balance": 100, "log": []}
    original = account
    with ex.transaction(account) as draft:
        draft["balance"] -= 30
        draft["log"].append("withdraw 30")
        assert account == {"balance": 100, "log": []}
    assert account is original
    assert account == {"balance": 70, "log": ["withdraw 30"]}


def test_transaction_rolls_back(ex):
    account = {"balance": 100, "log": ["opened"]}
    with pytest.raises(ValueError, match="insufficient"):
        with ex.transaction(account) as draft:
            draft["balance"] -= 500
            draft["log"].append("withdraw 500")
            raise ValueError("insufficient funds")
    assert account == {"balance": 100, "log": ["opened"]}


def test_transaction_commit_removes_deleted_keys(ex):
    data = {"a": 1, "b": 2}
    with ex.transaction(data) as draft:
        del draft["a"]
    assert data == {"b": 2}


# --- open_all ----------------------------------------------------------------

def test_open_all_reads_and_closes(ex, tmp_path):
    paths = []
    for name in "abc":
        path = tmp_path / f"{name}.txt"
        path.write_text(name * 2)
        paths.append(path)
    with ex.open_all(paths) as files:
        assert [f.read() for f in files] == ["aa", "bb", "cc"]
    assert all(f.closed for f in files)


def test_open_all_write_mode(ex, tmp_path):
    paths = [tmp_path / "x.txt", tmp_path / "y.txt"]
    with ex.open_all(paths, "w") as files:
        for f in files:
            f.write("hi")
    assert [p.read_text() for p in paths] == ["hi", "hi"]


def test_open_all_closes_on_error_in_block(ex, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("a")
    with pytest.raises(KeyError):
        with ex.open_all([path]) as files:
            raise KeyError
    assert files[0].closed


def test_open_all_closes_opened_files_when_one_fails(ex, tmp_path, monkeypatch):
    path = tmp_path / "a.txt"
    path.write_text("a")
    opened = []
    real_open = open

    def tracking_open(*args, **kwargs):
        file = real_open(*args, **kwargs)
        opened.append(file)
        return file

    monkeypatch.setattr("builtins.open", tracking_open)
    with pytest.raises(FileNotFoundError):
        with ex.open_all([path, tmp_path / "missing.txt"]):
            pass
    assert len(opened) == 1 and opened[0].closed


def test_open_all_empty(ex):
    with ex.open_all([]) as files:
        assert files == []
