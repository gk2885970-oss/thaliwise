"""Budget vs nutrition trade-off helpers."""

from typing import Dict, Any, List
import pandas as pd
from .optimizer import optimize_diet, filter_foods_for_diet
import pulp


def analyze_budget_tradeoff(
    foods: pd.DataFrame,
    daily_targets: Dict[str, float],
    base_budget: float,
    diet_type: str = "vegetarian",
    exclusions: List[str] | None = None,
    budget_steps: List[float] | None = None,
) -> Dict[str, Any]:
    """Run optimizer at several budget levels and report achieved nutrition."""
    exclusions = exclusions or []
    if budget_steps is None:
        budget_steps = [
            base_budget * 0.7,
            base_budget * 0.85,
            base_budget,
            base_budget * 1.15,
            base_budget * 1.3,
            base_budget * 1.5,
        ]

    results = []
    for b in budget_steps:
        b = max(100.0, round(b, 0))
        res = optimize_diet(
            foods, daily_targets, b, diet_type=diet_type, exclusions=exclusions
        )
        results.append(
            {
                "budget": b,
                "status": res["status"],
                "total_cost": res.get("total_cost", 0),
                "adequacy_calories": res["adequacy"].get("calories", 0),
                "adequacy_protein": res["adequacy"].get("protein", 0),
                "adequacy_iron": res["adequacy"].get("iron", 0),
                "extra_needed": res.get("extra_budget_needed"),
            }
        )
    return {"base_budget": base_budget, "scenarios": results}
