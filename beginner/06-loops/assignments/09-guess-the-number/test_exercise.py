"""Tests for assignment 09. Run: pytest beginner/06-loops/assignments/09-guess-the-number -v"""

import pytest


@pytest.fixture
def type_answers(monkeypatch):
    """Replace input() with a fake that returns the given answers one by one."""

    def setup(*answers):
        remaining = iter(answers)
        monkeypatch.setattr("builtins.input", lambda prompt: next(remaining))

    return setup


@pytest.mark.parametrize("guess, expected", [(10, "too low"), (90, "too high"), (42, "correct")])
def test_hint(ex, guess, expected):
    assert ex.hint(guess, 42) == expected


def test_play_win_first_try(ex, type_answers, capsys):
    type_answers("42")
    assert ex.play(42) == 1
    assert capsys.readouterr().out == "correct\nYou got it in 1 try!\n"


def test_play_win_after_hints(ex, type_answers, capsys):
    type_answers("50", "25", "37")
    assert ex.play(37) == 3
    assert capsys.readouterr().out == "too high\ntoo low\ncorrect\nYou got it in 3 tries!\n"


def test_play_invalid_input_does_not_count(ex, type_answers, capsys):
    type_answers("fifty", "4.2", "", "50")
    assert ex.play(50, max_tries=1) == 1
    out = capsys.readouterr().out
    assert out.count("Please enter a whole number.") == 3
    assert out.endswith("correct\nYou got it in 1 try!\n")


def test_play_accepts_spaces_around_number(ex, type_answers):
    type_answers(" 7 ")
    assert ex.play(7) == 1


def test_play_out_of_tries(ex, type_answers, capsys):
    type_answers("1", "2", "3")
    assert ex.play(99, max_tries=3) is None
    assert capsys.readouterr().out == "too low\ntoo low\ntoo low\nOut of tries. The number was 99.\n"


def test_play_stops_asking_after_win(ex, type_answers):
    type_answers("5", "should never be read")
    assert ex.play(5) == 1
