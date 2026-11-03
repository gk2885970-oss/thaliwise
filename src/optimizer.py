"""Linear programming diet cost minimizer using PuLP."""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import pulp


def filter_foods_for_diet(
    foods: pd.DataFrame,
    diet_type: str,
    exclusions: List[str],
) -> pd.DataFrame:
    df = foods.copy()
    if diet_type == "vegan":
        df = df[df["is_vegan"] == True]
    elif diet_type == "vegetarian":
        df = df[df["is_vegetarian"] == True]
    elif diet_type == "eggitarian":
        # Allow eggs + vegetarian
        df = df[(df["is_vegetarian"] == True) | (df["food_id"] == "F031")]
    # non-vegetarian: all

    # Exclusions by food_id or name
    excl_lower = [e.lower().strip() for e in exclusions]
    mask = ~df["food_id"].str.lower().isin(excl_lower)
    mask &= ~df["name_en"].str.lower().isin(excl_lower)
    mask &= ~df["name_hi"].fillna("").str.lower().isin(excl_lower)
    df = df[mask]
    return df.reset_index(drop=True)


def optimize_diet(
    foods: pd.DataFrame,
    daily_targets: Dict[str, float],
    weekly_budget: float,
    diet_type: str = "vegetarian",
    exclusions: Optional[List[str]] = None,
    pantry: Optional[Dict[str, float]] = None,
    force_min_variety: int = 4,
) -> Dict[str, Any]:
    """
    Minimize weekly cost subject to nutrition and budget constraints.

    Returns dict with status, basket, totals, adequacy, messages.
    """
    exclusions = exclusions or []
    pantry = pantry or {}

    df = filter_foods_for_diet(foods, diet_type, exclusions)
    if df.empty:
        return {
            "status": "infeasible",
            "message": "No foods available after dietary filters.",
            "basket": [],
            "total_cost": 0.0,
            "budget_remaining": weekly_budget,
            "nutrients": {"calories": 0, "protein": 0, "iron": 0},
            "adequacy": {"calories": 0, "protein": 0, "iron": 0},
            "weekly_targets": {
                "calories": daily_targets["calories_kcal"] * 7,
                "protein": daily_targets["protein_g"] * 7,
                "iron": daily_targets["iron_mg"] * 7,
            },
        }

    # Weekly targets
    weekly_cal = daily_targets["calories_kcal"] * 7
    weekly_prot = daily_targets["protein_g"] * 7
    weekly_iron = daily_targets["iron_mg"] * 7

    # Decision variables: grams per week for each food
    # For eggs (piece unit) we still use grams; assume 50 g per egg
    # For liquids (litre) price is per litre ≈ per kg for density ~1

    prob = pulp.LpProblem("ThaliWise_Diet", pulp.LpMinimize)

    food_ids = df["food_id"].tolist()
    # Compatible with PuLP 2.x and 4.x (dicts API removed in some 4.x builds)
    
    qty = {}
    qty = pulp.LpVariable.dicts(
    "qty_g", food_ids, lowBound=0, cat="Continuous"
)

    # Objective: minimize cost
    # cost = (price_per_kg / 1000) * grams
    costs = []
    for _, row in df.iterrows():
        fid = row["food_id"]
        price_per_g = row["price_inr_per_kg"] / 1000.0
        # Eggs special: price is per piece (~50g), so effective price_per_g = 6/50
        if row["unit"] == "piece":
            price_per_g = row["price_inr_per_kg"] / 50.0  # price_inr_per_kg holds price-per-piece
        costs.append(price_per_g * qty[fid])
    prob += pulp.lpSum(costs), "Total_Cost"

    # Nutrient constraints (per 100g values)
    cal_expr = []
    prot_expr = []
    iron_expr = []
    for _, row in df.iterrows():
        fid = row["food_id"]
        g = qty[fid]
        cal_expr.append((row["calories_kcal_per_100g"] / 100.0) * g)
        prot_expr.append((row["protein_g_per_100g"] / 100.0) * g)
        iron_expr.append((row["iron_mg_per_100g"] / 100.0) * g)

    prob += pulp.lpSum(cal_expr) >= weekly_cal, "Min_Calories"
    prob += pulp.lpSum(prot_expr) >= weekly_prot, "Min_Protein"
    prob += pulp.lpSum(iron_expr) >= weekly_iron, "Min_Iron"

    # Budget constraint
    prob += pulp.lpSum(costs) <= weekly_budget, "Budget"

    # Quantity bounds (practical limits)
    for _, row in df.iterrows():
        fid = row["food_id"]
        max_q = float(row["max_qty_g_week"])
        prob += qty[fid] <= max_q, f"Max_{fid}"

    # Encourage basic variety: require some pulses and some vegetables
    # (soft practicality constraints for a realistic household basket)
    pulse_ids = df[df["category"] == "Pulses"]["food_id"].tolist()
    veg_ids = df[df["category"] == "Vegetables"]["food_id"].tolist()
    cereal_ids = df[df["category"] == "Cereals"]["food_id"].tolist()
    if pulse_ids:
        prob += pulp.lpSum(qty[fid] for fid in pulse_ids) >= 400, "Min_Pulses_g"
    if veg_ids:
        prob += pulp.lpSum(qty[fid] for fid in veg_ids) >= 1000, "Min_Veg_g"
    if cereal_ids:
        # Cap total cereals to avoid extreme mono-diets when budget is tight
        prob += pulp.lpSum(qty[fid] for fid in cereal_ids) <= 12000, "Max_Cereals_g"

    # Solve
    try:
        status = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))
    except Exception:
        status = prob.solve(msg=0)

    result: Dict[str, Any] = {
        "status": pulp.LpStatus[status],
        "message": "",
        "basket": [],
        "total_cost": 0.0,
        "budget_remaining": weekly_budget,
        "nutrients": {"calories": 0.0, "protein": 0.0, "iron": 0.0},
        "adequacy": {"calories": 0.0, "protein": 0.0, "iron": 0.0},
        "weekly_targets": {
            "calories": weekly_cal,
            "protein": weekly_prot,
            "iron": weekly_iron,
        },
        "solver_status": pulp.LpStatus[status],
    }

    if status != pulp.LpStatusOptimal and status != pulp.LpStatusNotSolved:
        # Try relaxed problem without budget to find min cost for nutrition
        return _handle_infeasible(
            df, weekly_cal, weekly_prot, weekly_iron, weekly_budget, diet_type, exclusions
        )

    # Extract solution
    basket = []
    total_cost = 0.0
    tot_cal = 0.0
    tot_prot = 0.0
    tot_iron = 0.0

    for _, row in df.iterrows():
        fid = row["food_id"]
        q = pulp.value(qty[fid]) or 0.0
        if q < 1.0:  # ignore tiny
            continue
        price_per_g = row["price_inr_per_kg"] / 1000.0
        if row["unit"] == "piece":
            price_per_g = row["price_inr_per_kg"] / 50.0
        cost = price_per_g * q
        cal = (row["calories_kcal_per_100g"] / 100.0) * q
        prot = (row["protein_g_per_100g"] / 100.0) * q
        iron = (row["iron_mg_per_100g"] / 100.0) * q

        basket.append(
            {
                "food_id": fid,
                "name_en": row["name_en"],
                "name_hi": row.get("name_hi", ""),
                "category": row["category"],
                "quantity_g": round(q, 1),
                "quantity_display": _format_qty(q, row["unit"]),
                "unit": row["unit"],
                "price_per_kg": row["price_inr_per_kg"],
                "cost": round(cost, 2),
                "calories": round(cal, 1),
                "protein": round(prot, 1),
                "iron": round(iron, 2),
            }
        )
        total_cost += cost
        tot_cal += cal
        tot_prot += prot
        tot_iron += iron

    basket.sort(key=lambda x: -x["cost"])

    result["basket"] = basket
    result["total_cost"] = round(total_cost, 2)
    result["budget_remaining"] = round(weekly_budget - total_cost, 2)
    result["nutrients"] = {
        "calories": round(tot_cal, 1),
        "protein": round(tot_prot, 1),
        "iron": round(tot_iron, 2),
    }
    result["adequacy"] = {
        "calories": round(100 * tot_cal / weekly_cal, 1) if weekly_cal > 0 else 0,
        "protein": round(100 * tot_prot / weekly_prot, 1) if weekly_prot > 0 else 0,
        "iron": round(100 * tot_iron / weekly_iron, 1) if weekly_iron > 0 else 0,
    }
    result["status"] = "optimal"
    result["message"] = "Optimal low-cost basket found that meets nutrition targets within budget."
    return result


