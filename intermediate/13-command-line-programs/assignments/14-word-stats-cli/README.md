# Assignment 14 · Word stats CLI

> **Lesson:** [13 · Command-line programs](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Build `wordstats`, a small command-line tool that counts the most common words in files or in its
standard input. It should behave like a real Unix tool: `--help`, clear errors on stderr, correct exit
codes, and it works in a pipe.

```text
$ python exercise.py --top 3 --min-length 4 sample.txt
    5  python
    2  code
    2  readable
$ cat sample.txt | python exercise.py --top 1 --format json
{
  "total": 40,
  "unique": 30,
  "top": [
    [
      "python",
      5
    ]
  ]
}
$ python exercise.py missing.txt
wordstats: error: cannot read missing.txt: No such file or directory
$ echo $?
1
```

## The command line

```text
usage: wordstats [-h] [--version] [-t N] [-m N] [--case-sensitive] [-f {text,json}] [FILE ...]
```

| Argument | Meaning |
|---|---|
| `FILE ...` | zero or more files. **None, or `-`**: read standard input |
| `-t N`, `--top N` | how many words to show, default `10`; must be at least 1 (else a usage error) |
| `-m N`, `--min-length N` | ignore words shorter than N characters, default `1`; must be at least 1 |
| `--case-sensitive` | count `Python` and `python` separately (default: lower-case everything) |
| `-f`, `--format` | `text` (default) or `json` |
| `--version` | prints `wordstats 1.0` and exits |

## What to write

| Function | Does |
|---|---|
| `positive_int(text)` | an argparse `type`: returns the int, raises `argparse.ArgumentTypeError` if it is below 1 |
| `build_parser()` | returns the `ArgumentParser` with `prog="wordstats"` and the arguments above |
| `count_words(lines, min_length=1, case_sensitive=False)` | a `Counter` of the words in an iterable of lines. A word is a run of letters, digits, `_` or `'` (regex `[\w']+`) |
| `format_text(counts, top)` | one line per word, `f"{count:>5}  {word}"`, most common first, joined with `"\n"`. No words: `""` |
| `format_json(counts, top)` | `json.dumps({"total": ..., "unique": ..., "top": [[word, count], ...]}, indent=2)`, where `total` is the number of words counted and `unique` the number of different ones |
| `main(argv=None)` | parses `argv`, reads the files (or stdin), prints the report to stdout and **returns** the exit code: `0` on success, `1` if a file cannot be read (message on **stderr**: `wordstats: error: cannot read <file>: <reason>`) |

Ties in the ranking keep the order in which the words first appeared (that is what `Counter.most_common` does).

## Hints

<details>
<summary>Hint 1: reading files and stdin</summary>

Read everything first, so that a missing second file does not print a half-finished report:

```python
def read_lines(paths):
    lines = []
    for path in paths or ["-"]:
        if path == "-":
            lines.extend(sys.stdin)
        else:
            with open(path, encoding="utf-8") as file:
                lines.extend(file)
    return lines
```

`open` raises `FileNotFoundError` (an `OSError`); its `.strerror` attribute is the reason text,
e.g. `No such file or directory`.
</details>

<details>
<summary>Hint 2: the json format for an indented list of pairs</summary>

`json.dumps(..., indent=2)` puts every list item on its own line. That is fine: the tests compare the
**parsed** JSON, not the exact text.
</details>

<details>
<summary>Hint 3: testing it yourself</summary>

Call `main` directly in the REPL: `main(["--top", "3", "sample.txt"])`. The test file shows how pytest's
`capsys` and `monkeypatch` check the output and fake stdin.
</details>

## Check your work

```bash
pytest intermediate/13-command-line-programs/assignments/14-word-stats-cli -v
```

Then use your tool for real:

```bash
python intermediate/13-command-line-programs/assignments/14-word-stats-cli/exercise.py --help
```

```bash
python intermediate/13-command-line-programs/assignments/14-word-stats-cli/exercise.py intermediate/*/README.md --top 15 --min-length 6
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/13-command-line-programs/assignments/14-word-stats-cli/exercise.py),
then tick off assignment 14 in the [progress checklist](../../../../README.md#progress-checklist).
