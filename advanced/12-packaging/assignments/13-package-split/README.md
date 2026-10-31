# Assignment 13 · Package split

> **Lesson:** [12 · Packaging](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

`exercise.py` is a complete little program in **one** file: text helpers, statistics and a command line.
Turn it into a proper **package** with layered modules, a public API, a `__main__.py` and a
`pyproject.toml`, without breaking anyone who still imports the old file.

This assignment is about structure, not new code: you mostly **move** code. That is a real skill:
almost every project starts as one file and has to be split at some point.

## What to build

Create everything **in this folder**, next to `exercise.py`:

```text
13-package-split/
├── pyproject.toml
├── exercise.py          ← becomes a small shim (step 4)
└── wordtools/
    ├── __init__.py      ← the public API
    ├── __main__.py      ← python -m wordtools
    ├── text.py          ← words(), slugify(), word_count()
    ├── stats.py         ← top_words()
    └── cli.py           ← main()
```

### Step 1 · The modules

| Module | Contains | May import from the package |
|---|---|---|
| `text.py` | `words`, `slugify`, `word_count` | nothing (it is the lowest layer) |
| `stats.py` | `top_words` | `text`, with a **relative** import |
| `cli.py` | `main(argv=None)`, unchanged behaviour | anything |

### Step 2 · The public API

`wordtools/__init__.py` re-exports `slugify`, `word_count` and `top_words`, lists exactly those three in
`__all__`, and sets `__version__ = "1.0.0"`. (`words` stays an internal helper of `wordtools.text`.)

### Step 3 · Running and installing

- `wordtools/__main__.py` calls `cli.main()` and exits with its return code, so
  `python -m wordtools top FILE -n 2` works.
- `pyproject.toml` declares a setuptools build backend, the project `name = "wordtools"`, a `version`
  equal to `wordtools.__version__`, `requires-python = ">=3.10"`, and a command-line entry point
  `wordtools` that points to `wordtools.cli:main`. Tell setuptools which package to include with
  `[tool.setuptools]` `packages = ["wordtools"]`.

### Step 4 · The shim

Code elsewhere still does `from exercise import slugify`. Replace the contents of `exercise.py` by a
shim that:

- re-exports `slugify`, `word_count`, `top_words` and `__version__` **from `wordtools`** (the very same
  function objects, no copies),
- emits a `DeprecationWarning` on import (`"importing from 'exercise' is deprecated; use 'wordtools' instead"`),
- defines no functions of its own.

## Check it by hand

From this folder:

```bash
python -m wordtools slug "Hello, World!"
```

```bash
python -m wordtools top exercise.py -n 3
```

And, in a fresh venv, the real installation (your `pyproject.toml` at work):

```bash
pip install -e .
wordtools --version
```

## Hints

<details>
<summary>Hint 1: moving code</summary>

Move one function at a time and run `python -m wordtools ...` after each move. Each module gets only the
imports it needs (`re` for `text.py`, `Counter` for `stats.py`, `argparse` for `cli.py`). In `cli.py`,
`from . import __version__` reads the version from the package.
</details>

<details>
<summary>Hint 2: pyproject.toml</summary>

Start from the example in the lesson. The `[project.scripts]` line has the form
`command = "package.module:function"`.
</details>

<details>
<summary>Hint 3: the shim</summary>

```python
import warnings

from wordtools import __version__, slugify, top_words, word_count

warnings.warn("...", DeprecationWarning, stacklevel=2)
```

`stacklevel=2` makes the warning point at the line that imported the shim, which is where the user
has to change something.
</details>

## Check your work

```bash
pytest advanced/12-packaging/assignments/13-package-split -v
```

The tests read `pyproject.toml` with `tomllib`, which exists from Python 3.11 on; on 3.10 those tests are
skipped.

## Done?

Compare with the [template solution](../../../../solutions/advanced/12-packaging/assignments/13-package-split/),
then tick off assignment 13 in the [progress checklist](../../../../README.md#progress-checklist).
