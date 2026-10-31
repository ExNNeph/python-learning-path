"""Tests for assignment 10. Run: pytest professional/10-architecture/assignments/10-ports-and-adapters -v"""

import datetime
import logging
import sqlite3

import pytest

D = datetime.date
TODAY = D(2026, 11, 1)


def loan(ex, name, title, loaned_on, email=None):
    return ex.Loan(name, email or f"{name.lower()}@example.com", title, loaned_on)


@pytest.fixture
def loans(ex):
    return [
        loan(ex, "Ada", "Mort", D(2026, 10, 15)),        # due 10-29: 3 days overdue
        loan(ex, "Bob", "Emma", D(2026, 10, 30)),        # not overdue
        loan(ex, "Ada", "Dune", D(2026, 9, 1)),          # due 09-15: 47 days overdue
        loan(ex, "Cleo", "Beloved", D(2026, 10, 18)),    # due exactly today: not overdue
        loan(ex, "Bob", "Ulysses", D(2026, 10, 1)),      # due 10-15: 17 days overdue
    ]


ADA_BODY = """Hello Ada,

these books are overdue:
- Dune: 47 days overdue, fine 10.00 EUR
- Mort: 3 days overdue, fine 0.75 EUR

Total: 10.75 EUR"""


# --- the pure core -------------------------------------------------------------

@pytest.mark.parametrize("loaned_on, grace, expected", [
    (D(2026, 10, 18), 14, 0),
    (D(2026, 10, 17), 14, 1),
    (D(2026, 11, 1), 14, 0),
    (D(2026, 9, 1), 14, 47),
    (D(2026, 10, 30), 0, 2),
    (D(2026, 10, 1), 30, 1),
])
def test_days_overdue(ex, loaned_on, grace, expected):
    assert ex.days_overdue(loan(ex, "Ada", "X", loaned_on), TODAY, grace) == expected


@pytest.mark.parametrize("days, expected", [(0, 0), (1, 25), (39, 975), (40, 1000), (41, 1000), (365, 1000)])
def test_fine_cents(ex, days, expected):
    assert ex.fine_cents(days) == expected


def test_fine_cents_custom(ex):
    assert ex.fine_cents(3, per_day=50, cap=120) == 120
    assert ex.fine_cents(2, per_day=50, cap=120) == 100


@pytest.mark.parametrize("cents, text", [(1075, "10.75 EUR"), (5, "0.05 EUR"), (0, "0.00 EUR"), (100, "1.00 EUR"), (123456, "1234.56 EUR")])
def test_format_cents(ex, cents, text):
    assert ex.format_cents(cents) == text


def test_build_reminders(ex, loans):
    reminders = ex.build_reminders(loans, TODAY)
    assert [r.to for r in reminders] == ["ada@example.com", "bob@example.com"]
    ada, bob = reminders
    assert ada == ex.Reminder("ada@example.com", "2 overdue book(s)", ADA_BODY)
    assert bob.subject == "1 overdue book(s)"
    assert bob.body == (
        "Hello Bob,\n\nthese books are overdue:\n- Ulysses: 17 days overdue, fine 4.25 EUR\n\nTotal: 4.25 EUR"
    )


def test_build_reminders_sorts_by_email_not_name(ex):
    loans = [
        loan(ex, "Zoe", "A", D(2026, 1, 1), email="a@example.com"),
        loan(ex, "Adam", "B", D(2026, 1, 1), email="z@example.com"),
    ]
    assert [r.to for r in ex.build_reminders(loans, TODAY)] == ["a@example.com", "z@example.com"]


def test_build_reminders_same_day_sorted_by_title(ex):
    loans = [loan(ex, "Ada", "Zen", D(2026, 1, 1)), loan(ex, "Ada", "Art", D(2026, 1, 1))]
    body = ex.build_reminders(loans, TODAY)[0].body
    assert body.index("- Art") < body.index("- Zen")


def test_build_reminders_grace_days(ex, loans):
    assert [r.to for r in ex.build_reminders(loans, TODAY, grace_days=61)] == []
    assert [r.to for r in ex.build_reminders(loans, TODAY, grace_days=1)] == [
        "ada@example.com", "bob@example.com", "cleo@example.com"]


