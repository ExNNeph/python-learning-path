"""Assignment 09 · Contact book.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest intermediate/08-json-and-structured-data/assignments/09-contact-book -v
"""

import json
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class Contact:
    name: str
    email: str
    birthday: date | None = None
    tags: set[str] = field(default_factory=set)


def encode(obj):
    """json.dumps default hook: date -> ISO string, set -> sorted list, else TypeError."""
    raise NotImplementedError


def contact_to_dict(contact):
    """Return a dict with only JSON types (birthday as ISO string or None, tags sorted)."""
    raise NotImplementedError


def contact_from_dict(data):
    """Validate data and return a Contact. Raise ValueError naming the bad field."""
    raise NotImplementedError


def save_contacts(path, contacts):
    """Write {"version": 1, "contacts": [...]} atomically as pretty UTF-8 JSON."""
    raise NotImplementedError


def load_contacts(path):
    """Return the contacts in the file; [] if it does not exist; ValueError if invalid."""
    raise NotImplementedError


if __name__ == "__main__":
    book = Path(__file__).with_name("contacts.json")
    contacts = load_contacts(book)
    print(f"{len(contacts)} contacts loaded from {book.name}")
    contacts.append(Contact("Ada Lovelace", "ada@example.com", date(1815, 12, 10), {"math"}))
    save_contacts(book, contacts)
    print(book.read_text(encoding="utf-8"))
