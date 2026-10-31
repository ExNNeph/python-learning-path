"""Assignment 01 · Requirement checker.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest professional/01-project-setup/assignments/01-requirement-checker -v
"""

import operator
import re
from dataclasses import dataclass


def normalize_name(name):
    """PEP 503: lowercase, runs of '-', '_' and '.' become one '-'."""
    raise NotImplementedError


def parse_version(text):
    """'1.10.0' -> (1, 10): a tuple of ints without trailing zeros. ValueError if invalid."""
    raise NotImplementedError


def matches(version, spec):
    """True if `version` satisfies one specifier such as '>=1.4' or '~=1.4.2'."""
    raise NotImplementedError


@dataclass(frozen=True)
class Requirement:
    name: str
    extras: tuple = ()
    specifiers: tuple = ()
    marker: str = None

    def allows(self, version):
        """True if the version satisfies every specifier."""
        raise NotImplementedError


def parse_requirement(line):
    """'name[extras] specs ; marker  # comment' -> Requirement."""
    raise NotImplementedError


def parse_lock(text):
    """'name==version' lines -> {normalised name: version}."""
    raise NotImplementedError


def check(requirements, lock_text):
    """List of problems: requirements that the lock file is missing or does not satisfy."""
    raise NotImplementedError


if __name__ == "__main__":
    print(parse_requirement('HTTPX[http2] >=0.27, <1 ; python_version >= "3.10"'))
    print(check(["httpx>=0.27,<1", "rich", "click>=8.1"], "httpx==0.26.0\nclick==8.1.7\n"))
