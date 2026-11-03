"""Nutrition calculation tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.household_profile import HouseholdProfile, Member, calculate_daily_targets
from src.data_loader import load_nutrition_targets


def test_single_adult():
    targets_df = load_nutrition_targets()
    profile = HouseholdProfile(
        members=[Member("18-59", "Male", "Adult", 1)],
        weekly_budget=1000,
    )
    daily = calculate_daily_targets(profile, targets_df)
    assert 1800 <= daily["calories_kcal"] <= 2800
    assert 40 <= daily["protein_g"] <= 70
    assert 15 <= daily["iron_mg"] <= 30


def test_scaling():
    targets_df = load_nutrition_targets()
    p1 = HouseholdProfile(members=[Member("18-59", "Female", "Adult", 1)])
    p2 = HouseholdProfile(members=[Member("18-59", "Female", "Adult", 2)])
    d1 = calculate_daily_targets(p1, targets_df)
    d2 = calculate_daily_targets(p2, targets_df)
    assert abs(d2["calories_kcal"] - 2 * d1["calories_kcal"]) < 1e-6


if __name__ == "__main__":
    test_single_adult()
    test_scaling()
    print("Nutrition tests passed.")
