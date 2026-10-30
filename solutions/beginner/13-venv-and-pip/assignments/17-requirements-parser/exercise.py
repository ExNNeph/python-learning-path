"""Assignment 17 · Requirements parser: template solution."""

from pathlib import Path

SPECIFIER_START = "=<>!~"


def parse_requirement(line):
    """Return (normalised_name, specifier) for a requirement line, or None for blank/comment lines."""
    # Remove the comment first, then the whitespace: "  # note" and "" both end up empty.
    content = line.split("#")[0].strip()
    if not content:
        return None

    # Find where the name ends: the first character that can start a specifier.
    # Default: the whole line is the name (a requirement without a version).
    split_at = len(content)
    for index, char in enumerate(content):
        if char in SPECIFIER_START:
            split_at = index
            break

    name = content[:split_at].strip().lower().replace("_", "-")
    specifier = content[split_at:].replace(" ", "")
    return name, specifier


def parse_requirements(text):
    """Return a dict mapping each normalised name to its specifier."""
    requirements = {}
    for line in text.splitlines():   # like split("\n"), but also handles Windows "\r\n"
        parsed = parse_requirement(line)
        if parsed is not None:
            name, specifier = parsed
            requirements[name] = specifier   # a repeated name: the later line wins
    return requirements


def pinned(requirements):
    """Return a sorted list of the names whose specifier starts with '=='."""
    return sorted(name for name, specifier in requirements.items() if specifier.startswith("=="))


def diff_requirements(old_text, new_text):
    """Return {'added': [...], 'removed': [...], 'changed': [...]}, each list sorted."""
    old = parse_requirements(old_text)
    new = parse_requirements(new_text)
    # dict.keys() behaves like a set, so -, & and | work on it directly.
    added = new.keys() - old.keys()
    removed = old.keys() - new.keys()
    changed = {name for name in old.keys() & new.keys() if old[name] != new[name]}
    # Sets have no order; sorting makes the result stable and easy to compare in tests.
    return {"added": sorted(added), "removed": sorted(removed), "changed": sorted(changed)}


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
