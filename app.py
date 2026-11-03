"""
ThaliWise — Budget-First Nutrition Optimizer
Polished Streamlit web app (mobile-first)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.data_loader import load_foods, load_nutrition_targets
from src.data_validation import validate_foods
from src.household_profile import HouseholdProfile, Member, calculate_daily_targets
from src.optimizer import optimize_diet
from src.meal_planner import generate_meal_plan
from src.substitution import suggest_substitutes
from src.budget_analysis import analyze_budget_tradeoff
from src.ai_layer import parse_natural_language, explain_basket
from src.localization import t
from src.reporting import shopping_list_to_csv

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ThaliWise | Budget-First Nutrition",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — clean, modern, mobile-first
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Outfit:wght@500;600;700&display=swap');

:root {
    --green-900: #1B5E20;
    --green-700: #2E7D32;
    --green-500: #43A047;
    --green-100: #E8F5E9;
    --green-50:  #F1F8E9;
    --orange-700: #E65100;
    --orange-500: #FF6D00;
    --orange-100: #FFF3E0;
    --slate-900: #0F172A;
    --slate-700: #334155;
    --slate-500: #64748B;
    --slate-200: #E2E8F0;
    --slate-100: #F1F5F9;
    --white: #FFFFFF;
    --radius: 16px;
    --shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', system-ui, sans-serif;
    color: var(--slate-900);
}

/* Hide default Streamlit chrome noise */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stToolbar"] { display: none; }

/* Main container */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1B5E20 140%);
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem;
    padding: 0.35rem 0;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #94A3B8 !important;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 45%, #E65100 160%);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    color: white;
    margin-bottom: 1.75rem;
    box-shadow: 0 12px 40px rgba(27, 94, 32, 0.25);
}
.hero h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.02em;
    color: white;
}
.hero .tag {
    font-size: 1.15rem;
    opacity: 0.92;
    margin-bottom: 1.25rem;
    font-weight: 500;
}
.hero .question {
    font-size: 1.05rem;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    border: 1px solid rgba(255,255,255,0.2);
    margin-top: 0.5rem;
}

/* ── Cards ── */
.card {
    background: white;
    border: 1px solid var(--slate-200);
    border-radius: var(--radius);
    padding: 1.35rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
.card-green {
    background: var(--green-50);
    border: 1px solid #C8E6C9;
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
}
.card-orange {
    background: var(--orange-100);
    border: 1px solid #FFE0B2;
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
}

/* ── Section titles (light + dark) ── */
.section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.45rem;
    font-weight: 600;
    margin: 0.5rem 0 1rem 0;
    letter-spacing: -0.01em;
    color: #E8F5E9 !important;
}
.section-sub {
    font-size: 0.95rem;
    margin-bottom: 1.25rem;
    color: #A5D6A7 !important;
}

@media (prefers-color-scheme: light) {
    .section-title {
        color: #1B5E20 !important;
    }
    .section-sub {
        color: #558B2F !important;
    }
}

/* ── Metric pills ── */
.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    margin: 1rem 0 1.5rem 0;
}
.pill {
    background: white;
    border: 1px solid var(--slate-200);
    border-radius: 999px;
    padding: 0.45rem 1rem;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--green-700);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.pill span {
    color: var(--slate-500);
    font-weight: 500;
    margin-right: 0.35rem;
}

/* ── Status banners ── */
.banner-ok {
    background: linear-gradient(90deg, #E8F5E9, #F1F8E9);
    border-left: 5px solid var(--green-500);
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
    color: var(--green-900);
    font-weight: 500;
}
.banner-warn {
    background: linear-gradient(90deg, #FFF3E0, #FFF8E1);
    border-left: 5px solid var(--orange-500);
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
    color: #E65100;
    font-weight: 500;
}
.banner-err {
    background: #FFEBEE;
    border-left: 5px solid #E53935;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
    color: #B71C1C;
    font-weight: 500;
}

/* ── Food item row ── */
.food-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 0;
    border-bottom: 1px solid var(--slate-100);
}
.food-row:last-child { border-bottom: none; }
.food-name {
    font-weight: 600;
    color: var(--slate-900);
}
.food-meta {
    font-size: 0.85rem;
    color: var(--slate-500);
}
.food-cost {
    font-weight: 700;
    color: var(--green-700);
    font-size: 1.05rem;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.6rem 1.4rem !important;
    border: none !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #43A047, #2E7D32) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(67, 160, 71, 0.35);
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(67, 160, 71, 0.45);
}
.stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--green-700) !important;
    border: 1.5px solid var(--green-500) !important;
}

/* ── Inputs ── */
.stNumberInput input, .stTextInput input, .stSelectbox > div {
    border-radius: 10px !important;
}

/* ── Metric override ── */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--slate-200);
    border-radius: 14px;
    padding: 1rem 1.15rem;
    box-shadow: var(--shadow);
}
div[data-testid="stMetric"] label {
    color: var(--slate-500) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: var(--green-900) !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--slate-200);
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    border-radius: 10px !important;
}

/* ── Disclaimer ── */
.disclaimer {
    font-size: 0.8rem;
    color: var(--slate-500);
    text-align: center;
    margin-top: 2.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--slate-200);
}

/* ── Feature grid ── */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}
.feature-card {
    background: white;
    border: 1px solid var(--slate-200);
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: var(--shadow);
    transition: transform 0.15s ease;
}
.feature-card:hover { transform: translateY(-3px); }
.feature-icon {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
}
.feature-title {
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--slate-900);
    margin-bottom: 0.25rem;
}
.feature-desc {
    font-size: 0.82rem;
    color: var(--slate-500);
    line-height: 1.4;
}

/* ── Adequacy bar ── */
.adeq-bar-bg {
    background: var(--slate-100);
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    margin-top: 0.35rem;
}
.adeq-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #43A047, #66BB6A);
}

/* ── Step indicator ── */
.steps {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.step {
    background: var(--slate-100);
    color: var(--slate-500);
    border-radius: 999px;
    padding: 0.35rem 0.9rem;
    font-size: 0.8rem;
    font-weight: 600;
}
.step.active {
    background: var(--green-500);
    color: white;
}
.step.done {
    background: var(--green-100);
    color: var(--green-700);
}
</style>
""",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data
def get_foods():
    df = load_foods()
    ok, errs = validate_foods(df)
    return df, ok, errs


