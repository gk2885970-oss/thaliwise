"""Household profile and daily nutrition target calculation."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import pandas as pd


@dataclass
class Member:
    age_group: str  # e.g. "18-59", "1-3", "10-12"
    sex: str  # "Male", "Female", "Any"
    category: str = "Adult"  # Adult, Child, Adolescent, Pregnant, Lactating
    count: int = 1


@dataclass
class HouseholdProfile:
    members: List[Member] = field(default_factory=list)
    diet_type: str = "vegetarian"  # vegetarian, non-vegetarian, vegan, eggitarian
    exclusions: List[str] = field(default_factory=list)  # food_ids or names
    locality: str = "Delhi/NCR"
    weekly_budget: float = 1500.0
    existing_pantry: Dict[str, float] = field(default_factory=dict)  # food_id -> grams available

    def total_members(self) -> int:
        return sum(m.count for m in self.members)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "members": [
                {
                    "age_group": m.age_group,
                    "sex": m.sex,
                    "category": m.category,
                    "count": m.count,
                }
                for m in self.members
            ],
            "diet_type": self.diet_type,
            "exclusions": self.exclusions,
            "locality": self.locality,
            "weekly_budget": self.weekly_budget,
        }


def calculate_daily_targets(
    profile: HouseholdProfile, targets_df: pd.DataFrame
) -> Dict[str, float]:
    """Sum daily calorie, protein, iron targets for the household."""
    total_cal = 0.0
    total_prot = 0.0
    total_iron = 0.0
    details = []

    for m in profile.members:
        # Find best matching row
        mask = (targets_df["category"] == m.category) & (
            targets_df["age_group"] == m.age_group
        )
        if m.sex != "Any":
            mask = mask & (targets_df["sex"] == m.sex)
        rows = targets_df[mask]
        if rows.empty:
            # Fallback to Adult Male/Female or Child Any
            if m.category == "Child":
                rows = targets_df[
                    (targets_df["category"] == "Child")
                    & (targets_df["age_group"] == "4-6")
                ]
            else:
                rows = targets_df[
                    (targets_df["category"] == "Adult")
                    & (targets_df["age_group"] == "18-59")
                    & (targets_df["sex"] == ("Male" if m.sex != "Female" else "Female"))
                ]
        if rows.empty:
            # Hard fallback
            cal, prot, iron = 2000.0, 50.0, 20.0
        else:
            row = rows.iloc[0]
            cal = float(row["calories_kcal"])
            prot = float(row["protein_g"])
            iron = float(row["iron_mg"])

        total_cal += cal * m.count
        total_prot += prot * m.count
        total_iron += iron * m.count
        details.append(
            {
                "desc": f"{m.count}× {m.category} {m.age_group} {m.sex}",
                "cal": cal,
                "prot": prot,
                "iron": iron,
            }
        )

    return {
        "calories_kcal": total_cal,
        "protein_g": total_prot,
        "iron_mg": total_iron,
        "details": details,
        "source": "ICMR-NIN 2020 approximate RDAs (illustrative for prototype)",
    }
