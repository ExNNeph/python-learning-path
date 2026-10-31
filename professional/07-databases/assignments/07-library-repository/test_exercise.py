"""Tests for assignment 07. Run: pytest professional/07-databases/assignments/07-library-repository -v"""

import sqlite3

import pytest


@pytest.fixture
def conn(ex):
    connection = ex.connect()
    yield connection
    connection.close()


@pytest.fixture
def empty():
    """A bare database without migrations."""
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def repo(ex, conn):
    return ex.LibraryRepository(conn)


@pytest.fixture
def library(repo):
    """A small library: three books, two members."""
    ids = {
        "earthsea": repo.add_book("A Wizard of Earthsea", "Ursula K. Le Guin", 1968),
        "mort": repo.add_book("Mort", "Terry Pratchett", 1987),
        "dune": repo.add_book("Dune", "Frank Herbert", 1965),
        "ada": repo.add_member("Ada", "ada@example.com"),
        "bob": repo.add_member("Bob", "bob@example.com"),
    }
    return repo, ids


def titles(books):
    return [book["title"] for book in books]


def tables(conn):
    return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


# --- migrations and connect ----------------------------------------------------

def test_connect(ex, conn):
    assert conn.row_factory is sqlite3.Row
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
    assert {"books", "members", "loans"} <= tables(conn)


def test_migrate_counts_and_is_repeatable(ex, empty):
    conn = empty
    assert ex.migrate(conn) == 3
    assert ex.migrate(conn) == 0
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 3


def test_migrate_only_new_ones(ex, empty):
    conn = empty
    assert ex.migrate(conn, ex.MIGRATIONS[:1]) == 1
    assert tables(conn) == {"books"}
    assert ex.migrate(conn) == 2
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 3


def test_migration_is_atomic(ex, empty):
    conn = empty
    broken = ex.MIGRATIONS[:1] + [["CREATE TABLE extra (x INTEGER)", "CREATE TABLE oops ("]]
    with pytest.raises(sqlite3.Error):
        ex.migrate(conn, broken)
    assert tables(conn) == {"books"}                     # migration 2 left no trace
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
    assert ex.migrate(conn) == 2                         # and the fixed list still applies cleanly


def test_file_database_persists(ex, tmp_path):
    path = tmp_path / "library.db"
    first = ex.connect(str(path))
    book = ex.LibraryRepository(first).add_book("Mort", "Terry Pratchett")
    first.close()
    second = ex.connect(str(path))
    assert ex.LibraryRepository(second).get_book(book)["title"] == "Mort"
    assert ex.migrate(second) == 0
    second.close()


# --- books and members ---------------------------------------------------------

def test_add_and_get_book(repo):
    first = repo.add_book("Mort", "Terry Pratchett", 1987)
    second = repo.add_book("Untitled", "Anonymous")
    assert second != first
    assert repo.get_book(first) == {"id": first, "title": "Mort", "author": "Terry Pratchett", "year": 1987}
    assert repo.get_book(second)["year"] is None
    assert repo.get_book(999) is None


def test_add_book_commits(ex, tmp_path):
    path = str(tmp_path / "x.db")
    first = ex.connect(path)
    ex.LibraryRepository(first).add_book("Mort", "Terry Pratchett")
    other = sqlite3.connect(path)                        # a second connection sees only committed data
    assert other.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1
    other.close()
    first.close()


def test_duplicate_email(ex, repo):
    repo.add_member("Ada", "ada@example.com")
    with pytest.raises(ex.DuplicateEmail) as info:
        repo.add_member("Ada Again", "ada@example.com")
    assert isinstance(info.value, ex.LibraryError)
    assert isinstance(info.value.__cause__, sqlite3.IntegrityError)
    assert repo.add_member("Bob", "bob@example.com") > 0          # the connection still works


# --- search --------------------------------------------------------------------

def test_search_title_and_author_case_insensitive(library):
    repo, _ = library
    assert titles(repo.search_books("le guin")) == ["A Wizard of Earthsea"]
    assert titles(repo.search_books("MORT")) == ["Mort"]
    assert titles(repo.search_books("e")) == ["A Wizard of Earthsea", "Dune", "Mort"]
    assert repo.search_books("tolkien") == []


def test_search_is_injection_safe(library):
    repo, _ = library
    assert repo.search_books("' OR '1'='1") == []
    assert repo.search_books("x'); DROP TABLE books; --") == []
    assert len(repo.search_books("")) == 3                         # the table still exists


