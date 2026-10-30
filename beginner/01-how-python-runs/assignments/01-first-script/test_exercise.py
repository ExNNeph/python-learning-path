"""Tests for assignment 01. Run: pytest beginner/01-how-python-runs/assignments/01-first-script -v"""


def test_greeting_ada(ex):
    assert ex.greeting("Ada") == "Hello, Ada! Welcome to Python."


def test_greeting_other_name(ex):
    assert ex.greeting("Grace") == "Hello, Grace! Welcome to Python."


def test_seconds_in_one_day(ex):
    assert ex.seconds_in_days(1) == 86400


def test_seconds_in_zero_days(ex):
    assert ex.seconds_in_days(0) == 0


def test_seconds_in_a_week(ex):
    assert ex.seconds_in_days(7) == 604800


def test_main_prints_two_lines(ex, capsys):
    ex.main()
    assert capsys.readouterr().out == (
        "Hello, World! Welcome to Python.\n"
        "A week has 604800 seconds.\n"
    )
