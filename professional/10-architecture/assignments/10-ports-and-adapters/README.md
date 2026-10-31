# Assignment 10 · Ports and adapters

> **Lesson:** [10 · Architecture](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

`exercise.py` starts with `legacy_send_overdue_reminders`: a working function that reads overdue loans
from SQLite, calculates fines and emails every member. It cannot be tested without a database file, the
real date and a mail server, and adding SMS would mean rewriting it. Rebuild the same behaviour from
small parts, as in the lesson: a **pure core** that makes every decision, **ports** for the outside
world, **adapters** for SQLite and for tests, and a thin **service** that connects them.

The data classes `Loan` and `Reminder`, the three ports (`LoanRepository`, `Notifier`, `Clock`) and the
`SCHEMA` of the database are given.

## What to write

### The core (pure functions: no I/O, no clock)

| Name | Specification |
|---|---|
| `days_overdue(loan, today, grace_days=14)` | the loan is due `grace_days` after `loaned_on`; returns how many days `today` is past the due date, `0` if it is not overdue |
| `fine_cents(days, per_day=25, cap=1000)` | `days * per_day`, at most `cap` |
| `format_cents(cents)` | `1075` → `"10.75 EUR"`, `5` → `"0.05 EUR"` |
| `build_reminders(loans, today, grace_days=14)` | one `Reminder` per member who has at least one overdue loan, **sorted by email**. Inside a reminder, the overdue loans are listed oldest first (by `loaned_on`, then title). Loans that are not overdue are not mentioned |

A reminder looks like this (`subject` is `"<n> overdue book(s)"`, lines joined with `"\n"`):

```text
to:      ada@example.com
subject: 2 overdue book(s)
body:
Hello Ada,

these books are overdue:
- Dune: 47 days overdue, fine 10.00 EUR
- Mort: 3 days overdue, fine 0.75 EUR

Total: 10.75 EUR
```

### Adapters

| Name | Specification |
|---|---|
| `InMemoryLoans(loans=())` | `open_loans()` returns a **new list** of the given loans |
| `SqliteLoans(conn)` | `open_loans()` returns a `Loan` for every loan in the database with `returned_on IS NULL`, ordered by loan id, with `loaned_on` converted to a `datetime.date` |
| `RecordingNotifier()` | `send(to, subject, body)` appends the tuple `(to, subject, body)` to its list `sent` |
| `FixedClock(day)` / `SystemClock()` | `today()` returns the given day / the real date |

### The service

| Name | Specification |
|---|---|
| `ReminderService(loans, notifier, clock, grace_days=14)` | `run()` builds the reminders from `loans.open_loans()` and `clock.today()`, sends each one with `notifier.send(to, subject, body)`, and returns how many were sent. If sending one reminder raises an exception, log it with `log.exception(...)` and **continue** with the others |
| `build_service(conn, notifier)` | the composition root: a `ReminderService` with `SqliteLoans(conn)`, the given notifier and a `SystemClock` |

## Hints

<details>
<summary>Hint 1: grouping</summary>

Keep only the overdue loans together with their days, sort them by `(email, loaned_on, title)`, then
`itertools.groupby(..., key=email)` gives one group per member, already in email order.
</details>

<details>
<summary>Hint 2: the service stays small</summary>

`run()` should be about six lines: call the core, loop, send, count. If it calculates anything, that
calculation belongs in the core.
</details>

## Check your work

```bash
pytest professional/10-architecture/assignments/10-ports-and-adapters -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/10-architecture/assignments/10-ports-and-adapters/exercise.py),
then tick off assignment 10 in the [progress checklist](../../../../README.md#progress-checklist).
