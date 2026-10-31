"""Assignment 01 · Requirement checker: template solution."""

import operator
import re
from dataclasses import dataclass

# Two-character operators first: otherwise ">=1" would be read as ">" followed by "=1".
SPEC_RE = re.compile(r"\s*(==|!=|>=|<=|~=|>|<)\s*(\S+)\s*")
REQUIREMENT_RE = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[(.*?)\])?\s*(.*)")

COMPARE = {
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}


def normalize_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def _release(text):
    """All numeric parts, trailing zeros included: '1.4.0' -> [1, 4, 0]."""
    parts = text.strip().split(".")
    if not all(part.isdigit() for part in parts):     # "" (from "..", or empty) is not a digit
        raise ValueError(f"invalid version: {text!r}")
    return [int(part) for part in parts]


def parse_version(text):
    parts = _release(text)
    while parts and parts[-1] == 0:
        parts.pop()
    # Without trailing zeros, equal versions give equal tuples, and tuple comparison
    # (element by element, a prefix is smaller) is exactly version comparison.
    return tuple(parts)


def matches(version, spec):
    found = SPEC_RE.fullmatch(spec)
    if not found:
        raise ValueError(f"invalid specifier: {spec!r}")
    op, wanted = found.groups()
    have = parse_version(version)
    if op != "~=":
        return COMPARE[op](have, parse_version(wanted))
    # ~=1.4.2 means ">=1.4.2" and "the same up to the second-to-last part": ==1.4.*
    prefix = _release(wanted)[:-1]
    if not prefix:
        raise ValueError(f"~= needs at least two version parts: {spec!r}")
    padded = have + (0,) * len(prefix)               # 1 must count as 1.0 when compared with 1.*
    return have >= parse_version(wanted) and padded[: len(prefix)] == tuple(prefix)


@dataclass(frozen=True)
class Requirement:
    name: str
    extras: tuple = ()
    specifiers: tuple = ()
    marker: str = None

    def allows(self, version):
        return all(matches(version, spec) for spec in self.specifiers)


def parse_requirement(line):
    line = line.split("#", 1)[0]
    rest, has_marker, marker = line.partition(";")
    found = REQUIREMENT_RE.fullmatch(rest.strip())
    if not found:
        raise ValueError(f"invalid requirement: {line.strip()!r}")
    name, extras, spec_text = found.groups()
    specifiers = []
    for spec in filter(None, (part.strip() for part in spec_text.split(","))):
        matches("0", spec)                           # raises ValueError for a bad specifier
        specifiers.append(spec.replace(" ", ""))
    return Requirement(
        name=normalize_name(name),
        extras=tuple(sorted(normalize_name(e.strip()) for e in (extras or "").split(",") if e.strip())),
        specifiers=tuple(specifiers),
        marker=marker.strip() if has_marker else None,
    )


def parse_lock(text):
    locked = {}
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        name, sep, version = line.partition("==")
        try:
            parse_version(version)
        except ValueError:
            sep = ""
        if not sep or not name.strip():
            raise ValueError(f"line {number}: expected name==version")
        locked[normalize_name(name.strip())] = version.strip()
    return locked


def _is_requirement(line):
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("#")


def check(requirements, lock_text):
    locked = parse_lock(lock_text)
    problems = []
    for requirement in map(parse_requirement, filter(_is_requirement, requirements)):
        version = locked.get(requirement.name)
        if version is None:
            problems.append(f"{requirement.name}: missing from the lock file")
        elif not requirement.allows(version):
            wanted = ",".join(requirement.specifiers)
            problems.append(f"{requirement.name}: locked {version} does not satisfy {wanted}")
    return problems


if __name__ == "__main__":
    print(parse_requirement('HTTPX[http2] >=0.27, <1 ; python_version >= "3.10"'))
    print(check(["httpx>=0.27,<1", "rich", "click>=8.1"], "httpx==0.26.0\nclick==8.1.7\n"))
