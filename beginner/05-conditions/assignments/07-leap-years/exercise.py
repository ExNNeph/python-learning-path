"""Assignment 07 · Leap years.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/05-conditions/assignments/07-leap-years -v
"""


def is_leap_year(year):
    """Return True if year is a Gregorian leap year (div. by 4, not by 100 unless by 400)."""
    raise NotImplementedError


def days_in_month(month, year):
    """Return the number of days in month (1-12) of year, or None for an invalid month."""
    raise NotImplementedError


def season(month):
    """Return 'winter' (Dec-Feb), 'spring' (Mar-May), 'summer' (Jun-Aug), 'autumn' (Sep-Nov) or None."""
    raise NotImplementedError


if __name__ == "__main__":
    year = int(input("Year: "))
    print(year, "is a leap year" if is_leap_year(year) else "is not a leap year")
