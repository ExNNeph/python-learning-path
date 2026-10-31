# Assignment 09 · Contact book

> **Lesson:** [08 · JSON and structured data](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2 h

## Goal

Save a list of contacts as a JSON file and load it back, **without losing anything** (dates, sets) and
**without trusting the file**: a hand-edited or corrupted file must produce a clear `ValueError`, never
a `KeyError` somewhere deep inside the program.

The file looks like this:

```json
{
  "version": 1,
  "contacts": [
    {
      "name": "Zoë Ada",
      "email": "zoe@example.com",
      "birthday": "1990-12-10",
      "tags": ["family", "math"]
    }
  ]
}
```

## What to write

`Contact` is already defined for you: a dataclass with `name: str`, `email: str`,
`birthday: date | None = None` and `tags: set[str]` (default: empty set).

| Function | Does |
|---|---|
| `encode(obj)` | a `default=` hook for `json.dumps`: `date` → ISO string, `set` → **sorted** list. Anything else: `TypeError` |
| `contact_to_dict(contact)` | a dict with only JSON types: `birthday` as ISO string or `None`, `tags` as a **sorted** list |
| `contact_from_dict(data)` | builds a `Contact` from a dict, **validating** it (rules below). Unknown keys are ignored |
| `save_contacts(path, contacts)` | writes `{"version": 1, "contacts": [...]}` with `indent=2`, `ensure_ascii=False`, UTF-8, **atomically** (temporary file + `os.replace`) |
| `load_contacts(path)` | returns the list of contacts. A file that does not exist: `[]`. Invalid JSON, a wrong `version` or a wrong shape: `ValueError` |

Validation rules for `contact_from_dict`, each violation raising `ValueError` with a message that
**names the field**:

- `data` must be a dict;
- `name`: a non-empty string (stripped);
- `email`: a string that contains `@` (stripped and lower-cased);
- `birthday` (optional, may be missing or `null`): an ISO date string;
- `tags` (optional): a list of strings; becomes a set.

## Examples

```python
>>> ada = Contact("Zoë Ada", "zoe@example.com", date(1990, 12, 10), {"math", "family"})
>>> contact_to_dict(ada)
{'name': 'Zoë Ada', 'email': 'zoe@example.com', 'birthday': '1990-12-10', 'tags': ['family', 'math']}
>>> contact_from_dict({"name": " Linus ", "email": "LINUS@Example.org"})
Contact(name='Linus', email='linus@example.org', birthday=None, tags=set())
>>> contact_from_dict({"name": "Linus"})
Traceback (most recent call last):
ValueError: field 'email' must be a string containing '@'
>>> json.dumps({"when": date(2026, 1, 1), "tags": {"b", "a"}}, default=encode)
'{"when": "2026-01-01", "tags": ["a", "b"]}'
>>> save_contacts("contacts.json", [ada])
>>> load_contacts("contacts.json") == [ada]
True
```

## Hints

<details>
<summary>Hint 1: contact_from_dict</summary>

Use `data.get("email")` (not `data["email"]`) so a missing key gives `None`, and then check with
`isinstance(value, str)`. For the birthday, wrap only `date.fromisoformat(...)` in `try`/`except ValueError`
and re-raise with your own message (`raise ValueError(...) from None`).
</details>

<details>
<summary>Hint 2: load_contacts</summary>

`FileNotFoundError` → return `[]`. `json.JSONDecodeError` is already a `ValueError`, but re-raising it
with the file name makes the message more helpful. Then check: is the top level a dict, is `version`
equal to `1`, is `contacts` a list? Finally `[contact_from_dict(item) for item in ...]`.
</details>

<details>
<summary>Hint 3: save_contacts</summary>

See lesson 08, section 6. Use `Path(path)` so both strings and `Path` objects work.
</details>

## Check your work

```bash
pytest intermediate/08-json-and-structured-data/assignments/09-contact-book -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/08-json-and-structured-data/assignments/09-contact-book/exercise.py),
then tick off assignment 09 in the [progress checklist](../../../../README.md#progress-checklist).
