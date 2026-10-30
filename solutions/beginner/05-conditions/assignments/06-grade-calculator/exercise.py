"""Assignment 06 · Grade calculator: template solution."""


def grade(points):
    """Return 'A'-'F' for 0-100 points (A: 90+, B: 80+, C: 70+, D: 60+, else F), or 'invalid'."""
    # Guard clause: deal with bad input first, so the rest only sees valid points.
    if not 0 <= points <= 100:
        return "invalid"
    # Narrowest condition first. Each elif is only reached when every condition
    # above it was False, so "points >= 80" here already means 80 <= points < 90.
    if points >= 90:
        return "A"
    elif points >= 80:
        return "B"
    elif points >= 70:
        return "C"
    elif points >= 60:
        return "D"
    return "F"


def passed(points):
    """Return True for grades A-D, False for F and for invalid points."""
    # Reusing grade() keeps the boundaries in one place.
    # `in` with a string checks for a substring; "invalid" and "F" are not in "ABCD".
    # A tuple ("A", "B", "C", "D") would work just as well and be stricter.
    return grade(points) in ("A", "B", "C", "D")


def feedback(points):
    """Return '<points> points: grade <letter>' or 'Invalid score: <points>'."""
    letter = grade(points)
    if letter == "invalid":
        return f"Invalid score: {points}"
    return f"{points} points: grade {letter}"


if __name__ == "__main__":
    print(feedback(float(input("Points: "))))
