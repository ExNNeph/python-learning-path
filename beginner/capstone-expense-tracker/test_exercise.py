"""Tests for the capstone. Run: pytest beginner/capstone-expense-tracker -v

The tests follow the milestones in README.md. Run one milestone at a time with -k, e.g.:
    pytest beginner/capstone-expense-tracker -v -k milestone1
"""

import pytest


def expense(date, category, amount, note=""):
    return {"date": date, "category": category, "amount": amount, "note": note}


@pytest.fixture
def october():
    return [
        expense("2026-09-28", "food", 18.4),
        expense("2026-10-01", "food", 12.5, "lunch"),
        expense("2026-10-02", "transport", 2.9),
        expense("2026-10-05", "food", 31.2),
        expense("2026-10-07", "fun", 15.0),
        expense("2026-10-12", "transport", 49.0),
        expense("2026-11-01", "rent", 750.0),
    ]


# ── Milestone 1 · Parse and validate ─────────────────────────────────────────

@pytest.mark.parametrize("text, expected", [("12.50", 12.5), (" 3,99 ", 3.99), ("7", 7.0), ("0.005", 0.01), ("1e2", 100.0)])
def test_milestone1_parse_amount(ex, text, expected):
    assert ex.parse_amount(text) == expected


@pytest.mark.parametrize("text", ["abc", "", "0", "-5", "12.50 EUR"])
def test_milestone1_parse_amount_invalid(ex, text):
    with pytest.raises(ValueError) as info:
        ex.parse_amount(text)
    assert str(info.value) == f"invalid amount: '{text}'"


def test_milestone1_make_expense(ex):
    assert ex.make_expense("2026-10-01", "  Food ", "12,50", " lunch ") == expense("2026-10-01", "food", 12.5, "lunch")


def test_milestone1_make_expense_note_is_optional(ex):
    assert ex.make_expense("2026-10-01", "fun", "5") == expense("2026-10-01", "fun", 5.0, "")


@pytest.mark.parametrize("date_text", ["2026-13-01", "01.10.2026", "", "yesterday", "2026-02-30"])
def test_milestone1_make_expense_invalid_date(ex, date_text):
    with pytest.raises(ValueError) as info:
        ex.make_expense(date_text, "food", "1")
    assert str(info.value) == f"invalid date: '{date_text}'"


@pytest.mark.parametrize("category", ["", "   "])
def test_milestone1_make_expense_empty_category(ex, category):
    with pytest.raises(ValueError) as info:
        ex.make_expense("2026-10-01", category, "1")
    assert str(info.value) == "category must not be empty"


def test_milestone1_make_expense_invalid_amount(ex):
    with pytest.raises(ValueError, match="invalid amount"):
        ex.make_expense("2026-10-01", "food", "free")


# ── Milestone 2 · Store ──────────────────────────────────────────────────────

def test_milestone2_load_missing_file_gives_empty_list(ex, tmp_path):
    assert ex.load_expenses(tmp_path / "nothing-here.csv") == []


def test_milestone2_save_writes_csv(ex, tmp_path, october):
    path = tmp_path / "expenses.csv"
    ex.save_expenses(path, october[:2])
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines == [
        "date,category,amount,note",
        "2026-09-28,food,18.40,",
        "2026-10-01,food,12.50,lunch",
    ]


def test_milestone2_round_trip(ex, tmp_path, october):
    path = tmp_path / "expenses.csv"
    october[0]["note"] = 'cinema, with "popcorn"'
    ex.save_expenses(path, october)
    assert ex.load_expenses(path) == october


def test_milestone2_save_does_not_change_amounts(ex, tmp_path, october):
    ex.save_expenses(tmp_path / "expenses.csv", october)
    assert october[1]["amount"] == 12.5


