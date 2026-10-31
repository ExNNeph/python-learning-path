"""Assignment 12 · Release notes.

Replace each `raise NotImplementedError` with your code. Commit is given.
Check your work:  pytest professional/12-git-ci-and-releases/assignments/12-release-notes -v
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Commit:
    type: str
    scope: str | None
    description: str
    breaking: bool = False
    breaking_note: str | None = None


def parse_commit(message):
    """A Commit for a Conventional Commit message, None for any other message."""
    raise NotImplementedError


def parse_version(text):
    """'1.4.2' -> (1, 4, 2); ValueError for anything else."""
    raise NotImplementedError


def bump_kind(commits):
    """'major', 'minor', 'patch' or None: the biggest change wins."""
    raise NotImplementedError


def next_version(current, commits):
    """The next semantic version after `current` for these commits (unchanged if no release)."""
    raise NotImplementedError


def render_changelog(version, date, commits):
    """The Markdown changelog section for this release."""
    raise NotImplementedError


def release(current, messages, date):
    """(new version, changelog) for raw commit messages, or (current, None) if nothing to release."""
    raise NotImplementedError


if __name__ == "__main__":
    messages = [
        "feat(cli): add --json output",
        "fix: handle empty files",
        "docs: explain the retry settings",
        "Merge branch 'main' into feature",
        "feat(api)!: remove the v1 endpoints",
        "refactor: split the client\n\nBREAKING CHANGE: ApiClient now needs a transport",
    ]
    version, notes = release("1.2.0", messages, "2026-11-01")
    print(version)
    print(notes)