def test_search_wildcards_are_literal(repo):
    repo.add_book("100% Python", "A. Author")
    repo.add_book("snake_case for all", "B. Author")
    repo.add_book("Backslash \\ Tales", "C. Author")
    repo.add_book("Plain", "D. Author")
    assert titles(repo.search_books("%")) == ["100% Python"]
    assert titles(repo.search_books("_")) == ["snake_case for all"]
    assert titles(repo.search_books("\\")) == ["Backslash \\ Tales"]


# --- lending -------------------------------------------------------------------

def test_lend_and_return(library):
    repo, ids = library
    loan = repo.lend(ids["mort"], ids["ada"], "2026-11-01")
    assert isinstance(loan, int)
    assert titles(repo.available_books()) == ["A Wizard of Earthsea", "Dune"]
    repo.return_book(ids["mort"], "2026-11-05")
    assert titles(repo.available_books()) == ["A Wizard of Earthsea", "Dune", "Mort"]
    row = repo.conn.execute("SELECT loaned_on, returned_on FROM loans WHERE id = ?", (loan,)).fetchone()
    assert tuple(row) == ("2026-11-01", "2026-11-05")


def test_lend_twice_not_available(ex, library):
    repo, ids = library
    repo.lend(ids["mort"], ids["ada"], "2026-11-01")
    with pytest.raises(ex.NotAvailable):
        repo.lend(ids["mort"], ids["bob"], "2026-11-02")
    repo.return_book(ids["mort"], "2026-11-03")
    assert repo.lend(ids["mort"], ids["bob"], "2026-11-04")       # free again


def test_lend_unknown_book_or_member(ex, library):
    repo, ids = library
    with pytest.raises(ex.NotFound):
        repo.lend(999, ids["ada"], "2026-11-01")
    with pytest.raises(ex.NotFound):
        repo.lend(ids["mort"], 999, "2026-11-01")
    assert repo.conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0] == 0


def test_return_without_open_loan(ex, library):
    repo, ids = library
    with pytest.raises(ex.NotFound, match=f"no open loan for book {ids['dune']}"):
        repo.return_book(ids["dune"], "2026-11-01")


def test_lend_many(library):
    repo, ids = library
    loans = repo.lend_many(ids["ada"], [ids["dune"], ids["mort"]], "2026-11-01")
    assert len(loans) == 2 and loans[0] < loans[1]
    assert titles(repo.available_books()) == ["A Wizard of Earthsea"]


def test_lend_many_is_all_or_nothing(ex, library):
    repo, ids = library
    repo.lend(ids["earthsea"], ids["bob"], "2026-11-01")
    with pytest.raises(ex.NotAvailable):
        repo.lend_many(ids["ada"], [ids["dune"], ids["mort"], ids["earthsea"]], "2026-11-02")
    assert titles(repo.available_books()) == ["Dune", "Mort"]      # dune and mort were rolled back
    with pytest.raises(ex.NotFound):
        repo.lend_many(ids["ada"], [ids["dune"], 999], "2026-11-02")
    assert titles(repo.available_books()) == ["Dune", "Mort"]
    assert repo.conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0] == 1


def test_lend_many_same_book_twice(ex, library):
    repo, ids = library
    with pytest.raises(ex.NotAvailable):
        repo.lend_many(ids["ada"], [ids["dune"], ids["dune"]], "2026-11-01")
    assert len(repo.available_books()) == 3


# --- questions -----------------------------------------------------------------

def test_available_books_empty_library(repo):
    assert repo.available_books() == []


def test_top_borrowers(ex, library):
    repo, ids = library
    cleo = repo.add_member("Cleo", "cleo@example.com")
    repo.add_member("Dan", "dan@example.com")                    # never borrows
    repo.lend(ids["mort"], ids["bob"], "2026-11-01")
    repo.return_book(ids["mort"], "2026-11-02")
    repo.lend(ids["mort"], ids["bob"], "2026-11-03")             # returned and open loans both count
    repo.lend(ids["dune"], ids["ada"], "2026-11-01")
    repo.lend(ids["earthsea"], cleo, "2026-11-01")
    assert repo.top_borrowers() == [("Bob", 2), ("Ada", 1), ("Cleo", 1)]
    assert repo.top_borrowers(limit=2) == [("Bob", 2), ("Ada", 1)]


def test_top_borrowers_none(library):
    repo, _ = library
    assert repo.top_borrowers() == []


def test_results_are_plain_data(library):
    repo, ids = library
    assert type(repo.get_book(ids["mort"])) is dict
    assert all(type(book) is dict for book in repo.search_books(""))
    repo.lend(ids["mort"], ids["ada"], "2026-11-01")
    assert all(type(entry) is tuple for entry in repo.top_borrowers())
