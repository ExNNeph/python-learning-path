"""Tests for assignment 12. Run: pytest professional/12-git-ci-and-releases/assignments/12-release-notes -v"""

import pytest

MESSAGES = [
    "feat(cli): add --json output",
    "fix: handle empty files",
    "docs: explain the retry settings",
    "Merge branch 'main' into feature",
    "feat(api)!: remove the v1 endpoints",
    "refactor: split the client\n\nBREAKING CHANGE: ApiClient now needs a transport",
]

EXPECTED_NOTES = """## 2.0.0 (2026-11-01)

### ⚠ Breaking changes
- **api:** remove the v1 endpoints
- ApiClient now needs a transport

### Features
- **cli:** add --json output
- **api:** remove the v1 endpoints

### Bug fixes
- handle empty files
"""


def commits(ex, *messages):
    return [ex.parse_commit(m) for m in messages]


# --- parse_commit --------------------------------------------------------------

def test_parse_simple(ex):
    assert ex.parse_commit("fix: handle empty files") == ex.Commit("fix", None, "handle empty files")


def test_parse_scope_and_bang(ex):
    assert ex.parse_commit("feat(api)!: remove the v1 endpoints") == ex.Commit(
        "feat", "api", "remove the v1 endpoints", breaking=True)
    assert ex.parse_commit("perf(db-layer): add index") == ex.Commit("perf", "db-layer", "add index")


def test_parse_breaking_footer(ex):
    message = "refactor: split the client\n\nThe client was too big.\n\nBREAKING CHANGE: ApiClient now needs a transport\nRefs #12"
    assert ex.parse_commit(message) == ex.Commit(
        "refactor", None, "split the client", breaking=True, breaking_note="ApiClient now needs a transport")
    assert ex.parse_commit("fix: x\n\nBREAKING-CHANGE: y").breaking_note == "y"


def test_footer_must_start_a_line(ex):
    commit = ex.parse_commit("fix: x\n\nThis is not a BREAKING CHANGE: really")
    assert commit.breaking is False and commit.breaking_note is None


def test_parse_ignores_surrounding_whitespace_and_keeps_description(ex):
    assert ex.parse_commit("\n  docs: fix typo in README  \n") == ex.Commit("docs", None, "fix typo in README")
    assert ex.parse_commit("feat: support: colons in text").description == "support: colons in text"


@pytest.mark.parametrize("message", [
    "Merge branch 'main' into feature",
    "Fix bug",
    "feat:no space",
    "feat:  two spaces",
    "Feat: capital type",
    "feat(): empty scope",
    "feat(a b): space in scope",
    "feat(api)!!: two bangs",
    "feat: ",
    "",
    "body only\n\nfeat: not the first line",
])
def test_not_conventional(ex, message):
    assert ex.parse_commit(message) is None


# --- versions ------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [("1.4.2", (1, 4, 2)), ("0.0.0", (0, 0, 0)), (" 10.20.30 ", (10, 20, 30))])
def test_parse_version(ex, text, expected):
    assert ex.parse_version(text) == expected


@pytest.mark.parametrize("text", ["v1.4.2", "1.4", "1.4.2.0", "01.2.3", "1.02.3", "1.2.x", ""])
def test_parse_version_rejects(ex, text):
    with pytest.raises(ValueError):
        ex.parse_version(text)


@pytest.mark.parametrize("messages, expected", [
    (["docs: a", "chore: b"], None),
    (["fix: a", "docs: b"], "patch"),
    (["perf: a"], "patch"),
    (["fix: a", "feat: b"], "minor"),
    (["feat: a", "docs!: drop old docs"], "major"),
    (["chore: a\n\nBREAKING CHANGE: python 3.9 dropped"], "major"),
    ([], None),
])
def test_bump_kind(ex, messages, expected):
    assert ex.bump_kind(commits(ex, *messages)) == expected


@pytest.mark.parametrize("current, messages, expected", [
    ("1.2.3", ["fix: a"], "1.2.4"),
    ("1.2.3", ["feat: a", "fix: b"], "1.3.0"),
    ("1.2.3", ["feat!: a"], "2.0.0"),
    ("1.2.3", ["docs: a"], "1.2.3"),
    ("0.4.1", ["feat!: a"], "0.5.0"),
    ("0.4.1", ["feat: a"], "0.5.0"),
    ("0.4.1", ["fix: a"], "0.4.2"),
    ("1.9.9", ["feat: a"], "1.10.0"),
])
def test_next_version(ex, current, messages, expected):
    assert ex.next_version(current, commits(ex, *messages)) == expected


def test_next_version_validates(ex):
    with pytest.raises(ValueError):
        ex.next_version("v1.0.0", commits(ex, "fix: a"))


# --- changelog -----------------------------------------------------------------

def test_render_full(ex):
    parsed = [c for c in commits(ex, *MESSAGES) if c]
    assert ex.render_changelog("2.0.0", "2026-11-01", parsed) == EXPECTED_NOTES


def test_render_leaves_out_empty_sections_and_other_types(ex):
    parsed = commits(ex, "perf(db): add index on loans.book_id", "docs: update README", "test: more cases")
    assert ex.render_changelog("1.2.4", "2026-11-02", parsed) == (
        "## 1.2.4 (2026-11-02)\n\n### Performance\n- **db:** add index on loans.book_id\n"
    )


def test_render_section_order(ex):
    parsed = commits(ex, "perf: p", "fix: f", "feat: a")
    text = ex.render_changelog("1.1.0", "2026-11-01", parsed)
    assert text.index("### Features") < text.index("### Bug fixes") < text.index("### Performance")


# --- release -------------------------------------------------------------------

def test_release(ex):
    assert ex.release("1.2.0", MESSAGES, "2026-11-01") == ("2.0.0", EXPECTED_NOTES)


def test_release_nothing_to_release(ex):
    assert ex.release("1.2.0", ["docs: a", "Merge branch 'x'", "ci: faster"], "2026-11-01") == ("1.2.0", None)
    assert ex.release("1.2.0", [], "2026-11-01") == ("1.2.0", None)


def test_release_patch(ex):
    version, notes = ex.release("0.3.9", ["fix(io): close files", "chore: deps"], "2026-12-24")
    assert version == "0.3.10"
    assert notes == "## 0.3.10 (2026-12-24)\n\n### Bug fixes\n- **io:** close files\n"
