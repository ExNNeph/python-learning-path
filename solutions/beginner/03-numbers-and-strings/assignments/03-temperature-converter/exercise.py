"""Assignment 03 · Temperature converter: template solution."""


def celsius_to_fahrenheit(celsius):
    """Return the temperature in °F, rounded to 1 decimal: 100 -> 212.0."""
    # `/` always returns a float, so the result is a float even for whole numbers (212.0).
    # Rounding hides binary float noise such as 99.50000000000001.
    return round(celsius * 9 / 5 + 32, 1)


def fahrenheit_to_celsius(fahrenheit):
    """Return the temperature in °C, rounded to 1 decimal: 0 -> -17.8."""
    # The brackets matter: without them Python would compute 32 * 5 / 9 first.
    return round((fahrenheit - 32) * 5 / 9, 1)


def celsius_to_kelvin(celsius):
    """Return the temperature in K, rounded to 2 decimals: -273.15 -> 0.0."""
    # 0.1 + 273.15 is 273.25000000000006 in binary floating point; round() fixes the display.
    return round(celsius + 273.15, 2)


def format_temperature(value, unit):
    """Return e.g. '21.5 °C' for (21.456, 'C'): one decimal, a space, the degree sign, the unit."""
    # The format spec .1f both rounds and *always* shows one decimal,
    # which round() alone cannot do: round(-40, 1) is still the int -40.
    return f"{value:.1f} °{unit}"


if __name__ == "__main__":
    body = 37
    print(format_temperature(body, "C"), "=", format_temperature(celsius_to_fahrenheit(body), "F"))
