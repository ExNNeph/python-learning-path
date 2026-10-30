"""Tests for assignment 03. Run: pytest beginner/03-numbers-and-strings/assignments/03-temperature-converter -v"""

import pytest


@pytest.mark.parametrize("celsius, expected", [(0, 32.0), (100, 212.0), (-40, -40.0), (37.5, 99.5), (21.3, 70.3)])
def test_celsius_to_fahrenheit(ex, celsius, expected):
    assert ex.celsius_to_fahrenheit(celsius) == expected


@pytest.mark.parametrize("fahrenheit, expected", [(32, 0.0), (212, 100.0), (-40, -40.0), (0, -17.8), (98.6, 37.0)])
def test_fahrenheit_to_celsius(ex, fahrenheit, expected):
    assert ex.fahrenheit_to_celsius(fahrenheit) == expected


@pytest.mark.parametrize("celsius, expected", [(0, 273.15), (-273.15, 0.0), (0.1, 273.25), (100, 373.15)])
def test_celsius_to_kelvin(ex, celsius, expected):
    assert ex.celsius_to_kelvin(celsius) == expected


@pytest.mark.parametrize(
    "value, unit, expected",
    [(21.456, "C", "21.5 °C"), (-40, "F", "-40.0 °F"), (0, "K", "0.0 °K"), (99.94, "F", "99.9 °F")],
)
def test_format_temperature(ex, value, unit, expected):
    assert ex.format_temperature(value, unit) == expected
