"""Assignment 10 · Ports and adapters.

legacy_send_overdue_reminders() below works, but it is untestable: it mixes the database, the clock,
the business rules and the mail server in one function. Rebuild it from small parts.
Replace each `raise NotImplementedError` with your code. The data classes, ports and SCHEMA are given.
Check your work:  pytest professional/10-architecture/assignments/10-ports-and-adapters -v
"""

import datetime
import logging
import smtplib
import sqlite3
from dataclasses import dataclass
from itertools import groupby
from typing import Protocol

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL);
CREATE TABLE books   (id INTEGER PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE loans   (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, member_id INTEGER NOT NULL,
                      loaned_on TEXT NOT NULL, returned_on TEXT);
"""


# --- the legacy code: read it, do not change it, do not call it -------------------

def legacy_send_overdue_reminders(db_path, smtp_host):
    conn = sqlite3.connect(db_path)
    today = datetime.date.today()
    rows = conn.execute(
        "SELECT members.name, members.email, books.title, loans.loaned_on FROM loans "
        "JOIN members ON members.id = loans.member_id JOIN books ON books.id = loans.book_id "
        "WHERE loans.returned_on IS NULL"
    ).fetchall()
    by_member = {}
    for name, email, title, loaned_on in rows:
        due = datetime.date.fromisoformat(loaned_on) + datetime.timedelta(days=14)
        if today > due:
            days = (today - due).days
            by_member.setdefault((email, name), []).append((title, days, min(1000, days * 25)))
    with smtplib.SMTP(smtp_host) as smtp:
        for (email, name), books in by_member.items():
            text = f"Hello {name},\n\nthese books are overdue:\n"
            for title, days, fine in books:
                text += f"- {title}: {days} days overdue, fine {fine // 100}.{fine % 100:02d} EUR\n"
            total = sum(fine for _, _, fine in books)
            text += f"\nTotal: {total // 100}.{total % 100:02d} EUR"
            smtp.sendmail("library@example.com", email, f"Subject: {len(books)} overdue book(s)\n\n{text}")


# --- domain: data and pure rules (no I/O, no clock) ----------------------------

@dataclass(frozen=True)
class Loan:
    member_name: str
    member_email: str
    title: str
    loaned_on: datetime.date


@dataclass(frozen=True)
class Reminder:
    to: str
    subject: str
    body: str


def days_overdue(loan, today, grace_days=14):
    """Days past the due date (loaned_on + grace_days), never negative."""
    raise NotImplementedError


def fine_cents(days, per_day=25, cap=1000):
    """days * per_day, at most cap."""
    raise NotImplementedError


def format_cents(cents):
    """1075 -> '10.75 EUR'."""
    raise NotImplementedError


def build_reminders(loans, today, grace_days=14):
    """One Reminder per member with overdue loans, sorted by email. Pure: no I/O."""
    raise NotImplementedError


# --- ports: what the application needs from the outside -------------------------

class LoanRepository(Protocol):
    def open_loans(self) -> list: ...


class Notifier(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class Clock(Protocol):
    def today(self) -> datetime.date: ...


# --- adapters ------------------------------------------------------------------

class InMemoryLoans:
    def __init__(self, loans=()):
        raise NotImplementedError

    def open_loans(self):
        raise NotImplementedError


class SqliteLoans:
    def __init__(self, conn):
        raise NotImplementedError

    def open_loans(self):
        raise NotImplementedError


class RecordingNotifier:
    def __init__(self):
        raise NotImplementedError

    def send(self, to, subject, body):
        raise NotImplementedError


class FixedClock:
    def __init__(self, day):
        raise NotImplementedError

    def today(self):
        raise NotImplementedError


class SystemClock:
    def today(self):
        raise NotImplementedError


# --- application: the use case, a thin shell around the core ---------------------

class ReminderService:
    def __init__(self, loans, notifier, clock, grace_days=14):
        raise NotImplementedError

    def run(self):
        """Build the reminders and send them; return how many were sent."""
        raise NotImplementedError


def build_service(conn, notifier):
    """The composition root: SqliteLoans + the given notifier + SystemClock."""
    raise NotImplementedError


if __name__ == "__main__":
    loans = [
        Loan("Ada", "ada@example.com", "Mort", datetime.date(2026, 10, 15)),
        Loan("Ada", "ada@example.com", "Dune", datetime.date(2026, 9, 1)),
        Loan("Bob", "bob@example.com", "Emma", datetime.date(2026, 10, 30)),
    ]
    for reminder in build_reminders(loans, datetime.date(2026, 11, 1)):
        print(f"To: {reminder.to}\nSubject: {reminder.subject}\n\n{reminder.body}\n")
