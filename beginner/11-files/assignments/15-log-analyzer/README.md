# Assignment 15 · Log analyzer

> **Lesson:** [11 · Files](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~1.5 h

## Goal

Servers write **log files**: one line per event. When something breaks, the first job is to find out
what happened. Write a tool that reads a log line by line, skips broken lines, counts the levels, lists
the errors, and writes a short summary file.

## The log format

Each line has a date, a time, a level and a message, separated by spaces. The message may contain spaces
itself. See [`sample.log`](sample.log):

```text
2026-10-30 08:16:10 ERROR Database timeout after 30 s
2026-10-30 08:15:42 WARNING Slow response from /api/orders (2.3 s)
```

Real logs are messy: there are blank lines and broken lines (fewer than four parts). Skip them.

## What to write

| Function | Returns / does |
|---|---|
| `parse_line(line)` | a tuple `(date, time, level, message)`, or `None` for a blank or broken line. Strip the line first |
| `count_levels(path)` | a dict `level → number of lines` for all valid lines in the file at `path` |
| `error_messages(path)` | a list of the messages of all `ERROR` lines, in file order |
| `write_summary(log_path, summary_path)` | writes a summary file (format below) and returns nothing |

The summary file has one line per level, **sorted by level name**, then a blank line, then each error
message with a `- ` in front:

```text
ERROR: 2
INFO: 5
WARNING: 2

- Database timeout after 30 s
- Payment provider returned 503
```

Every line ends with `\n`. A missing log file should raise `FileNotFoundError` (Python does that for you
if you just open it; do not catch it).

## Examples

```python
>>> parse_line("2026-10-30 08:16:10 ERROR Database timeout after 30 s\n")
('2026-10-30', '08:16:10', 'ERROR', 'Database timeout after 30 s')
>>> parse_line("#### corrupted ####") is None
True
>>> parse_line("   \n") is None
True
>>> count_levels("sample.log")
{'INFO': 5, 'WARNING': 2, 'ERROR': 2}
>>> error_messages("sample.log")
['Database timeout after 30 s', 'Payment provider returned 503']
```

## Hints

<details>
<summary>Hint 1: splitting off only the first three parts</summary>

`line.split(maxsplit=3)` splits at most 3 times, so the message keeps its spaces:
`"a b c d e f".split(maxsplit=3)` → `['a', 'b', 'c', 'd e f']`. If the result has fewer than 4 parts,
the line is broken. A list of length 4 can be turned into a tuple with `tuple(parts)`.
</details>

<details>
<summary>Hint 2: reading line by line</summary>

```python
with open(path, encoding="utf-8") as file:
    for line in file:
        entry = parse_line(line)
        ...
```

Skip the line with `continue` when `entry is None`. Unpack the rest: `date, time, level, message = entry`.
</details>

<details>
<summary>Hint 3: write_summary</summary>

Reuse `count_levels` and `error_messages`. `sorted(counts)` gives the levels in alphabetical order.
Open the summary with `"w"` and `encoding="utf-8"`, and write each line with `"\n"` at the end.
</details>

## Check your work

```bash
pytest beginner/11-files/assignments/15-log-analyzer -v
```

The tests create their own temporary log files (pytest's `tmp_path`), so they never touch `sample.log`.
To run your program on the sample:

```bash
python beginner/11-files/assignments/15-log-analyzer/exercise.py
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/11-files/assignments/15-log-analyzer/exercise.py),
then tick off assignment 15 in the [progress checklist](../../../../README.md#progress-checklist).