def test_build_reminders_nothing_overdue(ex):
    assert ex.build_reminders([], TODAY) == []


def test_build_reminders_is_pure(ex, loans):
    before = list(loans)
    first = ex.build_reminders(loans, TODAY)
    assert ex.build_reminders(loans, TODAY) == first
    assert loans == before                           # the input is not changed


# --- adapters ------------------------------------------------------------------

def test_in_memory_loans(ex, loans):
    repo = ex.InMemoryLoans(loans)
    result = repo.open_loans()
    assert result == loans
    result.clear()
    assert repo.open_loans() == loans                # callers cannot change the stored list
    assert ex.InMemoryLoans().open_loans() == []


def test_recording_notifier_and_clocks(ex):
    notifier = ex.RecordingNotifier()
    notifier.send("a@x.com", "hi", "body")
    assert notifier.sent == [("a@x.com", "hi", "body")]
    assert ex.FixedClock(TODAY).today() == TODAY
    assert ex.SystemClock().today() == datetime.date.today()


@pytest.fixture
def conn(ex):
    connection = sqlite3.connect(":memory:")
    connection.executescript(ex.SCHEMA)
    connection.executemany("INSERT INTO members VALUES (?, ?, ?)",
                           [(1, "Ada", "ada@example.com"), (2, "Bob", "bob@example.com")])
    connection.executemany("INSERT INTO books VALUES (?, ?)", [(1, "Mort"), (2, "Dune"), (3, "Emma")])
    connection.executemany(
        "INSERT INTO loans (id, book_id, member_id, loaned_on, returned_on) VALUES (?, ?, ?, ?, ?)",
        [(1, 2, 1, "2026-09-01", None), (2, 3, 2, "2026-09-02", "2026-09-10"), (3, 1, 1, "2026-10-15", None)],
    )
    yield connection
    connection.close()


def test_sqlite_loans(ex, conn):
    assert ex.SqliteLoans(conn).open_loans() == [
        ex.Loan("Ada", "ada@example.com", "Dune", D(2026, 9, 1)),
        ex.Loan("Ada", "ada@example.com", "Mort", D(2026, 10, 15)),
    ]


# --- the service ---------------------------------------------------------------

def test_service_sends_reminders(ex, loans):
    notifier = ex.RecordingNotifier()
    service = ex.ReminderService(ex.InMemoryLoans(loans), notifier, ex.FixedClock(TODAY))
    assert service.run() == 2
    assert notifier.sent[0] == ("ada@example.com", "2 overdue book(s)", ADA_BODY)
    assert [to for to, _, _ in notifier.sent] == ["ada@example.com", "bob@example.com"]


def test_service_uses_the_clock_and_grace_days(ex, loans):
    notifier = ex.RecordingNotifier()
    ex.ReminderService(ex.InMemoryLoans(loans), notifier, ex.FixedClock(D(2026, 10, 1)), grace_days=7).run()
    assert [to for to, _, _ in notifier.sent] == ["ada@example.com"]
    assert "23 days overdue" in notifier.sent[0][2]


def test_service_continues_after_a_failed_send(ex, loans, caplog):
    class FlakyNotifier(ex.RecordingNotifier):
        def send(self, to, subject, body):
            if to.startswith("ada"):
                raise ConnectionError("mailbox full")
            super().send(to, subject, body)

    notifier = FlakyNotifier()
    with caplog.at_level(logging.ERROR):
        sent = ex.ReminderService(ex.InMemoryLoans(loans), notifier, ex.FixedClock(TODAY)).run()
    assert sent == 1
    assert [to for to, _, _ in notifier.sent] == ["bob@example.com"]
    assert any(record.exc_info and "ada@example.com" in record.getMessage() for record in caplog.records)


def test_build_service_wires_the_real_adapters(ex, conn):
    notifier = ex.RecordingNotifier()
    service = ex.build_service(conn, notifier)
    assert isinstance(service.loans, ex.SqliteLoans)
    assert isinstance(service.clock, ex.SystemClock)
    assert service.notifier is notifier
    assert service.run() == 1                        # both of Ada's loans are long overdue by now
    assert notifier.sent[0][1] == "2 overdue book(s)"
