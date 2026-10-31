"""Assignment 07 · Library repository.

Replace each `raise NotImplementedError` with your code. MIGRATIONS and the exceptions are given.
Check your work:  pytest professional/07-databases/assignments/07-library-repository -v
"""

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
    """Apply the migrations above PRAGMA user_version, each in its own transaction. Return how many ran."""
    raise NotImplementedError


def connect(path=":memory:"):
    """A connection with sqlite3.Row rows, foreign keys on, and all migrations applied."""
    raise NotImplementedError


class LibraryRepository:
    def __init__(self, conn):
        self.conn = conn

    def add_book(self, title, author, year=None):
        raise NotImplementedError

    def get_book(self, book_id):
        raise NotImplementedError

    def add_member(self, name, email):
        raise NotImplementedError

    def search_books(self, text):
        raise NotImplementedError

    def lend(self, book_id, member_id, day):
        raise NotImplementedError

    def lend_many(self, member_id, book_ids, day):
        raise NotImplementedError

    def return_book(self, book_id, day):
        raise NotImplementedError

    def available_books(self):
        raise NotImplementedError

    def top_borrowers(self, limit=3):
        raise NotImplementedError


if __name__ == "__main__":
    repo = LibraryRepository(connect())
    earthsea = repo.add_book("A Wizard of Earthsea", "Ursula K. Le Guin", 1968)
    mort = repo.add_book("Mort", "Terry Pratchett", 1987)
    ada = repo.add_member("Ada", "ada@example.com")
    repo.lend(earthsea, ada, "2026-11-01")
    print(repo.search_books("le guin"))
    print(repo.available_books())
    print(repo.top_borrowers())
