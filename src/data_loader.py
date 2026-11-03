"""Load and prepare food and nutrition target datasets."""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_foods(csv_path: Path | None = None) -> pd.DataFrame:
    path = csv_path or DATA_DIR / "foods.csv"
    df = pd.read_csv(path)
    # Ensure numeric types
    for col in [
        "calories_kcal_per_100g",
        "protein_g_per_100g",
        "iron_mg_per_100g",
        "price_inr_per_kg",
        "min_qty_g_week",
        "max_qty_g_week",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["is_vegetarian"] = df["is_vegetarian"].astype(bool)
    df["is_vegan"] = df["is_vegan"].astype(bool)
    # Price is per kg or per litre; for eggs we treat "piece" specially later
    return df


def load_nutrition_targets(csv_path: Path | None = None) -> pd.DataFrame:
    path = csv_path or DATA_DIR / "nutrition_targets.csv"
    df = pd.read_csv(path)
    for col in ["calories_kcal", "protein_g", "iron_mg"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_food_by_id(foods: pd.DataFrame, food_id: str) -> pd.Series | None:
    row = foods[foods["food_id"] == food_id]
    if row.empty:
        return None
    return row.iloc[0]
