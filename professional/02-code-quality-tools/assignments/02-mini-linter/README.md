# Assignment 02 · Mini linter

> **Lesson:** [02 · Code quality tools](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Build a small linter in the style of `ruff`: it parses Python source with `ast`, walks the tree, reports
five kinds of problems with rule codes, respects `# noqa` comments, lets you select rules, and has a
command line with a proper exit code.

## The rules

| Code | Finds | Message | Position |
|---|---|---|---|
| `PLP001` | an imported name that is never used | `'<name>' imported but unused` | the `import` statement |
| `PLP002` | a bare `except:` | `bare except` | the `except` clause |
| `PLP003` | a mutable default argument: a list, dict or set literal, or a call to `list()`, `dict()` or `set()` | `mutable default argument in '<function>'` | the default value |
| `PLP004` | a call to `print` | `print found` | the call |
| `PLP005` | `== None` or `!= None` | `comparison to None: use 'is' or 'is not'` | the comparison |

Details for `PLP001`: the name an import **binds** counts (`import os.path` binds `os`,
`import numpy as np` binds `np`, `from a import b as c` binds `c`). A name counts as used if it appears
anywhere as a name (`os.getcwd()` uses `os`) or as a string in a module-level `__all__ = [...]`.
`from __future__ import ...` is never reported. One finding per unused name.

## What to write

| Name | Specification |
|---|---|
| `Finding` | a **frozen**, **ordered** dataclass with the fields `line`, `col`, `code`, `message` (in that order, so findings sort by position). Lines and columns are **1-based** |
| `lint(source, select=None)` | returns the sorted list of findings. `select`: an iterable of codes to check (default: all five). Lines with `# noqa` drop all findings on that line; `# noqa: PLP002, PLP004` drops only those codes. Source that does not parse gives exactly one finding: code `PLP000`, message `syntax error: <the error's msg>`, at the error's line and column |
| `format_finding(path, finding)` | `"<path>:<line>:<col>: <code> <message>"` |
| `main(argv)` | lints each file named in `argv` (read as UTF-8), prints every finding with `format_finding`, then a summary line `Found N problem(s).` or `All checks passed.`, and **returns** the exit code: `1` if anything was found, else `0`. Option `--select PLP001,PLP004` restricts the rules |

## Examples

```python
>>> source = '''
... import os, sys
... def add(item, items=[]):
...     try:
...         items.append(item)
...     except:
...         print("failed")
...     return items if sys.argv != None else None
... '''
>>> for finding in lint(source):
...     print(format_finding("demo.py", finding))
demo.py:2:1: PLP001 'os' imported but unused
demo.py:3:21: PLP003 mutable default argument in 'add'
demo.py:6:5: PLP002 bare except
demo.py:7:9: PLP004 print found
demo.py:8:21: PLP005 comparison to None: use 'is' or 'is not'

>>> lint("print('hi')  # noqa: PLP004")
[]
>>> lint("def f(:")
[Finding(line=1, col=7, code='PLP000', message='syntax error: invalid syntax')]
```

```text
$ python exercise.py --select PLP004 demo.py
demo.py:7:9: PLP004 print found
Found 1 problem(s).
```

## Hints

<details>
<summary>Hint 1: one visitor for everything</summary>

A class `Checker(ast.NodeVisitor)` with a `findings` list and a method per node type: `visit_Import`,
`visit_ImportFrom`, `visit_ExceptHandler` (`node.type is None` means bare), `visit_FunctionDef` (the
defaults are in `node.args.defaults` and `node.args.kw_defaults`, which may contain `None`), `visit_Call`,
`visit_Compare` and `visit_Name`. Remember `self.generic_visit(node)` in each. `visit_AsyncFunctionDef =
visit_FunctionDef` covers `async def` too.
</details>

<details>
<summary>Hint 2: unused imports need two passes</summary>

While visiting, remember the imports as `{name: node}` and collect every `Name.id` in a set. After the
walk, the unused names are those in the first dict but not in the set. `alias.asname or
alias.name.split(".")[0]` is the bound name. For `__all__`, look at module-level `ast.Assign` nodes whose
target is the name `__all__` and whose value is a list or tuple of string constants.
</details>

<details>
<summary>Hint 3: noqa and syntax errors</summary>

`source.splitlines()[finding.line - 1]` is the line of a finding. A regular expression
`#\s*noqa(?::\s*([A-Z0-9,\s]+))?` tells you whether there is a `noqa` and which codes it lists. A
`SyntaxError` has the attributes `msg`, `lineno` and `offset` (already 1-based).
</details>

## Check your work

```bash
pytest professional/02-code-quality-tools/assignments/02-mini-linter -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/02-code-quality-tools/assignments/02-mini-linter/exercise.py),
then tick off assignment 02 in the [progress checklist](../../../../README.md#progress-checklist).
