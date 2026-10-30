"""Capstone · Expense tracker.

Replace each `raise NotImplementedError` with your code. Work through the milestones in README.md.
Check your work:  pytest beginner/capstone-expense-tracker -v
"""

import csv
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent / "expenses.csv"
FIELDS = ["date", "category", "amount", "note"]


# ── Milestone 1 · Parse and validate ─────────────────────────────────────────

def parse_amount(text):
    """Return text as a positive float rounded to 2 decimals (spaces and decimal comma allowed).

    Raise ValueError("invalid amount: '<text>'") if it is not a number or not greater than 0.
    """
    raise NotImplementedError


def make_expense(date_text, category, amount_text, note=""):
    """Return a validated expense dict: {'date', 'category', 'amount', 'note'}.

    - date: an ISO date 'YYYY-MM-DD'; else ValueError("invalid date: '<date_text>'")
    - category: stripped and lower-cased; empty -> ValueError("category must not be empty")
    - amount: parsed with parse_amount
    - note: stripped
    """
    raise NotImplementedError


# ── Milestone 2 · Store ──────────────────────────────────────────────────────

def load_expenses(path):
    """Return the list of expenses in the CSV file at path; an empty list if the file does not exist."""
    raise NotImplementedError


def save_expenses(path, expenses):
    """Write all expenses to the CSV file at path (header first, amounts with 2 decimals)."""
    raise NotImplementedError


# ── Milestone 3 · Analyse ────────────────────────────────────────────────────

def total(expenses):
    """Return the sum of all amounts, rounded to 2 decimals."""
    raise NotImplementedError


def filter_by_month(expenses, month):
    """Return the expenses whose date starts with month ('YYYY-MM'), in their original order."""
    raise NotImplementedError


def total_by_category(expenses):
    """Return {category: total}, totals rounded to 2 decimals, largest total first (ties: by name)."""
    raise NotImplementedError


def monthly_report(expenses, month):
    """Return the report text for one month (see README), or 'No expenses for <month>.'"""
    raise NotImplementedError


# ── Milestone 4 · The program ────────────────────────────────────────────────

def main(data_file=DATA_FILE):
    """Run the menu loop: add / list / report / quit (see README)."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
