"""Tests for assignment 03. Run: pytest professional/03-testing-like-a-professional/assignments/03-test-the-tests -v

These tests run YOUR tests (exercise.py): once against the real pricing.py, where they must pass,
and once against each mutant, a copy of pricing.py with one planted bug, where they must fail.
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

HERE = Path(__file__).parent
ROOT = HERE.parents[3]

# (id, original text, mutated text): each mutant changes exactly one place in pricing.py.
MUTANTS = [
    ("quantity-zero-allowed", "if item.quantity < 1:", "if item.quantity < 0:"),
    ("quantity-ignored", "sum(item.unit_price * item.quantity for", "sum(item.unit_price for"),
    ("save10-rounds-to-nearest", "return amount // 10", "return round(amount / 10)"),
    ("flat5-boundary", "500 if amount >= 2000 else 0", "500 if amount > 2000 else 0"),
    ("code-case-sensitive", "code = code.upper()", "code = code"),
    ("unknown-code-ignored", 'raise ValueError(f"unknown discount code: {code}")', "return 0"),
    ("shipping-boundary", "0 if amount >= 5000 else 495", "0 if amount > 5000 else 495"),
    ("shipping-before-discount", "convert(amount + shipping(amount),", "convert(amount + shipping(subtotal(items)),"),
    ("wrong-rate-lookup", "rates.get_rate(currency))", "rates.get_rate(currency.lower()))"),
    ("euro-rate-lookup", 'if currency == "EUR":\n', 'if currency == "EUR":\n        rates and rates.get_rate(currency)\n'),
]


def your_tests():
    if os.environ.get("PLP_SOLUTIONS") == "1":
        return ROOT / "solutions" / HERE.relative_to(ROOT) / "exercise.py"
    return HERE / "exercise.py"


def run_tests(pricing_source, workdir):
    """Run your tests against `pricing_source` in an isolated folder. True if they all passed."""
    workdir.mkdir()
    (workdir / "pricing.py").write_text(pricing_source, encoding="utf-8")
    (workdir / "test_yours.py").write_text(your_tests().read_text(encoding="utf-8"), encoding="utf-8")
    (workdir / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")       # keep the repo's settings out
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--import-mode=prepend"],
        cwd=workdir, capture_output=True, text=True, timeout=120,
    )
    return result.returncode, result.stdout


def results(tmp_root):
    """Run every variant (in parallel) and return {name: (exit code, output)}."""
    original = (HERE / "pricing.py").read_text(encoding="utf-8")
    variants = {"original": original}
    variants.update({name: original.replace(old, new, 1) for name, old, new in MUTANTS})
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {name: pool.submit(run_tests, source, Path(tmp_root) / name) for name, source in variants.items()}
    return {name: future.result() for name, future in futures.items()}


@pytest.fixture(scope="module")
def outcome(tmp_path_factory):
    """Computed once per module and shared by all tests below."""
    return results(tmp_path_factory.mktemp("mutants"))


def test_every_mutant_changes_pricing():
    original = (HERE / "pricing.py").read_text(encoding="utf-8")
    for name, old, new in MUTANTS:
        assert original.count(old) == 1, name


def test_your_tests_pass_on_the_real_code(outcome):
    code, output = outcome["original"]
    assert code != 5, "no tests found in exercise.py"
    assert code == 0, "your tests fail on the correct pricing.py:\n" + output


def test_you_wrote_enough_tests(outcome):
    code, output = outcome["original"]
    summary = output.strip().splitlines()[-1] if output.strip() else ""
    passed = int(summary.split()[0]) if summary.split()[1:2] == ["passed"] else 0
    assert passed >= 8, f"expected at least 8 passing tests, got: {summary!r}"


@pytest.mark.parametrize("mutant", [name for name, _, _ in MUTANTS])
def test_your_tests_catch_the_mutant(outcome, mutant):
    assert outcome["original"][0] == 0, "first make your tests pass on the real pricing.py"
    code, _ = outcome[mutant]
    assert code == 1, f"mutant {mutant!r} survived: no test failed. Which behaviour is not checked?"
