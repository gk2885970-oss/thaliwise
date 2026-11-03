"""AI / NLP helpers with fully functional rule-based fallback (no API required)."""

from typing import Dict, Any, List, Optional
import re


def parse_natural_language(text: str) -> Dict[str, Any]:
    """
    Extract household size, budget, diet type from free text.
    Rule-based; works offline.
    """
    text_l = text.lower().strip()
    result: Dict[str, Any] = {
        "adults": 2,
        "children": 0,
        "budget": 1500.0,
        "diet_type": "vegetarian",
        "raw": text,
        "parsed_ok": False,
    }

    # Budget: look for numbers near rupee / rs / budget
    budget_match = re.search(
        r"(?:rs\.?|₹|rupees?|budget|spend)\s*[:=]?\s*(\d[\d,]*)",
        text_l,
    )
    if not budget_match:
        budget_match = re.search(r"(\d[\d,]*)\s*(?:rs\.?|₹|rupees?)", text_l)
    if budget_match:
        result["budget"] = float(budget_match.group(1).replace(",", ""))
        result["parsed_ok"] = True

    # Family size
    fam = re.search(r"(?:family of|members?|people|persons?)\s*(\d+)", text_l)
    if fam:
        n = int(fam.group(1))
        result["adults"] = max(1, n - 1) if n > 1 else 1
        result["children"] = max(0, n - result["adults"])
        result["parsed_ok"] = True
    else:
        adults_m = re.search(r"(\d+)\s*adults?", text_l)
        child_m = re.search(r"(\d+)\s*(?:child|children|kids?)", text_l)
        if adults_m:
            result["adults"] = int(adults_m.group(1))
            result["parsed_ok"] = True
        if child_m:
            result["children"] = int(child_m.group(1))
            result["parsed_ok"] = True

    # Diet
    if any(w in text_l for w in ["vegan", "plant-based", "no dairy"]):
        result["diet_type"] = "vegan"
        result["parsed_ok"] = True
    elif any(w in text_l for w in ["non-veg", "non veg", "chicken", "meat", "egg and meat"]):
        result["diet_type"] = "non-vegetarian"
        result["parsed_ok"] = True
    elif any(w in text_l for w in ["egg", "eggitarian"]):
        result["diet_type"] = "eggitarian"
        result["parsed_ok"] = True
    elif any(w in text_l for w in ["veg", "vegetarian"]):
        result["diet_type"] = "vegetarian"
        result["parsed_ok"] = True

    return result


def explain_basket(
    result: Dict[str, Any],
    daily_targets: Dict[str, float],
    language: str = "en",
) -> str:
    """Generate a plain-language explanation of the optimization result."""
    status = result.get("status", "")
    cost = result.get("total_cost", 0)
    budget_rem = result.get("budget_remaining", 0)
    adeq = result.get("adequacy", {})
    basket = result.get("basket", [])

    if language == "hi":
        return _explain_hi(result, daily_targets)

    lines = []
    if status == "optimal":
        lines.append(
            f"Great news! We found a weekly food basket costing ₹{cost:.0f} that meets your "
            f"family's calorie, protein and iron targets."
        )
        if budget_rem > 0:
            lines.append(f"You still have about ₹{budget_rem:.0f} remaining in the budget.")
    elif status == "budget_insufficient":
        extra = result.get("extra_budget_needed", 0)
        lines.append(
            f"Your current budget cannot fully meet all three nutrition targets. "
            f"The lowest-cost way to meet them would need roughly ₹{extra:.0f} more."
        )
        lines.append(
            "Below is the nutrition-complete basket (over budget). You can raise the budget "
            "or accept lower nutrient levels."
        )
    else:
        lines.append(result.get("message", "Could not find a feasible plan."))

    if basket:
        top = basket[:3]
        names = ", ".join(b["name_en"] for b in top)
        lines.append(f"The largest cost items are: {names}.")
        lines.append(
            f"Nutrition achievement — Calories: {adeq.get('calories', 0):.0f}%, "
            f"Protein: {adeq.get('protein', 0):.0f}%, Iron: {adeq.get('iron', 0):.0f}%."
        )

    lines.append(
        "This is general nutrition planning based on ICMR-NIN reference values and sample "
        "market prices. It is not medical advice."
    )
    return " ".join(lines)


def _explain_hi(result: Dict[str, Any], daily_targets: Dict[str, float]) -> str:
    status = result.get("status", "")
    cost = result.get("total_cost", 0)
    adeq = result.get("adequacy", {})
    if status == "optimal":
        return (
            f"बढ़िया! हमें ₹{cost:.0f} की साप्ताहिक टोकरी मिली जो आपके परिवार की "
            f"कैलोरी, प्रोटीन और आयरन की जरूरत पूरी करती है। "
            f"कैलोरी: {adeq.get('calories', 0):.0f}%, प्रोटीन: {adeq.get('protein', 0):.0f}%, "
            f"आयरन: {adeq.get('iron', 0):.0f}%. यह सामान्य पोषण योजना है, चिकित्सीय सलाह नहीं।"
        )
    return (
        f"वर्तमान बजट में सभी पोषण लक्ष्य पूरे नहीं हो पा रहे। "
        f"अनुमानित अतिरिक्त राशि लगभग ₹{result.get('extra_budget_needed', 0):.0f} है।"
    )


def match_food_name(query: str, foods_df) -> Optional[str]:
    """Simple fuzzy match of local name to food_id."""
    q = query.lower().strip()
    for _, row in foods_df.iterrows():
        if q in str(row["name_en"]).lower() or q in str(row.get("name_hi", "")).lower():
            return row["food_id"]
        # common aliases
        aliases = {
            "toor": "F007",
            "arhar": "F007",
            "masoor": "F008",
            "moong": "F009",
            "chana": "F006",
            "rajma": "F011",
            "palak": "F017",
            "atta": "F002",
            "chawal": "F001",
        }
        if q in aliases:
            return aliases[q]
    return None