def test_milestone2_load_validates_rows(ex, tmp_path):
    path = tmp_path / "broken.csv"
    path.write_text("date,category,amount,note\n2026-10-01,food,lots,\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ex.load_expenses(path)


def test_milestone2_load_sample_file(ex, request):
    sample = request.path.parent / "sample-expenses.csv"
    expenses = ex.load_expenses(sample)
    assert len(expenses) == 9
    assert expenses[5] == expense("2026-10-07", "fun", 15.0, "cinema, with popcorn")


# ── Milestone 3 · Analyse ────────────────────────────────────────────────────

def test_milestone3_total(ex, october):
    assert ex.total(october) == 879.0


def test_milestone3_total_rounds(ex):
    assert ex.total([expense("2026-10-01", "a", 0.1), expense("2026-10-01", "a", 0.2)]) == 0.3


def test_milestone3_total_empty(ex):
    assert ex.total([]) == 0


def test_milestone3_filter_by_month(ex, october):
    result = ex.filter_by_month(october, "2026-10")
    assert [e["date"] for e in result] == ["2026-10-01", "2026-10-02", "2026-10-05", "2026-10-07", "2026-10-12"]


def test_milestone3_filter_by_month_none(ex, october):
    assert ex.filter_by_month(october, "2025-10") == []


def test_milestone3_total_by_category(ex, october):
    result = ex.total_by_category(ex.filter_by_month(october, "2026-10"))
    assert result == {"transport": 51.9, "food": 43.7, "fun": 15.0}
    assert list(result) == ["transport", "food", "fun"]


def test_milestone3_total_by_category_ties_by_name(ex):
    result = ex.total_by_category([expense("2026-10-01", "b", 5.0), expense("2026-10-01", "a", 5.0)])
    assert list(result) == ["a", "b"]


def test_milestone3_monthly_report(ex, october):
    assert ex.monthly_report(october, "2026-10") == (
        "Expenses for 2026-10\n"
        "============================\n"
        "transport              51.90\n"
        "food                   43.70\n"
        "fun                    15.00\n"
        "----------------------------\n"
        "TOTAL                 110.60"
    )


def test_milestone3_monthly_report_empty(ex, october):
    assert ex.monthly_report(october, "2026-12") == "No expenses for 2026-12."


# ── Milestone 4 · The program ────────────────────────────────────────────────

@pytest.fixture
def type_answers(monkeypatch):
    def setup(*answers):
        remaining = iter(answers)
        monkeypatch.setattr("builtins.input", lambda prompt="": next(remaining))

    return setup


def test_milestone4_add_saves_to_file(ex, tmp_path, type_answers, capsys):
    data = tmp_path / "expenses.csv"
    type_answers("add", "2026-10-01", "Food", "12,50", "lunch", "quit")
    ex.main(data)
    assert ex.load_expenses(data) == [expense("2026-10-01", "food", 12.5, "lunch")]
    out = capsys.readouterr().out
    assert "0 expenses loaded" in out
    assert "Saved." in out


def test_milestone4_invalid_input_does_not_crash(ex, tmp_path, type_answers, capsys):
    data = tmp_path / "expenses.csv"
    type_answers("add", "2026-10-01", "food", "free", "", "quit")
    ex.main(data)
    assert "Error: invalid amount: 'free'" in capsys.readouterr().out
    assert ex.load_expenses(data) == []


def test_milestone4_report(ex, tmp_path, type_answers, capsys, october):
    data = tmp_path / "expenses.csv"
    ex.save_expenses(data, october)
    type_answers("report", "2026-10", "quit")
    ex.main(data)
    out = capsys.readouterr().out
    assert "7 expenses loaded" in out
    assert "TOTAL                 110.60" in out


def test_milestone4_list_and_unknown_command(ex, tmp_path, type_answers, capsys, october):
    data = tmp_path / "expenses.csv"
    ex.save_expenses(data, october)
    type_answers("list", "dance", "quit")
    ex.main(data)
    out = capsys.readouterr().out
    assert "lunch" in out
    assert "Unknown command: 'dance'" in out
