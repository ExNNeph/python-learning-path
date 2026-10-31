"""Assignment 13 · Review fixes.

This module was submitted in a pull request and came back with seven review comments (see README.md).
Address every comment. The tests check each one.
Check your work:  pytest professional/13-code-review-and-documentation/assignments/13-review-fixes -v
"""

import datetime


def add_line(lines=[], description="", price=0.0, qty=1):
    lines.append({"description": description, "price": price, "qty": qty})
    return lines


def total(lines, tax=0.19):
    t = 0.0
    for l in lines:
        t = t + l["price"] * l["qty"]
    return round(t * (1 + tax), 2)


def find_duplicates(lines):
    dups = []
    for i in range(len(lines)):
        for j in range(len(lines)):
            if i != j and lines[i]["description"] == lines[j]["description"]:
                if lines[i]["description"] not in dups:
                    dups.append(lines[i]["description"])
    return dups


def parse_amount(text):
    try:
        return float(text.replace(",", "."))
    except:
        return 0


def due_date(issued, days=30):
    return issued + datetime.timedelta(days)


def calc(lines):
    return total(lines)
