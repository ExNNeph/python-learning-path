# Assignment 10 · Text extractor

> **Lesson:** [09 · Regular expressions](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Seven small text jobs, each solved with one well-chosen regular expression. Define the patterns as
**named module-level constants** (e.g. `EMAIL = re.compile(...)`) and keep each function short.

## What to write

| Function | Does |
|---|---|
| `find_emails(text)` | a list of all email addresses, in order. An address here is: one or more of letters, digits, `.`, `_`, `%`, `+`, `-`; then `@`; then a domain made of letters, digits, `-` and dots that **ends with a dot and at least two letters** |
| `is_valid_username(name)` | `True` if the **whole** name is 3 to 16 characters of letters, digits and `_`, **starting with a letter** |
| `dates_to_iso(text)` | the text with every date `DD.MM.YYYY` rewritten as `YYYY-MM-DD` |
| `parse_log_line(line)` | a dict with the keys `date`, `time`, `level`, `source`, `message` for a line like `2026-10-31 14:30:05 [ERROR] db: connection lost`; `None` if the line has a different form |
| `hashtags(text)` | the hashtags (`#` followed by word characters) **lower-cased, without `#`, without duplicates, in order of first appearance** |
| `squash_whitespace(text)` | every run of whitespace (spaces, tabs, newlines) replaced by one space, ends stripped |
| `mask_card_numbers(text)` | every card number of 16 digits, written in four blocks of four separated by nothing, single spaces or single dashes, replaced by `**** **** **** ` + its last four digits |

## Examples

```python
>>> find_emails("Mail ada.l+news@math.example.org or grace@navy.mil, not bob@localhost.")
['ada.l+news@math.example.org', 'grace@navy.mil']
>>> is_valid_username("ada_1815"), is_valid_username("1ada"), is_valid_username("ad")
(True, False, False)
>>> dates_to_iso("Born 10.12.1815, died 27.11.1852")
'Born 1815-12-10, died 1852-11-27'
>>> parse_log_line("2026-10-31 14:30:05 [ERROR] db: connection lost")
{'date': '2026-10-31', 'time': '14:30:05', 'level': 'ERROR', 'source': 'db', 'message': 'connection lost'}
>>> hashtags("Learning #Python! #regex is fun. #python #Py3")
['python', 'regex', 'py3']
>>> squash_whitespace("  too   many\n\tspaces ")
'too many spaces'
>>> mask_card_numbers("Card 4111-1111-1111-1234, backup 5500000000000004.")
'Card **** **** **** 1234, backup **** **** **** 0004.'
```

## Hints

<details>
<summary>Hint 1: find_emails and is_valid_username</summary>

Email: `[\w.%+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}`, roughly; check the edge cases in the tests.
`(?:...)` groups without capturing, which matters because `findall` returns groups when there are any.
Username: `fullmatch` with `[A-Za-z]\w{2,15}`. Careful: `\w` also matches letters like `é`;
the tests accept that.
</details>

<details>
<summary>Hint 2: dates_to_iso and mask_card_numbers</summary>

Both are `re.sub` with groups. For the date, `\b(\d{2})\.(\d{2})\.(\d{4})\b` and the replacement `r"\3-\2-\1"`.
For the card, put each block of four in a group and allow an optional separator between them:
`\b(\d{4})[ -]?(\d{4})[ -]?(\d{4})[ -]?(\d{4})\b`. The replacement only needs group 4.
</details>

<details>
<summary>Hint 3: parse_log_line and hashtags</summary>

Use named groups and `fullmatch(...)`, then `.groupdict()`. For hashtags, `findall(r"#(\w+)", text)`
returns only the part in the group. Remove duplicates while keeping the order with a `seen` set, or with
`list(dict.fromkeys(items))` (dict keys are unique and keep insertion order).
</details>

## Check your work

```bash
pytest intermediate/09-regular-expressions/assignments/10-text-extractor -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/09-regular-expressions/assignments/10-text-extractor/exercise.py),
then tick off assignment 10 in the [progress checklist](../../../../README.md#progress-checklist).
