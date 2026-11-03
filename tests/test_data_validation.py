"""Data validation tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_foods
from src.data_validation import validate_foods


def test_foods_valid():
    foods = load_foods()
    ok, errors = validate_foods(foods)
    assert ok, f"Validation errors: {errors}"


if __name__ == "__main__":
    test_foods_valid()
    print("Data validation tests passed.")
