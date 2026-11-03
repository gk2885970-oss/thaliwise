# ThaliWise — Budget-First Nutrition Optimizer

**What should we buy this week, within our budget, to meet our family’s nutrition needs?**

ThaliWise is a working Streamlit prototype that uses **linear programming** to find the lowest-cost weekly food basket meeting household targets for calories, protein and iron. It is built for an Innovation & Entrepreneurship student assignment (Group A2).

## Features

- Household profile (adults, children, seniors, diet type, exclusions)
- ICMR-NIN-inspired daily nutrition targets
- Real linear-programming cost minimisation (PuLP)
- Weekly shopping list with quantities and costs
- Illustrative 7-day meal ideas
- Food substitution suggestions
- Budget-vs-nutrition scenario analysis
- NGO / group procurement dashboard
- English / Hindi UI strings
- Rule-based natural-language input parsing (no API key required)
- CSV export of shopping / procurement lists

## Quick start

```bash
cd thaliwise
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit (usually http://localhost:8501).

## Project structure

```
thaliwise/
├── app.py                 # Streamlit entry point
├── requirements.txt
├── README.md
├── data/
│   ├── foods.csv          # ~55 Indian foods, nutrients + sample prices
│   └── nutrition_targets.csv
├── src/
│   ├── data_loader.py
│   ├── data_validation.py
│   ├── household_profile.py
│   ├── optimizer.py       # Core LP engine
│   ├── meal_planner.py
│   ├── substitution.py
│   ├── budget_analysis.py
│   ├── ai_layer.py        # Rule-based NLP + explanations
│   ├── localization.py
│   └── reporting.py
└── tests/
    ├── test_optimizer.py
    ├── test_nutrition.py
    └── test_data_validation.py
```

## Running tests

```bash
cd thaliwise
python -m tests.test_data_validation
python -m tests.test_nutrition
python -m tests.test_optimizer
```

## Data notes

- **Nutrient values** are approximate figures consistent with Indian Food Composition Tables 2017 (ICMR-NIN). They are not a full reproduction of the official tables.
- **Prices** are illustrative pilot values styled after Delhi retail observations (Department of Consumer Affairs / local survey). They are **not live market prices**. Update `data/foods.csv` with your local prices.
- **Targets** follow the spirit of ICMR-NIN 2020 RDAs; they are configurable and clearly labelled as reference values for planning, not medical prescriptions.

## Optional LLM

The current AI layer is fully functional without any API key (rule-based parsing and explanations). To add a real LLM later, extend `src/ai_layer.py` with an optional OpenAI/Claude client and keep the rule-based path as fallback.

## Disclaimer

ThaliWise provides **general nutrition planning** only. It does not diagnose, treat or give medical advice. Always consult qualified professionals for health conditions.

## Licence

Student prototype for educational use.
