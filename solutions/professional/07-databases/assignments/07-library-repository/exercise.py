"""Assignment 07 · Library repository: template solution."""

import sqlite3

MIGRATIONS = [
    # 1
    [
        """CREATE TABLE books (
            id     INTEGER PRIMARY KEY,
            title  TEXT NOT NULL,
            author TEXT NOT NULL,
            year   INTEGER
        )""",
    ],
    # 2
    [
        """CREATE TABLE members (
            id    INTEGER PRIMARY KEY,
            name  TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )""",
    ],
    # 3
    [
        """CREATE TABLE loans (
            id          INTEGER PRIMARY KEY,
            book_id     INTEGER NOT NULL REFERENCES books(id),
            member_id   INTEGER NOT NULL REFERENCES members(id),
            loaned_on   TEXT NOT NULL,
            returned_on TEXT
        )""",
        "CREATE INDEX loans_book ON loans(book_id)",
    ],
]


class LibraryError(Exception):
    pass


class NotFound(LibraryError):
    pass


class NotAvailable(LibraryError):
    pass


class DuplicateEmail(LibraryError):
    pass


def migrate(conn, migrations=MIGRATIONS):
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    applied = 0
    for version, statements in enumerate(migrations, start=1):
        if version <= current:
            continue
        # DDL does not start a transaction implicitly in sqlite3: open one ourselves,
        # so a migration and its version number are saved together or not at all.
        conn.execute("BEGIN")
        try:
            for statement in statements:
                conn.execute(statement)
            conn.execute(f"PRAGMA user_version = {version}")   # an int from our own code, not user input
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        applied += 1
    return applied


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn


def _like_pattern(text):
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class LibraryRepository:
    def __init__(self, conn):
        self.conn = conn

    # --- books and members -----------------------------------------------------

    def add_book(self, title, author, year=None):
        with self.conn:
            return self.conn.execute(
                "INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year)
            ).lastrowid

    def get_book(self, book_id):
        row = self.conn.execute(
            "SELECT id, title, author, year FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        return dict(row) if row else None

    def add_member(self, name, email):
        try:
            with self.conn:
                return self.conn.execute(
                    "INSERT INTO members (name, email) VALUES (?, ?)", (name, email)
                ).lastrowid
        except sqlite3.IntegrityError as error:
            raise DuplicateEmail(f"email already registered: {email}") from error

    def search_books(self, text):
        rows = self.conn.execute(
            """SELECT id, title, author, year FROM books
               WHERE title LIKE :pattern ESCAPE '\\' OR author LIKE :pattern ESCAPE '\\'
               ORDER BY title""",
            {"pattern": _like_pattern(text)},
        )
        return [dict(row) for row in rows]

    # --- loans -----------------------------------------------------------------

    def _check_exists(self, table, row_id):
        # `table` comes from our own code ("books" / "members"), never from input.
        if self.conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (row_id,)).fetchone() is None:
            raise NotFound(f"{table[:-1]} {row_id} not found")

    def _lend(self, book_id, member_id, day):
        self._check_exists("books", book_id)
        open_loan = self.conn.execute(
            "SELECT 1 FROM loans WHERE book_id = ? AND returned_on IS NULL", (book_id,)
        ).fetchone()
        if open_loan:
            raise NotAvailable(f"book {book_id} is already lent")
        return self.conn.execute(
            "INSERT INTO loans (book_id, member_id, loaned_on) VALUES (?, ?, ?)",
            (book_id, member_id, day),
        ).lastrowid

    def lend(self, book_id, member_id, day):
        return self.lend_many(member_id, [book_id], day)[0]

    def lend_many(self, member_id, book_ids, day):
        self._check_exists("members", member_id)
        with self.conn:                          # all loans, or (after any error) none
            return [self._lend(book_id, member_id, day) for book_id in book_ids]

    def return_book(self, book_id, day):
        with self.conn:
            changed = self.conn.execute(
                "UPDATE loans SET returned_on = ? WHERE book_id = ? AND returned_on IS NULL",
                (day, book_id),
            ).rowcount
        if changed == 0:
            raise NotFound(f"no open loan for book {book_id}")

    # --- questions -------------------------------------------------------------

    def available_books(self):
        rows = self.conn.execute(
            """SELECT books.id, books.title, books.author, books.year
               FROM books
               LEFT JOIN loans ON loans.book_id = books.id AND loans.returned_on IS NULL
               WHERE loans.id IS NULL
               ORDER BY books.title"""
        )
        return [dict(row) for row in rows]

    def top_borrowers(self, limit=3):
        rows = self.conn.execute(
            """SELECT members.name, COUNT(loans.id) AS loans
               FROM members
               JOIN loans ON loans.member_id = members.id
               GROUP BY members.id
               ORDER BY loans DESC, members.name
               LIMIT ?""",
            (limit,),
        )
        return [tuple(row) for row in rows]


if __name__ == "__main__":
    repo = LibraryRepository(connect())
    earthsea = repo.add_book("A Wizard of Earthsea", "Ursula K. Le Guin", 1968)
    mort = repo.add_book("Mort", "Terry Pratchett", 1987)
    ada = repo.add_member("Ada", "ada@example.com")
    repo.lend(earthsea, ada, "2026-11-01")
    print(repo.search_books("le guin"))
    print(repo.available_books())
    print(repo.top_borrowers())
