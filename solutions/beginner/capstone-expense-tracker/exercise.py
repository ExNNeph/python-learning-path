"""Capstone · Expense tracker: template solution.

The structure follows lesson 04: pure functions in the middle (milestones 1 and 3),
file access in two small functions (milestone 2), and all input()/print() in main().
"""

import csv
from datetime import date
from pathlib import Path

# Path(__file__).parent: next to this script, whatever folder the user starts from (lesson 11).
DATA_FILE = Path(__file__).parent / "expenses.csv"
FIELDS = ["date", "category", "amount", "note"]


# ── Milestone 1 · Parse and validate ─────────────────────────────────────────

def parse_amount(text):
    """Return text as a positive float rounded to 2 decimals (spaces and decimal comma allowed)."""
    # EAFP (lesson 10): try the conversion, translate the failure into our own message.
    try:
        amount = float(text.strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"invalid amount: '{text}'") from None
    # A number, but not a valid expense. Same message, so the user sees one clear rule.
    if amount <= 0:
        raise ValueError(f"invalid amount: '{text}'")
    return round(amount, 2)


def make_expense(date_text, category, amount_text, note=""):
    """Return a validated expense dict: {'date', 'category', 'amount', 'note'}."""
    # Every expense in the program goes through this one function, whether it comes from
    # the keyboard or from the CSV file. So "is this a valid expense?" is answered once.
    date_text = date_text.strip()
    try:
        date.fromisoformat(date_text)       # only used to validate; we keep the text
    except ValueError:
        raise ValueError(f"invalid date: '{date_text}'") from None

    category = category.strip().lower()     # "Food " and "food" are the same category
    if not category:
        raise ValueError("category must not be empty")

    return {
        "date": date_text,
        "category": category,
        "amount": parse_amount(amount_text),
        "note": note.strip(),
    }


# ── Milestone 2 · Store ──────────────────────────────────────────────────────

def load_expenses(path):
    """Return the list of expenses in the CSV file at path; an empty list if the file does not exist."""
    # On the very first run there is no file yet. That is normal, not an error,
    # so here (unlike the log analyzer) catching FileNotFoundError is the right call.
    try:
        with open(path, newline="", encoding="utf-8") as file:
            # DictReader turns each row into a dict keyed by the header (lesson 11).
            # Validating every row means a hand-edited, broken file fails loudly at load
            # time instead of producing wrong totals later.
            return [
                make_expense(row["date"], row["category"], row["amount"], row["note"] or "")
                for row in csv.DictReader(file)
            ]
    except FileNotFoundError:
        return []


def save_expenses(path, expenses):
    """Write all expenses to the CSV file at path (header first, amounts with 2 decimals)."""
    # Rewriting the whole file ("w") keeps it simple and always consistent.
    # That is fast enough for thousands of rows; for huge files you would append instead.
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for expense in expenses:
            # A new dict, so the caller's expense keeps its float amount.
            writer.writerow({**expense, "amount": f"{expense['amount']:.2f}"})


# ── Milestone 3 · Analyse ────────────────────────────────────────────────────

def total(expenses):
    """Return the sum of all amounts, rounded to 2 decimals."""
    # Rounding at the end hides float noise such as 0.1 + 0.2 (lesson 03).
    return round(sum(expense["amount"] for expense in expenses), 2)


def filter_by_month(expenses, month):
    """Return the expenses whose date starts with month ('YYYY-MM'), in their original order."""
    # ISO dates make this a plain string test: "2026-10-05".startswith("2026-10").
    return [expense for expense in expenses if expense["date"].startswith(month + "-")]


def total_by_category(expenses):
    """Return {category: total}, totals rounded to 2 decimals, largest total first (ties: by name)."""
    totals = {}
    for expense in expenses:                                   # the counting pattern (lesson 08),
        category = expense["category"]                         # summing instead of counting
        totals[category] = totals.get(category, 0) + expense["amount"]
    # Dicts keep insertion order, so building a new dict from sorted pairs sorts it.
    ranked = sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))
    return {category: round(amount, 2) for category, amount in ranked}


def monthly_report(expenses, month):
    """Return the report text for one month (see README), or 'No expenses for <month>.'"""
    selected = filter_by_month(expenses, month)
    if not selected:
        return f"No expenses for {month}."

    width = 28
    lines = [f"Expenses for {month}", "=" * width]
    for category, amount in total_by_category(selected).items():
        lines.append(f"{category:<20}{amount:>8.2f}")
    lines.append("-" * width)
    lines.append(f"{'TOTAL':<20}{total(selected):>8.2f}")
    # Building a list and joining once is clearer (and faster) than += on a string.
    return "\n".join(lines)


# ── Milestone 4 · The program ────────────────────────────────────────────────

def add_expense_interactively():
    """Ask for one expense; return it, or None after printing the validation error."""
    date_text = input("Date (YYYY-MM-DD, empty = today): ").strip() or date.today().isoformat()
    category = input("Category: ")
    amount = input("Amount: ")
    note = input("Note (optional): ")
    try:
        return make_expense(date_text, category, amount, note)
    except ValueError as error:
        # The boundary to the user: the one place that turns exceptions into messages.
        print(f"Error: {error}")
        return None


def print_list(expenses):
    if not expenses:
        print("No expenses yet.")
        return
    for expense in expenses:
        print(f"{expense['date']}  {expense['category']:<12}{expense['amount']:>9.2f}  {expense['note']}")


def main(data_file=DATA_FILE):
    """Run the menu loop: add / list / report / quit (see README)."""
    # data_file is a parameter so the tests can point it at a temporary file.
    expenses = load_expenses(data_file)
    print(f"Expense tracker · {len(expenses)} expenses loaded")
    while True:
        command = input("Command (add, list, report, quit): ").strip().lower()
        if command == "add":
            expense = add_expense_interactively()
            if expense is not None:
                expenses.append(expense)
                save_expenses(data_file, expenses)   # save right away: nothing lost on Ctrl+C
                print("Saved.")
        elif command == "list":
            print_list(expenses)
        elif command == "report":
            month = input("Month (YYYY-MM): ").strip()
            print(monthly_report(expenses, month))
        elif command == "quit":
            print("Bye!")
            break
        else:
            print(f"Unknown command: '{command}'")


if __name__ == "__main__":
    main()
