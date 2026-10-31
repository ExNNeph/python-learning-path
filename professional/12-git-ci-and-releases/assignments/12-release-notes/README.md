# Assignment 12 · Release notes

> **Lesson:** [12 · Git, CI and releases](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Build the core of a release tool like release-please or python-semantic-release: read the commit
messages since the last release, recognise Conventional Commits, decide the next semantic version, and
write the changelog section. A CI job would then tag the version and publish the package.

## Conventional Commits, as this tool understands them

The **first line** of a message must look like `type(scope)!: description`:

- `type`: lower-case letters (`feat`, `fix`, `docs`, …);
- `(scope)`: optional, any characters except brackets and whitespace;
- `!`: optional, marks a breaking change;
- then a colon, **one space**, and a description that does not start with whitespace.

Anything else (`Merge branch 'main'`, `Fix bug`, `feat:no space`) is **not** a Conventional Commit and
is ignored. A line `BREAKING CHANGE: <note>` (or `BREAKING-CHANGE: <note>`) anywhere after the first
line also marks the commit as breaking; the note is kept.

## What to write

| Name | Specification |
|---|---|
| `parse_commit(message)` | a `Commit` (given: `type`, `scope` or `None`, `description`, `breaking`, `breaking_note` or `None`), or `None` for a non-conventional message. Surrounding whitespace of the message is ignored |
| `parse_version(text)` | `"1.4.2"` → `(1, 4, 2)`. Exactly three numbers without leading zeros (`0` itself is fine); anything else (`v1.4.2`, `1.4`, `01.2.3`) raises `ValueError` |
| `bump_kind(commits)` | `"major"` if any commit is breaking, else `"minor"` if any is a `feat`, else `"patch"` if any is a `fix` or `perf`, else `None` |
| `next_version(current, commits)` | applies the bump to `current`: major → `X+1.0.0`, minor → `X.Y+1.0`, patch → `X.Y.Z+1`. **While the major version is 0**, a breaking change bumps the minor version. No bump: return `current` unchanged |
| `render_changelog(version, date, commits)` | the Markdown section, see below |
| `release(current, messages, date)` | parses the messages (ignoring non-conventional ones) and returns `(next version, changelog)`, or `(current, None)` if there is nothing to release |

### The changelog section

```markdown
## 2.0.0 (2026-11-01)

### ⚠ Breaking changes
- **api:** remove the v1 endpoints
- ApiClient now needs a transport

### Features
- **cli:** add --json output
- **api:** remove the v1 endpoints

### Bug fixes
- handle empty files
```

- The title line, then the sections in this order: `⚠ Breaking changes` (every breaking commit; its
  `breaking_note` if it has one, else its description), `Features` (`feat`), `Bug fixes` (`fix`),
  `Performance` (`perf`). Other types appear only under breaking changes.
- Entries keep the order of the commits. With a scope: `- **scope:** text`, without: `- text`.
- Empty sections are left out. Blocks are separated by one empty line; the text ends with one `"\n"`.

## Example

```python
>>> messages = [
...     "feat(cli): add --json output",
...     "fix: handle empty files",
...     "docs: explain the retry settings",
...     "Merge branch 'main' into feature",
...     "feat(api)!: remove the v1 endpoints",
...     "refactor: split the client\n\nBREAKING CHANGE: ApiClient now needs a transport",
... ]
>>> version, notes = release("1.2.0", messages, "2026-11-01")
>>> version
'2.0.0'
>>> print(notes)          # the section shown above
```

## Hints

<details>
<summary>Hint 1: the header</summary>

One regular expression with named groups does it:
`(?P<type>[a-z]+)(?:\((?P<scope>[^()\s]+)\))?(?P<bang>!)?: (?P<description>\S.*)`, used with `fullmatch`
on the first line. For the footer, search the rest with `re.MULTILINE` and `^BREAKING[ -]CHANGE: (.+)$`.
</details>

<details>
<summary>Hint 2: building the text</summary>

Collect the blocks in a list (`["## 2.0.0 (2026-11-01)", "### Features\n- ...", ...]`) and finish with
`"\n\n".join(blocks) + "\n"`. A list of `(type, title)` pairs keeps the section order in one place.
</details>

## Check your work

```bash
pytest professional/12-git-ci-and-releases/assignments/12-release-notes -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/12-git-ci-and-releases/assignments/12-release-notes/exercise.py),
then tick off assignment 12 in the [progress checklist](../../../../README.md#progress-checklist).