def _format_qty(grams: float, unit: str) -> str:
    if unit == "piece":
        eggs = grams / 50.0
        return f"{eggs:.0f} eggs (~{grams:.0f} g)"
    if unit == "litre":
        return f"{grams/1000:.2f} L"
    if grams >= 1000:
        return f"{grams/1000:.2f} kg"
    return f"{grams:.0f} g"


def _handle_infeasible(
    df: pd.DataFrame,
    weekly_cal: float,
    weekly_prot: float,
    weekly_iron: float,
    weekly_budget: float,
    diet_type: str,
    exclusions: List[str],
) -> Dict[str, Any]:
    """Solve without budget to get minimum cost for nutrition, then report gap."""
    prob = pulp.LpProblem("ThaliWise_MinCost", pulp.LpMinimize)
    food_ids = df["food_id"].tolist()
    qty = pulp.LpVariable.dicts(
    "qty_g", food_ids, lowBound=0, cat="Continuous"
)

    costs = []
    for _, row in df.iterrows():
        fid = row["food_id"]
        price_per_g = row["price_inr_per_kg"] / 1000.0
        if row["unit"] == "piece":
            price_per_g = row["price_inr_per_kg"] / 50.0
        costs.append(price_per_g * qty[fid])
    prob += pulp.lpSum(costs)

    cal_expr, prot_expr, iron_expr = [], [], []
    for _, row in df.iterrows():
        fid = row["food_id"]
        g = qty[fid]
        cal_expr.append((row["calories_kcal_per_100g"] / 100.0) * g)
        prot_expr.append((row["protein_g_per_100g"] / 100.0) * g)
        iron_expr.append((row["iron_mg_per_100g"] / 100.0) * g)
        prob += qty[fid] <= float(row["max_qty_g_week"])

    prob += pulp.lpSum(cal_expr) >= weekly_cal
    prob += pulp.lpSum(prot_expr) >= weekly_prot
    prob += pulp.lpSum(iron_expr) >= weekly_iron

    try:
        status = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=20))
    except Exception:
        status = prob.solve(msg=0)
    if status != pulp.LpStatusOptimal:
        return {
            "status": "infeasible",
            "message": (
                "Cannot meet nutrition targets with available foods under current "
                "dietary restrictions. Try relaxing exclusions or increasing variety of foods."
            ),
            "basket": [],
            "total_cost": 0.0,
            "budget_remaining": weekly_budget,
            "nutrients": {"calories": 0, "protein": 0, "iron": 0},
            "adequacy": {"calories": 0, "protein": 0, "iron": 0},
            "weekly_targets": {
                "calories": weekly_cal,
                "protein": weekly_prot,
                "iron": weekly_iron,
            },
            "min_cost_for_nutrition": None,
            "extra_budget_needed": None,
        }

    min_cost = pulp.value(prob.objective) or 0.0
    basket = []
    tot_cal = tot_prot = tot_iron = 0.0
    for _, row in df.iterrows():
        fid = row["food_id"]
        q = pulp.value(qty[fid]) or 0.0
        if q < 1:
            continue
        price_per_g = row["price_inr_per_kg"] / 1000.0
        if row["unit"] == "piece":
            price_per_g = row["price_inr_per_kg"] / 50.0
        cost = price_per_g * q
        cal = (row["calories_kcal_per_100g"] / 100.0) * q
        prot = (row["protein_g_per_100g"] / 100.0) * q
        iron = (row["iron_mg_per_100g"] / 100.0) * q
        basket.append(
            {
                "food_id": fid,
                "name_en": row["name_en"],
                "name_hi": row.get("name_hi", ""),
                "category": row["category"],
                "quantity_g": round(q, 1),
                "quantity_display": _format_qty(q, row["unit"]),
                "unit": row["unit"],
                "price_per_kg": row["price_inr_per_kg"],
                "cost": round(cost, 2),
                "calories": round(cal, 1),
                "protein": round(prot, 1),
                "iron": round(iron, 2),
            }
        )
        tot_cal += cal
        tot_prot += prot
        tot_iron += iron

    basket.sort(key=lambda x: -x["cost"])
    extra = max(0.0, min_cost - weekly_budget)

    return {
        "status": "budget_insufficient",
        "message": (
            f"Budget of ₹{weekly_budget:.0f} is insufficient to meet all nutrition targets. "
            f"Minimum cost to meet targets is approximately ₹{min_cost:.0f}. "
            f"You need about ₹{extra:.0f} more, or accept lower nutrient levels."
        ),
        "basket": basket,  # the nutrition-feasible but over-budget basket
        "total_cost": round(min_cost, 2),
        "budget_remaining": round(weekly_budget - min_cost, 2),
        "nutrients": {
            "calories": round(tot_cal, 1),
            "protein": round(tot_prot, 1),
            "iron": round(tot_iron, 2),
        },
        "adequacy": {
            "calories": 100.0,
            "protein": 100.0,
            "iron": 100.0,
        },
        "weekly_targets": {
            "calories": weekly_cal,
            "protein": weekly_prot,
            "iron": weekly_iron,
        },
        "min_cost_for_nutrition": round(min_cost, 2),
        "extra_budget_needed": round(extra, 2),
    }


def best_effort_under_budget(
    foods: pd.DataFrame,
    daily_targets: Dict[str, float],
    weekly_budget: float,
    diet_type: str = "vegetarian",
    exclusions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Maximize a weighted nutrient score subject to budget (fallback when full targets infeasible)."""
    exclusions = exclusions or []
    df = filter_foods_for_diet(foods, diet_type, exclusions)
    if df.empty:
        return optimize_diet(foods, daily_targets, weekly_budget, diet_type, exclusions)

    weekly_cal = daily_targets["calories_kcal"] * 7
    weekly_prot = daily_targets["protein_g"] * 7
    weekly_iron = daily_targets["iron_mg"] * 7

    # Weighted maximisation of min(achieved/target) style via soft objectives
    # Simpler: minimise cost of a scaled-down target or just run cost min with relaxed targets
    # For prototype we return the over-budget solution from _handle_infeasible
    return _handle_infeasible(
        df, weekly_cal, weekly_prot, weekly_iron, weekly_budget, diet_type, exclusions
    )