@st.cache_data
def get_targets():
    return load_nutrition_targets()


foods_df, foods_ok, foods_errs = get_foods()
targets_df = get_targets()

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════
defaults = {
    "lang": "en",
    "result": None,
    "daily_targets": None,
    "profile": None,
    "page": "Home",
    "budget_analysis": None,
    "ngo_result": None,
    "nl_parsed": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1.25rem 0;">
            <div style="font-family:'Outfit',sans-serif;font-size:1.6rem;font-weight:700;color:#A5D6A7 !important;">
                🥗 ThaliWise
            </div>
            <div style="font-size:0.82rem;color:#94A3B8 !important;margin-top:0.15rem;">
                Budget-first nutrition
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lang = st.selectbox("Language / भाषा", ["en", "hi"], index=0, label_visibility="collapsed")
    st.session_state.lang = lang

    st.markdown("---")

    pages = [
        ("🏠", "Home"),
        ("👨‍👩‍👧‍👦", "Household Profile"),
        ("⚡", "Generate Plan"),
        ("📊", "Results"),
        ("🛒", "Shopping List"),
        ("🍽️", "Meal Ideas"),
        ("🔄", "Substitutions"),
        ("📈", "Budget vs Nutrition"),
        ("🏛️", "NGO Dashboard"),
        ("ℹ️", "About & Data"),
    ]
    page_labels = [f"{icon}  {name}" for icon, name in pages]
    page_names = [name for _, name in pages]

    current_idx = page_names.index(st.session_state.page) if st.session_state.page in page_names else 0
    choice = st.radio("Navigate", page_labels, index=current_idx, label_visibility="collapsed")
    page = page_names[page_labels.index(choice)]
    st.session_state.page = page

    st.markdown("---")
    st.caption("General nutrition planning only · Not medical advice")

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def adequacy_bar(label: str, pct: float, value_str: str):
    pct_clamped = max(0, min(100, pct))
    color = "#43A047" if pct >= 95 else ("#FF8F00" if pct >= 70 else "#E53935")
    st.markdown(
        f"""
        <div style="margin-bottom:0.9rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.88rem;">
                <span style="font-weight:600;">{label}</span>
                <span style="color:#64748B;">{value_str} · <b style="color:{color}">{pct:.0f}%</b></span>
            </div>
            <div class="adeq-bar-bg">
                <div class="adeq-bar-fill" style="width:{pct_clamped}%;background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def step_indicator(active: str):
    steps = ["Profile", "Optimise", "Results", "Shop"]
    html = '<div class="steps">'
    found = False
    for s in steps:
        if s == active:
            html += f'<span class="step active">{s}</span>'
            found = True
        elif not found:
            html += f'<span class="step done">{s}</span>'
        else:
            html += f'<span class="step">{s}</span>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════
if page == "Home":
    st.markdown(
        """
        <div class="hero">
            <h1>🥗 ThaliWise</h1>
            <div class="tag">Budget-first nutrition optimizer</div>
            <div class="question">
                “What should we buy this week, within our budget, to meet our family’s nutrition needs?”
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">💰</div>
                <div class="feature-title">Budget first</div>
                <div class="feature-desc">Start from ₹X per week. The tool works backwards to the best nutrition you can afford.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🧮</div>
                <div class="feature-title">Real optimisation</div>
                <div class="feature-desc">Linear programming finds the cheapest basket that hits calorie, protein & iron targets.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🥬</div>
                <div class="feature-title">Local foods</div>
                <div class="feature-desc">55 common Indian foods with IFCT-style nutrients and sample market prices.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <div class="feature-title">Simple output</div>
                <div class="feature-desc">Shopping list, meal ideas, swaps and budget trade-offs — in plain language.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if st.button("Start planning →", type="primary", use_container_width=True):
            st.session_state.page = "Household Profile"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("💬 Quick start with natural language"):
        st.caption("Type something like: “Family of 4, Rs 1800 a week, vegetarian”")
        nl = st.text_input("Describe your household", placeholder="2 adults, 2 children, budget 1500, vegetarian", label_visibility="collapsed")
        if st.button("Parse & apply", use_container_width=True):
            parsed = parse_natural_language(nl)
            st.session_state.nl_parsed = parsed
            st.success(
                f"Parsed → Adults: {parsed['adults']}, Children: {parsed['children']}, "
                f"Budget: ₹{parsed['budget']:.0f}, Diet: {parsed['diet_type']}"
            )
            st.info("Go to **Household Profile** to review and generate the plan.")

    st.markdown(
        '<p class="disclaimer">General nutrition planning based on ICMR-NIN reference values and sample prices. Not medical advice.</p>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════
# HOUSEHOLD PROFILE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Household Profile":
    step_indicator("Profile")
    st.markdown('<p class="section-title">👨‍👩‍👧‍👦 Household profile</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Tell us who eats at home and how much you can spend this week.</p>', unsafe_allow_html=True)

    nl = st.session_state.get("nl_parsed", {})
    default_adults = int(nl.get("adults", 2))
    default_children = int(nl.get("children", 1))
    default_budget = float(nl.get("budget", 1800.0))
    default_diet = nl.get("diet_type", "vegetarian")
    diet_opts = ["vegetarian", "eggitarian", "non-vegetarian", "vegan"]
    diet_idx = diet_opts.index(default_diet) if default_diet in diet_opts else 0

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Family members**")
    c1, c2, c3 = st.columns(3)
    with c1:
        n_adults = st.number_input("Adults (18–59)", 0, 10, default_adults)
        n_seniors = st.number_input("Seniors (60+)", 0, 5, 0)
    with c2:
        n_c13 = st.number_input("Children 1–3 yrs", 0, 5, 0)
        n_c46 = st.number_input("Children 4–6 yrs", 0, 5, default_children if default_children else 0)
    with c3:
        n_c79 = st.number_input("Children 7–9 yrs", 0, 5, 0)
        n_adol = st.number_input("Adolescents 10–18", 0, 6, 0)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Budget & diet**")
    b1, b2 = st.columns(2)
    with b1:
        weekly_budget = st.number_input("Weekly food budget (₹)", 200.0, 20000.0, default_budget, 50.0)
        diet_type = st.selectbox("Dietary preference", diet_opts, index=diet_idx)
    with b2:
        locality = st.selectbox("Market / locality", ["Delhi/NCR", "Other (sample prices)"])
        exclusions = st.multiselect("Exclude foods (optional)", foods_df["name_en"].tolist())
    st.markdown("</div>", unsafe_allow_html=True)

    # Build members
    members = []
    if n_adults:
        members.append(Member("18-59", "Female", "Adult", max(1, n_adults // 2)))
        members.append(Member("18-59", "Male", "Adult", n_adults - max(1, n_adults // 2)))
    if n_seniors:
        members.append(Member("60+", "Female", "Adult", max(1, n_seniors // 2)))
        if n_seniors > 1:
            members.append(Member("60+", "Male", "Adult", n_seniors - max(1, n_seniors // 2)))
    if n_c13:
        members.append(Member("1-3", "Any", "Child", n_c13))
    if n_c46:
        members.append(Member("4-6", "Any", "Child", n_c46))
    if n_c79:
        members.append(Member("7-9", "Any", "Child", n_c79))
    if n_adol:
        members.append(Member("13-15", "Male", "Adolescent", max(1, n_adol // 2)))
        if n_adol > 1:
            members.append(Member("13-15", "Female", "Adolescent", n_adol - max(1, n_adol // 2)))
    if not members:
        members = [Member("18-59", "Female", "Adult", 1)]

    profile = HouseholdProfile(
        members=members,
        diet_type=diet_type,
        exclusions=exclusions,
        locality=locality,
        weekly_budget=weekly_budget,
    )
    daily = calculate_daily_targets(profile, targets_df)
    st.session_state.profile = profile
    st.session_state.daily_targets = daily

    st.markdown('<p class="section-title" style="font-size:1.15rem;">Daily nutrition targets</p>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calories", f"{daily['calories_kcal']:.0f} kcal")
    m2.metric("Protein", f"{daily['protein_g']:.0f} g")
    m3.metric("Iron", f"{daily['iron_mg']:.0f} mg")
    m4.metric("Family size", f"{profile.total_members()} people")
    st.caption(daily["source"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ Generate nutrition plan", type="primary", use_container_width=True):
        with st.spinner("Running linear-programming optimiser…"):
            result = optimize_diet(
                foods_df, daily, weekly_budget,
                diet_type=diet_type, exclusions=exclusions,
            )
            st.session_state.result = result
            st.session_state.page = "Results"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE PLAN (shortcut)
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Generate Plan":
    step_indicator("Optimise")
    st.markdown('<p class="section-title">⚡ Generate plan</p>', unsafe_allow_html=True)

    if st.session_state.profile is None:
        st.markdown(
            '<div class="banner-warn">Complete the Household Profile first, then come back here or generate directly from the profile page.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Go to Household Profile", type="primary"):
            st.session_state.page = "Household Profile"
            st.rerun()
    else:
        p = st.session_state.profile
        d = st.session_state.daily_targets
        st.markdown(
            f"""
            <div class="card-green">
                <b>Ready to optimise</b><br>
                Budget ₹{p.weekly_budget:.0f} · {p.diet_type} · {p.total_members()} people<br>
                Daily targets → {d['calories_kcal']:.0f} kcal · {d['protein_g']:.0f} g protein · {d['iron_mg']:.0f} mg iron
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Run optimiser", type="primary", use_container_width=True):
            with st.spinner("Finding the cheapest nutrient-complete basket…"):
                result = optimize_diet(
                    foods_df, d, p.weekly_budget,
                    diet_type=p.diet_type, exclusions=p.exclusions,
                )
                st.session_state.result = result
                st.session_state.page = "Results"
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Results":
    step_indicator("Results")
    st.markdown('<p class="section-title">📊 Optimisation results</p>', unsafe_allow_html=True)

    result = st.session_state.result
    daily = st.session_state.daily_targets

    if result is None:
        st.markdown(
            '<div class="banner-warn">No plan yet. Go to Household Profile and generate one.</div>',
            unsafe_allow_html=True,
        )
    else:
        status = result["status"]
        if status == "optimal":
            st.markdown(f'<div class="banner-ok">✅ {result["message"]}</div>', unsafe_allow_html=True)
        elif status == "budget_insufficient":
            st.markdown(f'<div class="banner-warn">⚠️ {result["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="banner-err">❌ {result["message"]}</div>', unsafe_allow_html=True)

        explanation = explain_basket(result, daily or {}, language=st.session_state.lang)
        st.markdown(f'<div class="card">{explanation}</div>', unsafe_allow_html=True)

        # Key metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Weekly cost", f"₹{result['total_cost']:.0f}")
        c2.metric("Budget left", f"₹{result['budget_remaining']:.0f}")
        c3.metric("Foods selected", len(result["basket"]))
        if result.get("extra_budget_needed"):
            c4.metric("Extra needed", f"₹{result['extra_budget_needed']:.0f}")
        else:
            c4.metric("Status", status.replace("_", " ").title())

        # Adequacy
        st.markdown('<p class="section-title" style="font-size:1.15rem;margin-top:1.5rem;">Nutrition achievement</p>', unsafe_allow_html=True)
        adeq = result["adequacy"]
        nutrients = result["nutrients"]
        targets_w = result["weekly_targets"]

        col_a, col_b = st.columns([1, 1.2])
        with col_a:
            adequacy_bar("Calories", adeq["calories"], f"{nutrients['calories']:.0f} / {targets_w['calories']:.0f} kcal")
            adequacy_bar("Protein", adeq["protein"], f"{nutrients['protein']:.0f} / {targets_w['protein']:.0f} g")
            adequacy_bar("Iron", adeq["iron"], f"{nutrients['iron']:.0f} / {targets_w['iron']:.0f} mg")

        with col_b:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Achieved",
                x=["Calories", "Protein", "Iron"],
                y=[nutrients["calories"], nutrients["protein"], nutrients["iron"]],
                marker_color="#43A047",
                text=[f"{nutrients['calories']:.0f}", f"{nutrients['protein']:.0f}", f"{nutrients['iron']:.0f}"],
                textposition="outside",
            ))
            fig.add_trace(go.Bar(
                name="Weekly target",
                x=["Calories", "Protein", "Iron"],
                y=[targets_w["calories"], targets_w["protein"], targets_w["iron"]],
                marker_color="#FF8A65",
                text=[f"{targets_w['calories']:.0f}", f"{targets_w['protein']:.0f}", f"{targets_w['iron']:.0f}"],
                textposition="outside",
            ))
            fig.update_layout(
                barmode="group",
                height=280,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", size=12),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Basket
        st.markdown('<p class="section-title" style="font-size:1.15rem;">Selected food basket</p>', unsafe_allow_html=True)
        if result["basket"]:
            bdf = pd.DataFrame(result["basket"])
            # Cost share pie
            fig2 = px.pie(
                bdf, values="cost", names="name_en",
                color_discrete_sequence=px.colors.sequential.Greens_r,
                hole=0.45,
            )
            fig2.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True,
                legend=dict(font=dict(size=11), orientation="v"),
                font=dict(family="DM Sans"),
            )
            fig2.update_traces(textposition="inside", textinfo="percent")

            left, right = st.columns([1.1, 1])
            with left:
                st.dataframe(
                    bdf[["name_en", "name_hi", "category", "quantity_display", "cost", "protein", "iron"]].rename(
                        columns={
                            "name_en": "Food",
                            "name_hi": "Hindi",
                            "category": "Category",
                            "quantity_display": "Qty",
                            "cost": "Cost ₹",
                            "protein": "Protein g",
                            "iron": "Iron mg",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=min(400, 50 + 35 * len(bdf)),
                )
            with right:
                st.plotly_chart(fig2, use_container_width=True)
                st.caption("Cost share of the weekly basket")
        else:
            st.write("No foods selected.")

        st.markdown("<br>", unsafe_allow_html=True)
        n1, n2, n3 = st.columns(3)
        with n1:
            if st.button("🛒 Shopping list", use_container_width=True):
                st.session_state.page = "Shopping List"
                st.rerun()
        with n2:
            if st.button("🍽️ Meal ideas", use_container_width=True):
                st.session_state.page = "Meal Ideas"
                st.rerun()
        with n3:
            if st.button("📈 Budget analysis", use_container_width=True):
                st.session_state.page = "Budget vs Nutrition"
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# SHOPPING LIST
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Shopping List":
    step_indicator("Shop")
    st.markdown('<p class="section-title">🛒 Weekly shopping list</p>', unsafe_allow_html=True)

    result = st.session_state.result
    if not result or not result.get("basket"):
        st.markdown('<div class="banner-warn">Generate a plan first to see your shopping list.</div>', unsafe_allow_html=True)
    else:
        basket = result["basket"]
        total = result["total_cost"]

        st.markdown(
            f"""
            <div class="card-green">
                <b>{len(basket)} items</b> · Estimated total <b>₹{total:.0f}</b>
                &nbsp;·&nbsp; Budget remaining ₹{result['budget_remaining']:.0f}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Group by category
        by_cat = {}
        for item in basket:
            by_cat.setdefault(item["category"], []).append(item)

        for cat, items in by_cat.items():
            st.markdown(f"**{cat}**")
            for item in items:
                cols = st.columns([0.08, 3.2, 1.5, 1])
                with cols[0]:
                    st.checkbox("", key=f"bought_{item['food_id']}", label_visibility="collapsed")
                with cols[1]:
                    st.markdown(
                        f"<span class='food-name'>{item['name_en']}</span> "
                        f"<span class='food-meta'>({item.get('name_hi', '')})</span>",
                        unsafe_allow_html=True,
                    )
                with cols[2]:
                    st.markdown(f"<span class='food-meta'>{item['quantity_display']}</span>", unsafe_allow_html=True)
                with cols[3]:
                    st.markdown(f"<span class='food-cost'>₹{item['cost']:.0f}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.4rem 0 1rem 0;border:none;border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

        csv_data = shopping_list_to_csv(basket)
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="thaliwise_shopping_list.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ═══════════════════════════════════════════════════════════════════════════
# MEAL IDEAS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Meal Ideas":
    st.markdown('<p class="section-title">🍽️ Sample meal ideas</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Illustrative suggestions using foods from your optimised basket. Adjust quantities to taste.</p>',
        unsafe_allow_html=True,
    )

    result = st.session_state.result
    if not result or not result.get("basket"):
        st.markdown('<div class="banner-warn">Generate a plan first.</div>', unsafe_allow_html=True)
    else:
        plan = generate_meal_plan(result["basket"])
        meal_icons = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snack": "🍎"}

        for day in plan:
            with st.expander(f"Day {day['day']}", expanded=(day["day"] == 1)):
                for meal_type, meal in day["meals"].items():
                    icon = meal_icons.get(meal_type, "🍴")
                    st.markdown(
                        f"""
                        <div style="padding:0.5rem 0 0.7rem 0;border-bottom:1px solid #F1F5F9;">
                            <span style="font-weight:700;">{icon} {meal_type.title()}</span><br>
                            <span style="color:#334155;">{meal['description']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.caption("Illustrative only — not exact meal-level nutrition calculations.")

# ═══════════════════════════════════════════════════════════════════════════
# SUBSTITUTIONS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Substitutions":
    st.markdown('<p class="section-title">🔄 Food substitutions</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Replace an expensive or unavailable food with a nutrient-similar alternative.</p>',
        unsafe_allow_html=True,
    )

    result = st.session_state.result
    profile = st.session_state.profile
    if not result or not result.get("basket"):
        st.markdown('<div class="banner-warn">Generate a plan first.</div>', unsafe_allow_html=True)
    else:
        names = {b["name_en"]: b["food_id"] for b in result["basket"]}
        chosen = st.selectbox("Select a food to replace", list(names.keys()))
        if chosen:
            fid = names[chosen]
            diet = profile.diet_type if profile else "vegetarian"
            subs = suggest_substitutes(foods_df, fid, result["basket"], diet_type=diet)
            if subs:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                sdf = pd.DataFrame(subs)
                st.dataframe(
                    sdf[["name_en", "category", "price_per_kg", "price_diff_per_kg", "protein_per_100g", "iron_per_100g", "reason"]].rename(
                        columns={
                            "name_en": "Alternative",
                            "category": "Category",
                            "price_per_kg": "₹/kg",
                            "price_diff_per_kg": "Δ price",
                            "protein_per_100g": "Protein/100g",
                            "iron_per_100g": "Iron/100g",
                            "reason": "Why",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
                st.caption("To apply a substitute, add the original food to exclusions on the Profile page and re-run.")
            else:
                st.info("No suitable substitutes found under current diet rules.")

# ═══════════════════════════════════════════════════════════════════════════
# BUDGET VS NUTRITION
# ═══════════════════════════════════════════════════════════════════════════
elif page == "Budget vs Nutrition":
    st.markdown('<p class="section-title">📈 Budget vs nutrition</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">See how nutrition adequacy changes when you raise or lower the weekly budget.</p>',
        unsafe_allow_html=True,
    )

    profile = st.session_state.profile
    daily = st.session_state.daily_targets
    if profile is None or daily is None:
        st.markdown('<div class="banner-warn">Complete Household Profile first.</div>', unsafe_allow_html=True)
    else:
        if st.button("Run budget scenarios", type="primary", use_container_width=True):
            with st.spinner("Evaluating multiple budget levels…"):
                analysis = analyze_budget_tradeoff(
                    foods_df, daily, profile.weekly_budget,
                    diet_type=profile.diet_type, exclusions=profile.exclusions,
                )
                st.session_state.budget_analysis = analysis

        analysis = st.session_state.get("budget_analysis")
        if analysis:
            adf = pd.DataFrame(analysis["scenarios"])
            st.dataframe(
                adf.rename(columns={
                    "budget": "Budget ₹",
                    "status": "Status",
                    "total_cost": "Cost ₹",
                    "adequacy_calories": "Cal %",
                    "adequacy_protein": "Protein %",
                    "adequacy_iron": "Iron %",
                    "extra_needed": "Extra ₹",
                }),
                use_container_width=True,
                hide_index=True,
            )

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=adf["budget"], y=adf["adequacy_calories"],
                name="Calories %", mode="lines+markers",
                line=dict(color="#43A047", width=3), marker=dict(size=8),
            ))
            fig.add_trace(go.Scatter(
                x=adf["budget"], y=adf["adequacy_protein"],
                name="Protein %", mode="lines+markers",
                line=dict(color="#FF6D00", width=3), marker=dict(size=8),
            ))
            fig.add_trace(go.Scatter(
                x=adf["budget"], y=adf["adequacy_iron"],
                name="Iron %", mode="lines+markers",
                line=dict(color="#1E88E5", width=3), marker=dict(size=8),
            ))
            fig.update_layout(
                title="Nutrition adequacy vs weekly budget",
                xaxis_title="Weekly budget (₹)",
                yaxis_title="Adequacy (%)",
                height=380,
                margin=dict(l=40, r=20, t=50, b=40),
                legend=dict(orientation="h", y=1.12),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 110]),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Higher budgets make it easier to hit all three targets at once.")

# ═══════════════════════════════════════════════════════════════════════════
# NGO DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
elif page == "NGO Dashboard":
    st.markdown('<p class="section-title">🏛️ NGO / Group dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Plan a common menu for anganwadi, hostel or community kitchen within a per-person budget.</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        n_beneficiaries = st.number_input("Beneficiaries", 10, 500, 50)
    with g2:
        per_person_budget = st.number_input("Per-person weekly ₹", 50.0, 1000.0, 150.0)
    with g3:
        group_diet = st.selectbox("Group diet", ["vegetarian", "eggitarian", "non-vegetarian"], key="ngo_diet")
    st.markdown("</div>", unsafe_allow_html=True)

    demo_profile = HouseholdProfile(
        members=[
            Member("18-59", "Female", "Adult", 1),
            Member("18-59", "Male", "Adult", 1),
            Member("4-6", "Any", "Child", 1),
        ],
        diet_type=group_diet,
        weekly_budget=per_person_budget * 3,
    )
    demo_daily = calculate_daily_targets(demo_profile, targets_df)

    if st.button("Generate group procurement plan", type="primary", use_container_width=True):
        with st.spinner("Optimising group basket…"):
            res = optimize_diet(foods_df, demo_daily, per_person_budget * 3, diet_type=group_diet)
            scale = n_beneficiaries / 3.0
            if res["basket"]:
                for b in res["basket"]:
                    b["quantity_g"] = round(b["quantity_g"] * scale, 1)
                    b["quantity_display"] = (
                        f"{b['quantity_g']/1000:.2f} kg" if b["quantity_g"] >= 1000 else f"{b['quantity_g']:.0f} g"
                    )
                    b["cost"] = round(b["cost"] * scale, 2)
                res["total_cost"] = round(res["total_cost"] * scale, 2)
                res["budget_remaining"] = round(per_person_budget * n_beneficiaries - res["total_cost"], 2)
            st.session_state.ngo_result = res

    ngo_res = st.session_state.get("ngo_result")
    if ngo_res:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total procurement", f"₹{ngo_res['total_cost']:.0f}")
        m2.metric("Per person", f"₹{ngo_res['total_cost']/n_beneficiaries:.1f}")
        m3.metric("Status", ngo_res["status"].replace("_", " ").title())

        if ngo_res["basket"]:
            st.dataframe(
                pd.DataFrame(ngo_res["basket"])[["name_en", "quantity_display", "cost"]].rename(
                    columns={"name_en": "Food", "quantity_display": "Quantity", "cost": "Cost ₹"}
                ),
                use_container_width=True,
                hide_index=True,
            )
            csv = shopping_list_to_csv(ngo_res["basket"])
            st.download_button(
                "⬇️ Download procurement list",
                data=csv,
                file_name="ngo_procurement.csv",
                mime="text/csv",
                use_container_width=True,
            )

# ═══════════════════════════════════════════════════════════════════════════
# ABOUT & DATA
# ═══════════════════════════════════════════════════════════════════════════
elif page == "About & Data":
    st.markdown('<p class="section-title">ℹ️ About ThaliWise</p>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card">
            <b>ThaliWise</b> is a student prototype for Innovation & Entrepreneurship.
            It makes the classic linear-programming diet problem (Stigler, 1945) practical for
            Indian households by combining verified nutrient data with sample local prices and a plain-language interface.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            **Core engine**
            - Linear programming (PuLP / CBC)
            - Minimises weekly cost
            - Constraints: calories, protein, iron, budget, diet, variety

            **AI layer**
            - Rule-based NL parsing & explanations
            - No paid API required
            - Ready for optional LLM upgrade
            """
        )
    with c2:
        st.markdown(
            """
            **Data sources**
            - Nutrients ≈ IFCT 2017 (ICMR-NIN)
            - Targets ≈ ICMR-NIN 2020 RDAs
            - Prices: illustrative Delhi/NCR pilot values
            - **Not live market prices**

            **Limitations**
            - ~55 common foods
            - Static sample prices
            - General planning only — not medical advice
            """
        )

    st.markdown('<p class="section-title" style="font-size:1.15rem;">Food database preview</p>', unsafe_allow_html=True)
    st.dataframe(
        foods_df[
            ["food_id", "name_en", "category", "calories_kcal_per_100g", "protein_g_per_100g", "iron_mg_per_100g", "price_inr_per_kg"]
        ].rename(columns={
            "food_id": "ID",
            "name_en": "Food",
            "category": "Category",
            "calories_kcal_per_100g": "kcal/100g",
            "protein_g_per_100g": "Protein",
            "iron_mg_per_100g": "Iron",
            "price_inr_per_kg": "₹/kg",
        }),
        use_container_width=True,
        hide_index=True,
        height=320,
    )
    st.caption(f"{len(foods_df)} foods loaded · Validation OK: {foods_ok}")

    st.markdown(
        '<p class="disclaimer">ThaliWise · Group A2 · Innovation & Entrepreneurship · General nutrition planning only</p>',
        unsafe_allow_html=True,
    )