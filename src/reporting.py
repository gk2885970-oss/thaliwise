"""Export helpers."""

import pandas as pd
from typing import List, Dict, Any
from io import StringIO


def shopping_list_to_csv(basket: List[Dict[str, Any]]) -> str:
    if not basket:
        return "food,quantity,cost\n"
    rows = []
    for b in basket:
        rows.append(
            {
                "Food": b["name_en"],
                "Hindi": b.get("name_hi", ""),
                "Category": b["category"],
                "Quantity": b["quantity_display"],
                "Quantity_g": b["quantity_g"],
                "Cost_INR": b["cost"],
                "Calories": b["calories"],
                "Protein_g": b["protein"],
                "Iron_mg": b["iron"],
            }
        )
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)
