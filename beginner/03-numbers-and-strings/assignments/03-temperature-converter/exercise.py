"""Assignment 03 · Temperature converter.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/03-numbers-and-strings/assignments/03-temperature-converter -v
"""


def celsius_to_fahrenheit(celsius):
    """Return the temperature in °F, rounded to 1 decimal: 100 -> 212.0."""
    raise NotImplementedError


def fahrenheit_to_celsius(fahrenheit):
    """Return the temperature in °C, rounded to 1 decimal: 0 -> -17.8."""
    raise NotImplementedError


def celsius_to_kelvin(celsius):
    """Return the temperature in K, rounded to 2 decimals: -273.15 -> 0.0."""
    raise NotImplementedError


def format_temperature(value, unit):
    """Return e.g. '21.5 °C' for (21.456, 'C'): one decimal, a space, the degree sign, the unit."""
    raise NotImplementedError


if __name__ == "__main__":
    body = 37
    print(format_temperature(body, "C"), "=", format_temperature(celsius_to_fahrenheit(body), "F"))
