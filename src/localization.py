"""Simple English / Hindi string table for UI."""

STRINGS = {
    "en": {
        "app_title": "ThaliWise",
        "tagline": "Budget-first nutrition optimizer",
        "start": "Start planning",
        "household": "Household profile",
        "budget": "Weekly budget (₹)",
        "generate": "Generate nutrition plan",
        "shopping_list": "Weekly shopping list",
        "results": "Optimization results",
        "meals": "Sample meal ideas",
        "substitutes": "Food substitutions",
        "budget_vs_nutrition": "Budget vs nutrition",
        "ngo": "NGO / Group dashboard",
        "disclaimer": "General nutrition planning only — not medical advice.",
        "language": "Language",
    },
    "hi": {
        "app_title": "थालीवाइज़",
        "tagline": "बजट-प्रथम पोषण अनुकूलक",
        "start": "योजना शुरू करें",
        "household": "परिवार प्रोफ़ाइल",
        "budget": "साप्ताहिक बजट (₹)",
        "generate": "पोषण योजना बनाएं",
        "shopping_list": "साप्ताहिक खरीदारी सूची",
        "results": "अनुकूलन परिणाम",
        "meals": "नमूना भोजन सुझाव",
        "substitutes": "भोजन विकल्प",
        "budget_vs_nutrition": "बजट बनाम पोषण",
        "ngo": "एनजीओ / समूह डैशबोर्ड",
        "disclaimer": "केवल सामान्य पोषण योजना — चिकित्सीय सलाह नहीं।",
        "language": "भाषा",
    },
}


def t(key: str, lang: str = "en") -> str:
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)
