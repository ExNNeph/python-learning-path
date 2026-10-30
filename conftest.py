"""Shared pytest setup for every assignment.

Each assignment test asks for the `ex` fixture: your `exercise.py` from the
same folder as the test, loaded fresh for every test.

With the environment variable PLP_SOLUTIONS=1 (CI sets it) the fixture loads
the template solution from the mirrored folder under `solutions/` instead.
That way the same tests check your work and prove the solutions correct.
"""

import importlib.util
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).parent


def exercise_path(test_dir: Path) -> Path:
    if os.environ.get("PLP_SOLUTIONS") == "1":
        return ROOT / "solutions" / test_dir.relative_to(ROOT) / "exercise.py"
    return test_dir / "exercise.py"


@pytest.fixture
def ex(request):
    path = exercise_path(request.path.parent)
    name = "exercise_" + "_".join(path.parent.relative_to(ROOT).parts).replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
