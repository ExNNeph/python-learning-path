"""Assignment 07 · Leap years: template solution."""


def is_leap_year(year):
    """Return True if year is a Gregorian leap year (div. by 4, not by 100 unless by 400)."""
    # The rule in words, translated one to one. The brackets are not strictly needed
    # (`and` binds tighter than `or`), but they show the reader the grouping.
    # The comparison already is a bool, so there is no need for if/else.
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def days_in_month(month, year):
    """Return the number of days in month (1-12) of year, or None for an invalid month."""
    if not 1 <= month <= 12:
        return None
    if month == 2:
        # A conditional expression: a choice between two values.
        return 29 if is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def season(month):
    """Return 'winter' (Dec-Feb), 'spring' (Mar-May), 'summer' (Jun-Aug), 'autumn' (Sep-Nov) or None."""
    # Winter wraps around the year end (12, 1, 2), so a membership test is
    # clearer than a range here. The other seasons are contiguous ranges.
    if month in (12, 1, 2):
        return "winter"
    if 3 <= month <= 5:
        return "spring"
    if 6 <= month <= 8:
        return "summer"
    if 9 <= month <= 11:
        return "autumn"
    return None


if __name__ == "__main__":
    year = int(input("Year: "))
    print(year, "is a leap year" if is_leap_year(year) else "is not a leap year")
