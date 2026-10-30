"""Assignment 06 · Grade calculator.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/05-conditions/assignments/06-grade-calculator -v
"""


def grade(points):
    """Return 'A'-'F' for 0-100 points (A: 90+, B: 80+, C: 70+, D: 60+, else F), or 'invalid'."""
    raise NotImplementedError


def passed(points):
    """Return True for grades A-D, False for F and for invalid points."""
    raise NotImplementedError


def feedback(points):
    """Return '<points> points: grade <letter>' or 'Invalid score: <points>'."""
    raise NotImplementedError


if __name__ == "__main__":
    print(feedback(float(input("Points: "))))
