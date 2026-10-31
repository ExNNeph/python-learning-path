"""Assignment 09 · Contact book: template solution."""

import json
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

FORMAT_VERSION = 1


@dataclass
class Contact:
    name: str
    email: str
    birthday: date | None = None
    tags: set[str] = field(default_factory=set)


def encode(obj):
    """json.dumps default hook: date -> ISO string, set -> sorted list, else TypeError."""
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, set):
        return sorted(obj)          # sorted: the same set always gives the same JSON
    # Raising TypeError is the contract of `default`: json reports it as "not serializable".
    raise TypeError(f"cannot serialise {type(obj).__name__}")


def contact_to_dict(contact):
    """Return a dict with only JSON types (birthday as ISO string or None, tags sorted)."""
    return {
        "name": contact.name,
        "email": contact.email,
        "birthday": contact.birthday.isoformat() if contact.birthday else None,
        "tags": sorted(contact.tags),
    }


def contact_from_dict(data):
    """Validate data and return a Contact. Raise ValueError naming the bad field."""
    # The boundary: everything below checks what the rest of the program relies on, so
    # that bad files fail HERE with a clear message, not later with a KeyError.
    if not isinstance(data, dict):
        raise ValueError(f"contact must be an object, got {type(data).__name__}")

    name = data.get("name")             # .get: a missing key becomes None, checked below
    if not isinstance(name, str) or not name.strip():
        raise ValueError("field 'name' must be a non-empty string")

    email = data.get("email")
    if not isinstance(email, str) or "@" not in email:
        raise ValueError("field 'email' must be a string containing '@'")

    birthday = data.get("birthday")
    if birthday is not None:
        if not isinstance(birthday, str):
            raise ValueError("field 'birthday' must be an ISO date string")
        try:
            birthday = date.fromisoformat(birthday)
        except ValueError:
            raise ValueError(f"field 'birthday' is not a valid date: {birthday!r}") from None

    tags = data.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValueError("field 'tags' must be a list of strings")

    return Contact(name.strip(), email.strip().lower(), birthday, set(tags))


def save_contacts(path, contacts):
    """Write {"version": 1, "contacts": [...]} atomically as pretty UTF-8 JSON."""
    path = Path(path)
    document = {"version": FORMAT_VERSION, "contacts": [contact_to_dict(c) for c in contacts]}
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as file:
        json.dump(document, file, indent=2, ensure_ascii=False)
    # Atomic swap: if anything above failed, the old file is still intact.
    os.replace(tmp, path)


def load_contacts(path):
    """Return the contacts in the file; [] if it does not exist; ValueError if invalid."""
    path = Path(path)
    try:
        with open(path, encoding="utf-8") as file:
            document = json.load(file)
    except FileNotFoundError:
        return []                       # first run: no file yet is not an error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path.name}: {error}") from None

    if not isinstance(document, dict) or document.get("version") != FORMAT_VERSION:
        raise ValueError(f"{path.name} is not a version {FORMAT_VERSION} contact book")
    contacts = document.get("contacts")
    if not isinstance(contacts, list):
        raise ValueError(f"field 'contacts' in {path.name} must be a list")
    return [contact_from_dict(item) for item in contacts]


if __name__ == "__main__":
    book = Path(__file__).with_name("contacts.json")
    contacts = load_contacts(book)
    print(f"{len(contacts)} contacts loaded from {book.name}")
    contacts.append(Contact("Ada Lovelace", "ada@example.com", date(1815, 12, 10), {"math"}))
    save_contacts(book, contacts)
    print(book.read_text(encoding="utf-8"))
