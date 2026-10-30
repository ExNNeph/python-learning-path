# Assignment 17 · Requirements parser

> **Lesson:** [13 · venv and pip](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~1.5 h

## Goal

Read `requirements.txt` files the way pip does, and compare two versions of one. A tool like this
answers a common code-review question: *"what did this change do to our dependencies?"* You combine
string processing, dicts, sets and functions from the whole Beginner level.

## The rules

- Blank lines and lines starting with `#` are ignored.
- An inline comment (` # ...`) is removed: `pytest>=7  # tests` means `pytest>=7`.
- A requirement is a **name**, optionally followed by a **specifier** that starts with one of the
  characters `=`, `<`, `>`, `!`, `~`.
- Names are case-insensitive, and `_` and `-` mean the same thing: `Flask_Login` is `flask-login`.
  **Normalise** names to lower case with `-`.
- Spaces anywhere in the specifier are removed: `flask == 3.0.3` → `==3.0.3`.

## What to write

| Function | Returns |
|---|---|
| `parse_requirement(line)` | a tuple `(name, specifier)` with the normalised name and the specifier (`""` if there is none), or `None` for a blank or comment line |
| `parse_requirements(text)` | a dict `name → specifier` for all requirements in the text |
| `pinned(requirements)` | a sorted list of the names whose specifier starts with `==` (given a dict like the one above) |
| `diff_requirements(old_text, new_text)` | a dict with the sorted lists `"added"`, `"removed"` and `"changed"` (same name, different specifier) |

## Examples

```python
>>> parse_requirement("requests>=2.31")
('requests', '>=2.31')
>>> parse_requirement("Flask_Login == 0.6.3   # auth")
('flask-login', '==0.6.3')
>>> parse_requirement("rich")
('rich', '')
>>> parse_requirement("# just a comment") is None
True
>>> reqs = parse_requirements("requests~=2.32\nflask==3.0.3\n\npytest>=7\n")
>>> reqs
{'requests': '~=2.32', 'flask': '==3.0.3', 'pytest': '>=7'}
>>> pinned(reqs)
['flask']
>>> diff_requirements("flask==2.3\nrequests\n", "flask==3.0.3\nrich\n")
{'added': ['rich'], 'removed': ['requests'], 'changed': ['flask']}
```

## Hints

<details>
<summary>Hint 1: comments</summary>

`line.split("#")[0]` keeps everything before the first `#` (the whole line if there is none). Then
`.strip()`. If nothing is left, return `None`.
</details>

<details>
<summary>Hint 2: where does the name end?</summary>

Loop over the characters with `enumerate` and stop at the first one that is `in "=<>!~"`. Everything before
is the name, everything from there on is the specifier. If no such character exists, the whole line is the
name. Remove spaces from the specifier with `.replace(" ", "")`.
</details>

<details>
<summary>Hint 3: normalising the name</summary>

`.strip().lower().replace("_", "-")`.
</details>

<details>
<summary>Hint 4: diff</summary>

Parse both texts. The names are the dict keys, so set operations from lesson 08 do most of the work:
`new.keys() - old.keys()` are the added names. For "changed", look at the names in **both** and compare
their specifiers. Remember to sort each list.
</details>

## Check your work

```bash
pytest beginner/13-venv-and-pip/assignments/17-requirements-parser -v
```

Then run it on this repository's own `requirements.txt`:

```bash
python beginner/13-venv-and-pip/assignments/17-requirements-parser/exercise.py
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/13-venv-and-pip/assignments/17-requirements-parser/exercise.py),
then tick off assignment 17 in the [progress checklist](../../../../README.md#progress-checklist).
