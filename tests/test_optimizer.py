"""Unit tests for the linear programming optimizer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.data_loader import load_foods
from src.optimizer import optimize_diet, filter_foods_for_diet
from src.household_profile import HouseholdProfile, Member, calculate_daily_targets
from src.data_loader import load_nutrition_targets


def test_load_foods():
    foods = load_foods()
    assert len(foods) >= 40
    assert "calories_kcal_per_100g" in foods.columns


def test_filter_vegetarian():
    foods = load_foods()
    veg = filter_foods_for_diet(foods, "vegetarian", [])
    assert all(veg["is_vegetarian"] == True)
    nonveg_ids = set(foods[foods["is_vegetarian"] == False]["food_id"])
    assert not any(fid in nonveg_ids for fid in veg["food_id"])


def test_simple_optimization():
    foods = load_foods()
    targets = {"calories_kcal": 2000.0, "protein_g": 50.0, "iron_mg": 20.0}
    result = optimize_diet(foods, targets, weekly_budget=2000.0, diet_type="vegetarian")
    assert result["status"] in ("optimal", "budget_insufficient")
    if result["status"] == "optimal":
        assert result["total_cost"] <= 2000.0 + 1e-3
        assert result["adequacy"]["calories"] >= 99.0
        assert result["adequacy"]["protein"] >= 99.0
        assert result["adequacy"]["iron"] >= 99.0
        assert len(result["basket"]) >= 1


def test_low_budget_infeasible_or_gap():
    foods = load_foods()
    targets = {"calories_kcal": 4000.0, "protein_g": 120.0, "iron_mg": 50.0}
    result = optimize_diet(foods, targets, weekly_budget=200.0, diet_type="vegetarian")
    assert result["status"] in ("budget_insufficient", "infeasible")


def test_household_targets():
    targets_df = load_nutrition_targets()
    profile = HouseholdProfile(
        members=[
            Member(age_group="18-59", sex="Female", category="Adult", count=1),
            Member(age_group="18-59", sex="Male", category="Adult", count=1),
            Member(age_group="4-6", sex="Any", category="Child", count=2),
        ],
        diet_type="vegetarian",
        weekly_budget=1800,
    )
    daily = calculate_daily_targets(profile, targets_df)
    assert daily["calories_kcal"] > 4000
    assert daily["protein_g"] > 100
    assert daily["iron_mg"] > 40


if __name__ == "__main__":
    test_load_foods()
    test_filter_vegetarian()
    test_simple_optimization()
    test_low_budget_infeasible_or_gap()
    test_household_targets()
    print("All optimizer tests passed.")
