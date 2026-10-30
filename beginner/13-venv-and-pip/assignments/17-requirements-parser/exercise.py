"""Assignment 17 · Requirements parser.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/13-venv-and-pip/assignments/17-requirements-parser -v
"""

from pathlib import Path

SPECIFIER_START = "=<>!~"


def parse_requirement(line):
    """Return (normalised_name, specifier) for a requirement line, or None for blank/comment lines.

    'Flask_Login == 0.6.3   # auth' -> ('flask-login', '==0.6.3');  'rich' -> ('rich', '')
    """
    raise NotImplementedError


def parse_requirements(text):
    """Return a dict mapping each normalised name to its specifier."""
    raise NotImplementedError


def pinned(requirements):
    """Return a sorted list of the names whose specifier starts with '=='."""
    raise NotImplementedError


def diff_requirements(old_text, new_text):
    """Return {'added': [...], 'removed': [...], 'changed': [...]}, each list sorted."""
    raise NotImplementedError


if __name__ == "__main__":
    # Walk up from this file's folder until we find the repository's requirements.txt.
    for folder in Path(__file__).resolve().parents:
        requirements_file = folder / "requirements.txt"
        if requirements_file.exists():
            text = requirements_file.read_text(encoding="utf-8")
            print(f"{requirements_file}:")
            for name, specifier in parse_requirements(text).items():
                print(f"  {name:<20}{specifier or '(any version)'}")
            break
