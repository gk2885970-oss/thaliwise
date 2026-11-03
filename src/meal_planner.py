"""Generate illustrative 7-day meal ideas from the optimized basket."""

from typing import List, Dict, Any
import random


# Simple template meals that map to common categories
MEAL_TEMPLATES = {
    "breakfast": [
        {"name": "Poha / Upma style", "uses": ["Cereals", "Vegetables", "Nuts_Seeds"]},
        {"name": "Roti + leftover sabzi", "uses": ["Cereals", "Vegetables"]},
        {"name": "Milk + banana / fruit", "uses": ["Dairy", "Fruits"]},
        {"name": "Besan chilla / omelette style", "uses": ["Pulses", "Eggs", "Vegetables"]},
        {"name": "Dalia / porridge", "uses": ["Cereals", "Dairy", "Nuts_Seeds"]},
    ],
    "lunch": [
        {"name": "Dal + rice + sabzi", "uses": ["Pulses", "Cereals", "Vegetables"]},
        {"name": "Roti + dal + salad", "uses": ["Cereals", "Pulses", "Vegetables"]},
        {"name": "Khichdi + curd", "uses": ["Cereals", "Pulses", "Dairy"]},
        {"name": "Rajma / chole + rice", "uses": ["Pulses", "Cereals"]},
        {"name": "Vegetable rice + raita", "uses": ["Cereals", "Vegetables", "Dairy"]},
    ],
    "dinner": [
        {"name": "Roti + sabzi + dal", "uses": ["Cereals", "Vegetables", "Pulses"]},
        {"name": "Light khichdi or soup + roti", "uses": ["Cereals", "Vegetables"]},
        {"name": "Paneer / tofu sabzi + roti", "uses": ["Dairy", "Pulses", "Cereals", "Vegetables"]},
        {"name": "Egg curry + rice (if allowed)", "uses": ["Eggs", "Cereals", "Vegetables"]},
        {"name": "Mixed vegetable + roti + curd", "uses": ["Vegetables", "Cereals", "Dairy"]},
    ],
    "snack": [
        {"name": "Fruit / banana", "uses": ["Fruits"]},
        {"name": "Roasted chana / peanuts", "uses": ["Pulses", "Nuts_Seeds"]},
        {"name": "Curd / buttermilk", "uses": ["Dairy"]},
        {"name": "Vegetable sticks", "uses": ["Vegetables"]},
    ],
}


def generate_meal_plan(basket: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
    """Create a simple illustrative weekly meal plan using foods present in the basket."""
    if not basket:
        return []

    categories_present = set(item["category"] for item in basket)
    names_by_cat: Dict[str, List[str]] = {}
    for item in basket:
        names_by_cat.setdefault(item["category"], []).append(item["name_en"])

    plan = []
    for day in range(1, days + 1):
        day_meals = {"day": day, "meals": {}}
        for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
            candidates = MEAL_TEMPLATES[meal_type]
            # Prefer templates whose required categories are largely available
            scored = []
            for t in candidates:
                overlap = len(set(t["uses"]) & categories_present)
                scored.append((overlap, t))
            scored.sort(key=lambda x: -x[0])
            chosen = scored[0][1] if scored else candidates[0]

            # Build a short description with actual foods
            used_foods = []
            for cat in chosen["uses"]:
                if cat in names_by_cat and names_by_cat[cat]:
                    used_foods.append(names_by_cat[cat][0])
            desc = chosen["name"]
            if used_foods:
                desc += " (using: " + ", ".join(used_foods[:3]) + ")"
            day_meals["meals"][meal_type] = {
                "title": chosen["name"],
                "description": desc,
                "note": "Illustrative suggestion only — adjust quantities to your family's taste and the shopping list.",
            }
        plan.append(day_meals)
    return plan
