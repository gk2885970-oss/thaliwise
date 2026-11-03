"""Suggest affordable nutrient-similar food substitutions."""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


def suggest_substitutes(
    foods: pd.DataFrame,
    original_food_id: str,
    current_basket: List[Dict[str, Any]],
    diet_type: str = "vegetarian",
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """Find cheaper or similar foods based on nutrient density and price."""
    orig = foods[foods["food_id"] == original_food_id]
    if orig.empty:
        return []
    orig = orig.iloc[0]

    # Filter candidates
    candidates = foods[foods["food_id"] != original_food_id].copy()
    if diet_type == "vegan":
        candidates = candidates[candidates["is_vegan"] == True]
    elif diet_type == "vegetarian":
        candidates = candidates[candidates["is_vegetarian"] == True]

    if candidates.empty:
        return []

    # Simple similarity: weighted nutrient vector + price
    def score(row):
        # Prefer same category
        cat_bonus = 2.0 if row["category"] == orig["category"] else 0.0
        # Nutrient distance (lower better)
        d_cal = abs(row["calories_kcal_per_100g"] - orig["calories_kcal_per_100g"]) / 100.0
        d_prot = abs(row["protein_g_per_100g"] - orig["protein_g_per_100g"]) / 10.0
        d_iron = abs(row["iron_mg_per_100g"] - orig["iron_mg_per_100g"]) / 2.0
        nutrient_dist = d_cal + d_prot + d_iron
        # Prefer lower price
        price_ratio = row["price_inr_per_kg"] / max(orig["price_inr_per_kg"], 1)
        # Combined: lower is better
        return nutrient_dist + 0.5 * price_ratio - cat_bonus

    candidates["score"] = candidates.apply(score, axis=1)
    candidates = candidates.sort_values("score").head(top_n)

    suggestions = []
    for _, row in candidates.iterrows():
        price_diff = row["price_inr_per_kg"] - orig["price_inr_per_kg"]
        suggestions.append(
            {
                "food_id": row["food_id"],
                "name_en": row["name_en"],
                "name_hi": row.get("name_hi", ""),
                "category": row["category"],
                "price_per_kg": row["price_inr_per_kg"],
                "price_diff_per_kg": round(price_diff, 1),
                "calories_per_100g": row["calories_kcal_per_100g"],
                "protein_per_100g": row["protein_g_per_100g"],
                "iron_per_100g": row["iron_mg_per_100g"],
                "reason": (
                    "Same category, similar nutrients"
                    if row["category"] == orig["category"]
                    else "Nutrient-similar alternative"
                ),
            }
        )
    return suggestions
