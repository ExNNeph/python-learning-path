# Assignment 01 · Requirement checker

> **Lesson:** [01 · Project setup](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Build the core of what `pip` and `uv` do before they install anything: normalise package names, compare
versions, evaluate specifiers, parse requirement lines, and check that a lock file satisfies the
declared dependencies.

To keep it focused, versions here are **release numbers only**: digits separated by dots (`1`, `1.4`,
`2.10.3`). Pre-releases like `2.0rc1` are out of scope.

## What to write

| Name | Specification |
|---|---|
| `normalize_name(name)` | PEP 503: lowercase, and every run of `-`, `_` and `.` becomes a single `-` |
| `parse_version(text)` | a tuple of ints with **trailing zeros removed**, so equal versions give equal tuples: `"1.10.0"` → `(1, 10)`, `"0"` → `()`. Surrounding whitespace is allowed. Anything else (empty, letters, `1..2`, `-1`) raises `ValueError("invalid version: '<text>'")` |
| `matches(version, spec)` | `True` if the version string satisfies one specifier string such as `">=1.4"`, `"== 2.0"`, `"~=1.4.2"`. Operators: `==`, `!=`, `>=`, `<=`, `>`, `<`, `~=`. `~=X.Y` means `>=X.Y` **and** the same version up to the second-to-last part of the spec (`~=1.4.2` allows `1.4.9`, not `1.5`). `~=` with a one-part version, or an unknown operator, raises `ValueError` |
| `Requirement` | a **frozen** dataclass: `name` (normalised), `extras` (sorted tuple of normalised names), `specifiers` (tuple of strings without spaces, in the given order), `marker` (the text after `;`, stripped, or `None`). Method `allows(version)`: `True` if **all** specifiers match (no specifiers: always `True`) |
| `parse_requirement(line)` | parses `name[extra1,extra2] spec1,spec2 ; marker` into a `Requirement`. Everything except the name is optional; a `#` starts a comment. A line without a valid name, or a specifier that is not an operator followed by a valid version, raises `ValueError` |
| `parse_lock(text)` | parses a lock file in the `name==version` format into `{normalised name: version}`. Blank lines and `#` comments are skipped. Any other line raises `ValueError("line N: expected name==version")` (N counts from 1) |
| `check(requirements, lock_text)` | `requirements` is a list of requirement lines (blank and comment lines are skipped). Returns a list of problems, one per failing requirement, in input order: `"<name>: missing from the lock file"` or `"<name>: locked <version> does not satisfy <specifiers joined by ','>"`. Markers are ignored. All good: `[]` |

## Examples

```python
>>> normalize_name("Flask_SQLAlchemy")
'flask-sqlalchemy'
>>> parse_version("1.10.0") > parse_version("1.9")
True
>>> matches("1.4.9", "~=1.4.2"), matches("1.5", "~=1.4.2")
(True, False)
>>> parse_requirement('HTTPX[http2] >=0.27, <1 ; python_version >= "3.10"  # client')
Requirement(name='httpx', extras=('http2',), specifiers=('>=0.27', '<1'), marker='python_version >= "3.10"')
>>> _.allows("0.27.2"), _.allows("1.0")
(True, False)
>>> check(["httpx>=0.27,<1", "rich", "click>=8.1"], "httpx==0.26.0\nclick==8.1.7\n")
['httpx: locked 0.26.0 does not satisfy >=0.27,<1', 'rich: missing from the lock file']
```

## Hints

<details>
<summary>Hint 1: versions</summary>

`text.strip().split(".")`, then check every part with `part.isdigit()` (an empty part means `..`). Remove
trailing zeros with a `while parts and parts[-1] == 0: parts.pop()`. Tuples compare element by element,
and a shorter tuple that is a prefix is smaller: `(1,) < (1, 0, 1)`, which is exactly `1.0.0 < 1.0.1`.
</details>

<details>
<summary>Hint 2: specifiers</summary>

Check the two-character operators before the one-character ones, or `">=1"` is read as `">"` + `"=1"`.
A dict from operator to function (`operator.ge`, `operator.lt`, ...) keeps `matches` short. For `~=`
you need the parts of the spec **before** trailing zeros are removed: `~=1.4.0` means `==1.4.*`.
</details>

<details>
<summary>Hint 3: requirement lines</summary>

Cut off the comment, then the marker (`line.partition(";")`). A regular expression like
`([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[(.*?)\])?\s*(.*)` splits the rest into name, extras and the
specifier text; split that at commas.
</details>

## Check your work

```bash
pytest professional/01-project-setup/assignments/01-requirement-checker -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/01-project-setup/assignments/01-requirement-checker/exercise.py),
then tick off assignment 01 in the [progress checklist](../../../../README.md#progress-checklist).
