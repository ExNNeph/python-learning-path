"""Assignment 12 · Release notes: template solution."""

import re
from dataclasses import dataclass

HEADER_RE = re.compile(r"(?P<type>[a-z]+)(?:\((?P<scope>[^()\s]+)\))?(?P<bang>!)?: (?P<description>\S.*)")
BREAKING_FOOTER_RE = re.compile(r"^BREAKING[ -]CHANGE: (.+)$", re.MULTILINE)
VERSION_RE = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")

SECTIONS = [("feat", "Features"), ("fix", "Bug fixes"), ("perf", "Performance")]


@dataclass(frozen=True)
class Commit:
    type: str
    scope: str | None
    description: str
    breaking: bool = False
    breaking_note: str | None = None


def parse_commit(message):
    header, _, rest = message.strip().partition("\n")
    match = HEADER_RE.fullmatch(header.strip())
    if match is None:
        return None                                    # not a Conventional Commit: ignored
    footer = BREAKING_FOOTER_RE.search(rest)
    return Commit(
        type=match["type"],
        scope=match["scope"],
        description=match["description"].strip(),
        breaking=bool(match["bang"] or footer),
        breaking_note=footer.group(1).strip() if footer else None,
    )


def parse_version(text):
    match = VERSION_RE.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"invalid version: {text!r}")
    return tuple(int(part) for part in match.groups())


def bump_kind(commits):
    """'major', 'minor', 'patch' or None: the biggest change wins."""
    if any(c.breaking for c in commits):
        return "major"
    if any(c.type == "feat" for c in commits):
        return "minor"
    if any(c.type in ("fix", "perf") for c in commits):
        return "patch"
    return None


def next_version(current, commits):
    major, minor, patch = parse_version(current)
    kind = bump_kind(commits)
    if kind == "major" and major == 0:
        kind = "minor"                                 # 0.x: the API is not stable yet
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return current


def _entry(commit, text):
    return f"- **{commit.scope}:** {text}" if commit.scope else f"- {text}"


def render_changelog(version, date, commits):
    blocks = [f"## {version} ({date})"]
    breaking = [_entry(c, c.breaking_note or c.description) for c in commits if c.breaking]
    if breaking:
        blocks.append("### ⚠ Breaking changes\n" + "\n".join(breaking))
    for commit_type, title in SECTIONS:
        entries = [_entry(c, c.description) for c in commits if c.type == commit_type]
        if entries:
            blocks.append(f"### {title}\n" + "\n".join(entries))
    return "\n\n".join(blocks) + "\n"


def release(current, messages, date):
    commits = [c for c in map(parse_commit, messages) if c is not None]
    version = next_version(current, commits)
    if version == current:
        return current, None                           # nothing worth releasing
    return version, render_changelog(version, date, commits)


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
