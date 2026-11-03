"""Validate food dataset integrity."""

import pandas as pd
from typing import List, Tuple


def validate_foods(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    required = [
        "food_id",
        "name_en",
        "category",
        "calories_kcal_per_100g",
        "protein_g_per_100g",
        "iron_mg_per_100g",
        "price_inr_per_kg",
        "min_qty_g_week",
        "max_qty_g_week",
    ]
    for col in required:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if df["food_id"].duplicated().any():
        errors.append("Duplicate food_id values found")

    if (df["price_inr_per_kg"] <= 0).any():
        errors.append("Non-positive prices found")

    for col in ["calories_kcal_per_100g", "protein_g_per_100g", "iron_mg_per_100g"]:
        if df[col].isna().any():
            errors.append(f"Missing nutrient values in {col}")
        if (df[col] < 0).any():
            errors.append(f"Negative values in {col}")

    if (df["min_qty_g_week"] > df["max_qty_g_week"]).any():
        errors.append("min_qty > max_qty for some foods")

    return len(errors) == 0, errors
