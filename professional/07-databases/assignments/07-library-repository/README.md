# Assignment 07 · Library repository

> **Lesson:** [07 · Databases](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~3 h

## Goal

Write the database layer of a small library: versioned schema migrations, and a repository class that
owns all the SQL. It must be safe against SQL injection, lend books in all-or-nothing transactions,
answer questions with joins and aggregates, and turn database errors into the library's own exceptions.

## Given

- `MIGRATIONS`: a list of migrations; each is a list of SQL statements. Migration 1 creates `books`,
  2 creates `members` (with a `UNIQUE` email), 3 creates `loans` and an index. A loan is **open** while
  its `returned_on` is `NULL`. Days are ISO strings like `"2026-11-01"`.
- `LibraryError` and its subclasses `NotFound`, `NotAvailable` and `DuplicateEmail`.

## What to write

| Name | Specification |
|---|---|
| `migrate(conn, migrations=MIGRATIONS)` | reads `PRAGMA user_version` and applies every migration with a higher number (migration *n* is `migrations[n - 1]`), in order. Each migration runs in **its own transaction** together with setting `user_version` to its number: if a statement fails, that migration leaves no trace (no table, no version change) and the error propagates. Returns the number of migrations applied (`0` when the database is up to date) |
| `connect(path=":memory:")` | opens the database, sets `row_factory = sqlite3.Row`, turns on foreign keys, migrates, returns the connection |
| `LibraryRepository(conn)` | stores the connection as `self.conn` (given). Every method uses `?` or `:name` placeholders for values |

### Repository methods

| Method | Specification |
|---|---|
| `add_book(title, author, year=None)` | inserts and commits; returns the new id |
| `get_book(book_id)` | `{"id", "title", "author", "year"}` as a dict, or `None` |
| `add_member(name, email)` | returns the new id. An email that is already registered raises `DuplicateEmail` **chained** to the `sqlite3.IntegrityError` |
| `search_books(text)` | books whose title **or** author contains `text`, case-insensitively, as dicts ordered by title. `%`, `_` and `\` in `text` match **literally** |
| `lend(book_id, member_id, day)` | creates an open loan and returns its id. `NotFound` for an unknown book or member, `NotAvailable` if the book has an open loan |
| `lend_many(member_id, book_ids, day)` | lends all books in **one transaction** and returns the loan ids in order. If any book is unknown or not available, the exception propagates and **no** loan is created |
| `return_book(book_id, day)` | sets `returned_on` of the book's open loan. No open loan: `NotFound("no open loan for book <id>")` |
| `available_books()` | books without an open loan, as dicts ordered by title |
| `top_borrowers(limit=3)` | `[(name, number of loans), ...]` over **all** loans (open and returned), most loans first, ties by name, at most `limit` entries; members without loans are left out |

## Examples

```python
>>> repo = LibraryRepository(connect())
>>> earthsea = repo.add_book("A Wizard of Earthsea", "Ursula K. Le Guin", 1968)
>>> mort = repo.add_book("Mort", "Terry Pratchett", 1987)
>>> ada = repo.add_member("Ada", "ada@example.com")
>>> repo.lend(earthsea, ada, "2026-11-01")
1
>>> repo.search_books("le guin")
[{'id': 1, 'title': 'A Wizard of Earthsea', 'author': 'Ursula K. Le Guin', 'year': 1968}]
>>> repo.available_books()
[{'id': 2, 'title': 'Mort', 'author': 'Terry Pratchett', 'year': 1987}]
>>> repo.lend_many(ada, [mort, earthsea], "2026-11-02")
Traceback (most recent call last):
NotAvailable: book 1 is already lent
>>> repo.available_books()                    # Mort was not lent either
[{'id': 2, 'title': 'Mort', 'author': 'Terry Pratchett', 'year': 1987}]
>>> repo.top_borrowers()
[('Ada', 1)]
```

## Hints

<details>
<summary>Hint 1: migrations</summary>

`sqlite3` does not start a transaction before `CREATE TABLE` by itself. Run `conn.execute("BEGIN")`, the
statements, and `conn.execute(f"PRAGMA user_version = {version}")` (a pragma cannot take a placeholder;
the number comes from your own loop, so that is safe), then `conn.commit()`. In `except BaseException:`
call `conn.rollback()` and re-raise.
</details>

<details>
<summary>Hint 2: search</summary>

SQLite's `LIKE` is case-insensitive for ASCII letters. Build the pattern in Python: escape `\` first, then
`%` and `_`, wrap it in `%...%`, and write `LIKE ? ESCAPE '\'` in the SQL. With a named parameter
(`:pattern`) you can use the same value for both columns.
</details>

<details>
<summary>Hint 3: lending</summary>

Let `lend` call `lend_many` with one book. In `lend_many`, check the member, then do all the work inside
one `with self.conn:` block: for each book, check that it exists, check for an open loan
(`WHERE book_id = ? AND returned_on IS NULL`), insert. An exception inside the block rolls everything back.
For `available_books`, `LEFT JOIN loans ON loans.book_id = books.id AND loans.returned_on IS NULL` and keep
the rows where `loans.id IS NULL`.
</details>

## Check your work

```bash
pytest professional/07-databases/assignments/07-library-repository -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/07-databases/assignments/07-library-repository/exercise.py),
then tick off assignment 07 in the [progress checklist](../../../../README.md#progress-checklist).
