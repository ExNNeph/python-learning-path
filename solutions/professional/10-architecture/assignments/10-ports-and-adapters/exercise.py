"""Assignment 10 · Ports and adapters: template solution."""

import datetime
import logging
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
    due = loan.loaned_on + datetime.timedelta(days=grace_days)
    return max(0, (today - due).days)


def fine_cents(days, per_day=25, cap=1000):
    return min(cap, days * per_day)


def format_cents(cents):
    return f"{cents // 100}.{cents % 100:02d} EUR"


def build_reminders(loans, today, grace_days=14):
    overdue = [(loan, days_overdue(loan, today, grace_days)) for loan in loans]
    overdue = [(loan, days) for loan, days in overdue if days > 0]
    # One reminder per member: sort by email, then group; inside, oldest loan first.
    overdue.sort(key=lambda pair: (pair[0].member_email, pair[0].loaned_on, pair[0].title))
    reminders = []
    for email, group in groupby(overdue, key=lambda pair: pair[0].member_email):
        group = list(group)
        lines = [f"- {loan.title}: {days} days overdue, fine {format_cents(fine_cents(days))}"
                 for loan, days in group]
        total = sum(fine_cents(days) for _, days in group)
        body = "\n".join([
            f"Hello {group[0][0].member_name},",
            "",
            "these books are overdue:",
            *lines,
            "",
            f"Total: {format_cents(total)}",
        ])
        reminders.append(Reminder(email, f"{len(group)} overdue book(s)", body))
    return reminders


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
        self.loans = list(loans)

    def open_loans(self):
        return list(self.loans)


class SqliteLoans:
    def __init__(self, conn):
        self.conn = conn

    def open_loans(self):
        rows = self.conn.execute(
            """SELECT members.name, members.email, books.title, loans.loaned_on
               FROM loans
               JOIN members ON members.id = loans.member_id
               JOIN books ON books.id = loans.book_id
               WHERE loans.returned_on IS NULL
               ORDER BY loans.id"""
        )
        return [Loan(name, email, title, datetime.date.fromisoformat(day)) for name, email, title, day in rows]


class RecordingNotifier:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))


class FixedClock:
    def __init__(self, day):
        self.day = day

    def today(self):
        return self.day


class SystemClock:
    def today(self):
        return datetime.date.today()


# --- application: the use case, a thin shell around the core ---------------------

class ReminderService:
    def __init__(self, loans, notifier, clock, grace_days=14):
        self.loans = loans
        self.notifier = notifier
        self.clock = clock
        self.grace_days = grace_days

    def run(self):
        reminders = build_reminders(self.loans.open_loans(), self.clock.today(), self.grace_days)
        sent = 0
        for reminder in reminders:
            try:
                self.notifier.send(reminder.to, reminder.subject, reminder.body)
                sent += 1
            except Exception:
                # One bad address must not stop the reminders for everybody else.
                log.exception("could not send reminder to %s", reminder.to)
        return sent


def build_service(conn, notifier):
    """The composition root: the real adapters, wired together."""
    return ReminderService(SqliteLoans(conn), notifier, SystemClock())


if __name__ == "__main__":
    loans = [
        Loan("Ada", "ada@example.com", "Mort", datetime.date(2026, 10, 15)),
        Loan("Ada", "ada@example.com", "Dune", datetime.date(2026, 9, 1)),
        Loan("Bob", "bob@example.com", "Emma", datetime.date(2026, 10, 30)),
    ]
    for reminder in build_reminders(loans, datetime.date(2026, 11, 1)):
        print(f"To: {reminder.to}\nSubject: {reminder.subject}\n\n{reminder.body}\n")
