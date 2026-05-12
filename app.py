import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Cost of Living — Australia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# Presentation-grade: min 14px labels, WCAG AA contrast on all text
# Two-colour narrative: RED = problem, GREEN = solution
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── App shell ── */
.stApp { background-color: #F5F4F0; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; }

/* ── Sidebar: dark, high contrast ── */
[data-testid="stSidebar"] {
    background-color: #111110 !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #E8E6DF !important; }
[data-testid="stSidebar"] .stSlider > label,
[data-testid="stSidebar"] .stMultiSelect > label,
[data-testid="stSidebar"] .stNumberInput > label,
[data-testid="stSidebar"] .stToggle > label {
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em;
    color: #A8A49A !important;
}
[data-testid="stSidebar"] hr { border-color: #2A2A28 !important; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 13px !important; }

/* ── Tab navigation ── */
[data-baseweb="tab-list"] {
    background: #111110 !important;
    border-radius: 10px !important;
    padding: 5px !important;
    gap: 3px !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #A8A49A !important;
    border-radius: 7px !important;
    padding: 9px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border: none !important;
    letter-spacing: 0.02em;
}
[data-baseweb="tab"]:hover { background: rgba(255,255,255,0.10) !important; color: #FFFFFF !important; }
[aria-selected="true"][data-baseweb="tab"] { background: #FFFFFF !important; color: #111110 !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* ── KPI cards ── */
.kpi-card {
    border-radius: 10px;
    padding: 16px 18px;
    min-height: 96px;
    box-sizing: border-box;
}
.kpi-card .k-lbl {
    font-size: 11px; font-weight: 700; letter-spacing: 0.09em;
    text-transform: uppercase; margin-bottom: 6px; line-height: 1.3;
}
.kpi-card .k-val {
    font-size: 30px; font-weight: 800; line-height: 1.05;
}
.kpi-card .k-sub {
    font-size: 12px; margin-top: 5px; font-weight: 500;
}

/* Default — white card, dark text */
.kpi-default { background: #FFFFFF; border: 1.5px solid #D8D5CC; }
.kpi-default .k-lbl { color: #5A574F; }
.kpi-default .k-val { color: #111110; }
.kpi-default .k-sub { color: #5A574F; }

/* Hero — deep green, signals positive/solution */
.kpi-hero { background: #0A4D35; border: none; }
.kpi-hero .k-lbl { color: #6ECBA8; }
.kpi-hero .k-val { color: #FFFFFF; font-size: 34px; }
.kpi-hero .k-sub { color: #9ED8C0; }

/* Alert — deep red, signals crisis/problem */
.kpi-alert { background: #5C1A0E; border: none; }
.kpi-alert .k-lbl { color: #F4A07A; }
.kpi-alert .k-val { color: #FFFFFF; font-size: 34px; }
.kpi-alert .k-sub { color: #E88A60; }

/* ── Delta badges ── */
.d-up  { color: #0A8A55; font-size: 12px; font-weight: 600; }
.d-dn  { color: #C0390A; font-size: 12px; font-weight: 600; }
.d-neu { color: #5A574F; font-size: 12px; font-weight: 600; }

/* ── Section / chart labels ── */
.chart-title {
    font-size: 12px; font-weight: 700; letter-spacing: 0.09em;
    color: #5A574F; text-transform: uppercase; margin-bottom: 4px;
    margin-top: 16px;
}

/* ── Callout boxes ── */
.callout {
    background: #FFFFFF; border-left: 4px solid #0A8A55;
    border-radius: 0 8px 8px 0; padding: 14px 18px;
    margin: 12px 0; font-size: 15px; font-weight: 500;
    color: #111110; line-height: 1.6;
}
.callout-warn {
    background: #FFF8F5; border-left: 4px solid #C0390A;
    border-radius: 0 8px 8px 0; padding: 14px 18px;
    margin: 12px 0; font-size: 15px; font-weight: 500;
    color: #111110; line-height: 1.6;
}
.callout strong, .callout-warn strong { font-weight: 800; }

/* ── Page heading ── */
.page-h { font-size: 26px; font-weight: 800; color: #111110; line-height: 1.25; margin-bottom: 4px; }
.page-sub { font-size: 15px; color: #5A574F; margin-bottom: 14px; }

#MainMenu, footer, .stDeployButton { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# COLOUR PALETTE  (two-colour narrative: RED = problem, GREEN = solution)
# ─────────────────────────────────────────────────────────────────
RED    = "#C0390A"   # crisis / inflation / cost
GREEN  = "#0A8A55"   # solution / wages / relief
AMBER  = "#9A6000"   # secondary / caution
PURPLE = "#4A43A0"   # projection / "what-if"
BLUE   = "#1A5FAB"   # neutral data
GRAY   = "#5A574F"   # labels (passes WCAG AA on white)
LGRAY  = "#D8D5CC"   # grid lines
WHITE  = "#FFFFFF"
_FONT  = "Inter, sans-serif"
_GRID  = "#EDE9E1"

def base_layout(height=280, hmode="x unified"):
    return dict(
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        font=dict(family=_FONT, size=13, color="#111110"),
        margin=dict(t=12, b=12, l=12, r=12),
        height=height,
        hovermode=hmode,
        hoverlabel=dict(font=dict(size=13, family=_FONT), bgcolor=WHITE, bordercolor=LGRAY),
        legend=dict(
            orientation="h", yanchor="top", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(255,255,255,0.9)", font=dict(size=12, family=_FONT),
            borderwidth=0,
        ),
        xaxis=dict(showgrid=False, tickfont=dict(size=12), title_font=dict(size=13)),
        yaxis=dict(showgrid=True, gridcolor=_GRID, tickfont=dict(size=12), title_font=dict(size=13)),
    )


def kpi(label, value, sub="", style="default"):
    sub_html = f'<div class="k-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card kpi-{style}">'
        f'<div class="k-lbl">{label}</div>'
        f'<div class="k-val">{value}</div>'
        f'{sub_html}</div>'
    )


# ─────────────────────────────────────────────────────────────────
# SHARED INDEX CONSTANTS
# ─────────────────────────────────────────────────────────────────
WAGE_IDX = {
    "2021Q1":131.1,"2021Q2":132.0,"2021Q3":132.8,"2021Q4":133.8,
    "2022Q1":134.6,"2022Q2":135.7,"2022Q3":137.2,"2022Q4":138.6,
    "2023Q1":140.4,"2023Q2":142.8,"2023Q3":145.1,"2023Q4":147.3,
    "2024Q1":150.2,"2024Q2":151.1,"2024Q3":153.1,"2024Q4":154.1,
    "2025Q1":155.3,"2025Q2":156.2,
}
CPI_IDX = {
    "2021Q1":84.03,"2021Q2":84.80,"2021Q3":85.50,"2021Q4":86.40,
    "2022Q1":88.10,"2022Q2":91.10,"2022Q3":92.80,"2022Q4":93.60,
    "2023Q1":93.90,"2023Q2":94.20,"2023Q3":94.50,"2023Q4":94.80,
    "2024Q1":95.41,"2024Q2":96.41,"2024Q3":96.62,"2024Q4":96.81,
    "2025Q1":97.70,"2025Q2":98.43,
}
CPI_YOY = {
    "2021Q1":1.1,"2021Q2":3.8,"2021Q3":3.0,"2021Q4":3.5,
    "2022Q1":5.1,"2022Q2":6.1,"2022Q3":7.3,"2022Q4":7.8,
    "2023Q1":7.0,"2023Q2":6.0,"2023Q3":5.4,"2023Q4":4.1,
    "2024Q1":3.6,"2024Q2":3.8,"2024Q3":2.8,"2024Q4":2.4,
    "2025Q1":2.4,"2025Q2":2.1,
}
WAGE_YOY = {
    "2021Q1":1.4,"2021Q2":1.7,"2021Q3":1.9,"2021Q4":2.3,
    "2022Q1":2.4,"2022Q2":2.6,"2022Q3":3.1,"2022Q4":3.3,
    "2023Q1":3.7,"2023Q2":3.7,"2023Q3":4.0,"2023Q4":4.2,
    "2024Q1":4.1,"2024Q2":4.0,"2024Q3":3.6,"2024Q4":3.5,
    "2025Q1":3.4,"2025Q2":3.38,
}
ALL_QUARTERS = list(WAGE_IDX.keys())
HIST_Q       = ALL_QUARTERS[:12]   # 2021–2023


# ─────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_main():
    hist = pd.DataFrame({
        "quarter":       HIST_Q,
        "quarter_label": HIST_Q,
        "quarter_end": pd.to_datetime([
            "2021-03-31","2021-06-30","2021-09-30","2021-12-31",
            "2022-03-31","2022-06-30","2022-09-30","2022-12-31",
            "2023-03-31","2023-06-30","2023-09-30","2023-12-31",
        ]),
        "year":        [2021]*4+[2022]*4+[2023]*4,
        "quarter_num": [1,2,3,4]*3,
        "cpi_index":   [CPI_IDX[q] for q in HIST_Q],
        "wage_index":  [WAGE_IDX[q] for q in HIST_Q],
        "cpi_qoq_pct":  [0.6,0.9,0.8,1.0,2.0,3.4,1.8,0.9,0.3,0.3,0.3,0.3],
        "cpi_yoy_pct":  [CPI_YOY[q] for q in HIST_Q],
        "wage_qoq_pct": [0.5,0.7,0.6,0.7,0.6,0.8,1.1,1.0,1.3,1.7,1.6,1.5],
        "wage_yoy_pct": [WAGE_YOY[q] for q in HIST_Q],
        "real_wage_gap_yoy":      [0.3,-2.1,-1.1,-1.2,-2.7,-3.5,-4.2,-4.5,-3.3,-2.3,-1.4,0.1],
        "wage_to_cpi_ratio":      [1.560,1.557,1.553,1.549,1.528,1.490,1.478,1.481,1.495,1.516,1.535,1.554],
        "purchasing_power_index": [99.10,98.88,98.66,98.37,97.05,94.62,93.91,94.06,94.98,96.29,97.53,98.70],
        "retail_turnover_quarterly":   [90000]*12,
        "retail_turnover_monthly_avg": [30000]*12,
        "months_in_quarter":           [3]*12,
        "retail_qoq_pct": [None]*12,
        "retail_yoy_pct": [None]*12,
    })
    recent = pd.read_csv("combined_data-2024.csv")
    recent["quarter_end"] = pd.to_datetime(recent["quarter_end"])
    df = pd.concat([hist, recent], ignore_index=True).sort_values("quarter_end").reset_index(drop=True)
    patch = {
        "2024Q1":{"cpi_yoy_pct":3.6,"wage_yoy_pct":4.1,"real_wage_gap_yoy":0.5},
        "2024Q2":{"cpi_yoy_pct":3.8,"wage_yoy_pct":4.0,"real_wage_gap_yoy":0.2},
        "2024Q3":{"cpi_yoy_pct":2.8,"wage_yoy_pct":3.6,"real_wage_gap_yoy":0.8},
        "2024Q4":{"cpi_yoy_pct":2.4,"wage_yoy_pct":3.5,"real_wage_gap_yoy":1.1},
    }
    for q, vals in patch.items():
        mask = df["quarter_label"] == q
        for col, val in vals.items():
            df.loc[mask, col] = val
    return df


@st.cache_data
def load_cpi_categories():
    return pd.DataFrame({
        "category": [
            "Housing","Electricity & gas","Food & beverages",
            "Insurance & finance","Health","Transport",
            "Alcohol & tobacco","Education","Recreation","Clothing & footwear",
        ],
        "cpi_change": [4.5,8.2,3.8,6.1,3.9,4.2,6.5,5.1,1.2,0.6],
        "discretionary": [False,False,False,False,False,False,True,False,True,True],
    })


@st.cache_data
def load_state_data():
    return pd.DataFrame({
        "state":               ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"],
        "retail_change_pct":   [4.8,3.9,6.1,7.2,4.3,2.1,3.5,5.8],
        "real_change_pct":     [1.2,0.3,2.5,3.6,0.7,-1.5,-0.1,2.2],
        "avg_weekly_earnings": [1820,1750,1680,1950,1620,1490,2010,1880],
    })


@st.cache_data
def load_business_indicators():
    return pd.DataFrame({
        "quarter":       ["2024Q1","2024Q2","2024Q3","2024Q4","2025Q1","2025Q2"],
        "input_costs":   [100.0,101.8,103.2,104.1,105.3,106.2],
        "gross_surplus": [100.0,100.6,100.9,101.0,101.2,101.3],
        "wages_bill":    [100.0,101.1,102.6,103.3,104.2,104.9],
    })


@st.cache_data
def load_employee_map_data():
    """
    Simulated employee-level dataset (n=82 employees × 18 quarters).
    Used to show purchasing power dispersion across states and salary bands.
    """
    np.random.seed(42)
    state_cfg = {
        "NSW": {"lat":-33.0,"lon":147.0,"n":26,"avg":1820,"std":420,"jlat":2.5,"jlon":3.5},
        "VIC": {"lat":-37.2,"lon":144.5,"n":20,"avg":1750,"std":380,"jlat":1.5,"jlon":2.0},
        "QLD": {"lat":-22.5,"lon":144.5,"n":16,"avg":1680,"std":360,"jlat":4.5,"jlon":5.0},
        "WA":  {"lat":-26.0,"lon":121.0,"n": 9,"avg":1950,"std":430,"jlat":4.0,"jlon":5.5},
        "SA":  {"lat":-30.5,"lon":136.0,"n": 6,"avg":1620,"std":340,"jlat":2.5,"jlon":3.0},
        "TAS": {"lat":-42.0,"lon":146.5,"n": 2,"avg":1490,"std":280,"jlat":0.6,"jlon":0.8},
        "ACT": {"lat":-35.28,"lon":149.13,"n":2,"avg":2010,"std":180,"jlat":0.1,"jlon":0.1},
        "NT":  {"lat":-20.0,"lon":133.5,"n": 1,"avg":1880,"std":300,"jlat":0.5,"jlon":0.5},
    }
    base_wage = WAGE_IDX[ALL_QUARTERS[0]]
    base_cpi  = CPI_IDX[ALL_QUARTERS[0]]
    rows, emp_id = [], 1
    for state, cfg in state_cfg.items():
        n = cfg["n"]
        base_wages     = np.random.normal(cfg["avg"], cfg["std"], n).clip(800, 4500).round()
        lats           = (cfg["lat"] + np.random.uniform(-cfg["jlat"], cfg["jlat"], n)).round(3)
        lons           = (cfg["lon"] + np.random.uniform(-cfg["jlon"], cfg["jlon"], n)).round(3)
        indiv_modifier = np.random.uniform(0.88, 1.12, n)
        for i in range(n):
            bw = base_wages[i]
            for q in ALL_QUARTERS:
                wg_ratio  = WAGE_IDX[q] / base_wage
                nominal   = round(bw * wg_ratio * indiv_modifier[i])
                cpi_ratio = CPI_IDX[q] / base_cpi
                real      = round(nominal / cpi_ratio)
                pp_index  = round((wg_ratio * indiv_modifier[i]) / cpi_ratio * 100, 1)
                rows.append({
                    "employee_id":            f"EMP-{emp_id:03d}",
                    "state":                  state,
                    "lat":                    float(lats[i]),
                    "lon":                    float(lons[i]),
                    "quarter":                q,
                    "weekly_wage":            int(nominal),
                    "base_weekly_wage":       int(bw),
                    "real_weekly_wage":       int(real),
                    "purchasing_power_index": pp_index,
                    "cpi_yoy_pct":            CPI_YOY[q],
                    "wage_yoy_pct":           WAGE_YOY[q],
                    "real_wage_gap_pp":       round(WAGE_YOY[q] - CPI_YOY[q], 2),
                })
            emp_id += 1
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────
df         = load_main()
df_cpi_cat = load_cpi_categories()
df_states  = load_state_data()
df_biz     = load_business_indicators()
df_emp     = load_employee_map_data()

# ─────────────────────────────────────────────────────────────────
# SIDEBAR  — all widgets declared here, values used inside tabs
# FIX: all filter variables computed BEFORE tab blocks so Streamlit
# re-renders tabs correctly on any sidebar change.
# ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🇦🇺 Cost of Living")
st.sidebar.caption("Australia · ABS Data · 2021–2025")
st.sidebar.divider()

st.sidebar.markdown("**Filters**")
ALL_STATES = df_states["state"].tolist()
selected_states = st.sidebar.multiselect(
    "States / Territories",
    options=ALL_STATES,
    default=ALL_STATES,
)
# Guard: if nothing selected, show all
if not selected_states:
    selected_states = ALL_STATES

show_essential_only = st.sidebar.toggle("Essential categories only", value=False)

st.sidebar.divider()
st.sidebar.markdown("**Workforce Map**")
w_min = int(df_emp["base_weekly_wage"].min())
w_max = int(df_emp["base_weekly_wage"].max())
salary_range = st.sidebar.slider(
    "Base weekly wage ($)",
    min_value=w_min, max_value=w_max,
    value=(w_min, w_max), step=50,
)

# Quarter selector for map (FIX: replaces animation_frame to avoid caching bug)
map_quarter = st.sidebar.select_slider(
    "Map quarter",
    options=ALL_QUARTERS,
    value="2022Q4",   # default = peak crisis
)

st.sidebar.divider()
st.sidebar.markdown("**What-if: Relief Package**")
relief_amount = st.sidebar.slider("Annual relief per employee ($)", 0, 3000, 1500, 100)
num_employees = st.sidebar.number_input("Employees covered", min_value=10, max_value=100000, value=500, step=50)

# ── Pre-compute all filtered datasets (outside tabs = always fresh) ──
# Tab 1
filtered_cat = (
    df_cpi_cat if not show_essential_only
    else df_cpi_cat[~df_cpi_cat["discretionary"]]
).sort_values("cpi_change", ascending=True).copy()

essential_above = filtered_cat[
    (~filtered_cat["discretionary"]) & (filtered_cat["cpi_change"] > 3.4)
]["category"].tolist()

# Tab 2
df_sf = df_states[df_states["state"].isin(selected_states)].copy()

df_emp_f = df_emp[
    df_emp["state"].isin(selected_states) &
    (df_emp["quarter"] == map_quarter) &
    (df_emp["base_weekly_wage"] >= salary_range[0]) &
    (df_emp["base_weekly_wage"] <= salary_range[1])
].copy()

neg_states = df_sf[df_sf["real_change_pct"] < 0]["state"].tolist()

# Tab 3 — What-if calculations
TURNOVER_COST     = 55000
PRODUCTIVITY_LOSS = 3400
STRESSED_PCT      = 0.33
AVG_WEEKLY        = 1750
TRANSPORT_SHARE   = 0.40
GROCERY_SHARE     = 0.33
ENERGY_SHARE      = 0.27

total_pkg_cost      = relief_amount * num_employees
retentions_gained   = num_employees * STRESSED_PCT * 0.20
turnover_saving     = retentions_gained * TURNOVER_COST
productivity_saving = num_employees * STRESSED_PCT * PRODUCTIVITY_LOSS
net_benefit         = turnover_saving + productivity_saving - total_pkg_cost
roi_ratio           = (turnover_saving + productivity_saving) / total_pkg_cost if total_pkg_cost > 0 else 0.0


# ─────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📉  The Gap",
    "👷  Human Cost",
    "💡  What If?",
])


# ═══════════════════════════════════════════════════════════════
# TAB 1 — THE GAP
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="page-h">Your employees are earning more — and affording less.</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">ABS data 2021–2025 · Real wage gap peaked at −4.5 percentage points in 2022.</div>', unsafe_allow_html=True)

    latest    = df.iloc[-1]
    peak_gap  = df["real_wage_gap_yoy"].min()
    trough_pp = df["purchasing_power_index"].min()
    gap_series = df["real_wage_gap_yoy"].dropna()
    latest_gap = gap_series.iloc[-1] if not gap_series.empty else 0.0
    gap_sign   = "+" if latest_gap >= 0 else ""

    cpi_val  = latest["cpi_yoy_pct"]
    wage_val = latest["wage_yoy_pct"]

    col_h, col1, col2, col3 = st.columns([1.5, 1, 1, 1])
    col_h.markdown(kpi(
        "Real Wage Gap — Latest quarter",
        f"{gap_sign}{latest_gap:.2f}pp",
        f"Peak deficit: −{abs(peak_gap):.1f}pp (2022Q4)",
        style="hero" if latest_gap >= 0 else "alert",
    ), unsafe_allow_html=True)
    col1.markdown(kpi(
        "CPI Inflation (YoY)",
        f"{cpi_val:.1f}%" if pd.notna(cpi_val) else "—",
        f'<span class="d-dn">▲ inflation pressure</span>',
    ), unsafe_allow_html=True)
    col2.markdown(kpi(
        "Wage Growth (YoY)",
        f"{wage_val:.2f}%" if pd.notna(wage_val) else "—",
        f'<span class="d-up">▲ ahead of CPI now</span>',
    ), unsafe_allow_html=True)
    col3.markdown(kpi(
        "Purchasing Power — Trough",
        f"{trough_pp:.1f}",
        f'<span class="d-dn">▼ vs 100 baseline (2021Q1)</span>',
    ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart row ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="chart-title">CPI vs Wage Growth — Year-on-Year % (2021–2025)</p>', unsafe_allow_html=True)
        df_yoy = df.dropna(subset=["cpi_yoy_pct","wage_yoy_pct"]).copy()

        fig1 = go.Figure()
        # Shaded gap area
        fig1.add_trace(go.Scatter(
            x=df_yoy["quarter_label"], y=df_yoy["cpi_yoy_pct"],
            name="CPI (inflation)", mode="lines+markers",
            line=dict(color=RED, width=2.5), marker=dict(size=6),
        ))
        fig1.add_trace(go.Scatter(
            x=df_yoy["quarter_label"], y=df_yoy["wage_yoy_pct"],
            name="Wage growth", mode="lines+markers",
            line=dict(color=GREEN, width=2.5), marker=dict(size=6),
            fill="tonexty", fillcolor="rgba(192,57,10,0.10)",
        ))
        fig1.add_annotation(
            x="2022Q4", y=7.8,
            text="Peak gap: −4.5pp",
            showarrow=True, arrowhead=2, arrowcolor=RED,
            font=dict(size=12, color=RED, family=_FONT), ax=45, ay=-28,
        )
        fig1.update_layout(**base_layout(270))
        fig1.update_yaxes(showgrid=True, gridcolor=_GRID, ticksuffix="%", tickfont=dict(size=12))
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown('<p class="chart-title">Purchasing Power Index (base = 2021Q1 = 100)</p>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_hrect(
            y0=float(df["purchasing_power_index"].min()) - 0.5, y1=100,
            fillcolor="rgba(192,57,10,0.07)", layer="below", line_width=0,
        )
        fig2.add_hline(
            y=100, line_dash="dash", line_color=GRAY, line_width=1.5,
            annotation_text="Baseline (2021Q1)",
            annotation_font=dict(size=12, family=_FONT, color=GRAY),
            annotation_position="top left",
        )
        pp_vals = df["purchasing_power_index"].tolist()
        fig2.add_trace(go.Scatter(
            x=df["quarter_label"], y=pp_vals,
            mode="lines+markers",
            line=dict(color=GREEN, width=2.5),
            marker=dict(size=7, color=[RED if v < 100 else GREEN for v in pp_vals]),
            showlegend=False,
        ))
        trough_idx = df["purchasing_power_index"].idxmin()
        fig2.add_annotation(
            x=df.loc[trough_idx,"quarter_label"],
            y=df.loc[trough_idx,"purchasing_power_index"],
            text=f"Trough: {df.loc[trough_idx,'purchasing_power_index']:.1f}",
            showarrow=True, arrowhead=2, arrowcolor=RED,
            font=dict(size=12, color=RED, family=_FONT), ax=45, ay=28,
        )
        fig2.update_layout(**base_layout(270), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # ── CPI by category (responds to show_essential_only) ──
    st.markdown('<p class="chart-title">CPI Change by Expenditure Category — Annual %, 2024</p>', unsafe_allow_html=True)

    fig3 = px.bar(
        filtered_cat, x="cpi_change", y="category", orientation="h",
        color="discretionary",
        color_discrete_map={True: AMBER, False: RED},
        labels={"cpi_change": "Annual CPI change (%)", "category": "", "discretionary": "Discretionary"},
        text="cpi_change",
    )
    fig3.add_vline(
        x=3.4, line_dash="dash", line_color=GREEN, line_width=2,
        annotation_text="Wage growth 3.4%",
        annotation_font=dict(size=12, color=GREEN, family=_FONT),
        annotation_position="top right",
    )
    fig3.update_traces(
        texttemplate="%{text:.1f}%", textposition="outside",
        textfont=dict(size=13, color="#111110"),
    )
    fig3.update_layout(
        **base_layout(260, hmode="y unified"),
        margin=dict(t=12, b=12, l=12, r=70),
        legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="left", x=0,
                    title_text="", font=dict(size=12)),
    )
    fig3.update_xaxes(showgrid=True, gridcolor=_GRID)
    fig3.update_yaxes(tickfont=dict(size=13))
    st.plotly_chart(fig3, use_container_width=True)

    # Dynamic narrative — updates with toggle
    if essential_above:
        st.markdown(
            f'<div class="callout-warn">⚠️ <strong>{len(essential_above)} essential categories</strong> '
            f'exceeded wage growth: <strong>{", ".join(essential_above)}</strong>. '
            'Workers cannot opt out of these costs.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="callout">✅ In the filtered view, no essential category exceeded wage growth.</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════
# TAB 2 — HUMAN COST
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="page-h">Financial stress doesn\'t stay at home — it shows up at work.</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">The cost of inaction is already measurable in productivity, absenteeism, and turnover.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown(kpi("Workers Under Financial Stress", "1 in 3",
                      "nationally · APA 2024", style="alert"), unsafe_allow_html=True)
    col2.markdown(kpi("Productivity Loss / Stressed Worker", "$3,400 / yr",
                      f'<span class="d-dn">▼ per annum · APA 2024</span>'), unsafe_allow_html=True)
    col3.markdown(kpi("Employee Replacement Cost", "$40K–$80K",
                      f'<span class="d-neu">AHRI estimate</span>'), unsafe_allow_html=True)

    if neg_states:
        st.markdown(
            f'<div class="callout-warn">⚠️ <strong>{", ".join(neg_states)}</strong>: '
            'real retail spending is <strong>negative</strong> — workers in these states are buying less in real terms.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)

    # Chart: Nominal vs Real retail by state (responds to selected_states)
    with col_a:
        st.markdown('<p class="chart-title">Retail Turnover: Nominal vs Real (2024)</p>', unsafe_allow_html=True)
        df_sm = df_sf.sort_values("real_change_pct", ascending=True)
        fig_ret = go.Figure()
        fig_ret.add_trace(go.Bar(
            y=df_sm["state"], x=df_sm["retail_change_pct"],
            name="Nominal", orientation="h",
            marker_color=BLUE, opacity=0.6,
            text=[f"{v:+.1f}%" for v in df_sm["retail_change_pct"]],
            textposition="outside", textfont=dict(size=12),
        ))
        fig_ret.add_trace(go.Bar(
            y=df_sm["state"], x=df_sm["real_change_pct"],
            name="Real (infl. adj.)", orientation="h",
            marker_color=[RED if v < 0 else GREEN for v in df_sm["real_change_pct"]],
            text=[f"{v:+.1f}%" for v in df_sm["real_change_pct"]],
            textposition="outside", textfont=dict(size=12),
        ))
        fig_ret.add_vline(x=0, line_color=GRAY, line_width=1)
        fig_ret.update_layout(
            **base_layout(280, hmode="y unified"),
            barmode="group",
            margin=dict(t=12, b=12, l=12, r=50),
        )
        fig_ret.update_xaxes(showgrid=True, gridcolor=_GRID)
        fig_ret.update_yaxes(tickfont=dict(size=13))
        st.plotly_chart(fig_ret, use_container_width=True)

    # Chart: Avg weekly earnings by state (responds to selected_states)
    with col_b:
        st.markdown('<p class="chart-title">Avg Weekly Earnings by State</p>', unsafe_allow_html=True)
        df_earn = df_sf.sort_values("avg_weekly_earnings")
        fig_earn = px.bar(
            df_earn, x="avg_weekly_earnings", y="state", orientation="h",
            color="real_change_pct",
            color_continuous_scale=[[0, RED],[0.5,"#F5E6A0"],[1, GREEN]],
            text="avg_weekly_earnings",
        )
        fig_earn.update_traces(
            texttemplate="$%{text:,.0f}", textposition="outside",
            textfont=dict(size=12),
        )
        fig_earn.update_layout(
            **base_layout(280),
            margin=dict(t=12, b=12, l=12, r=90),
            showlegend=False, coloraxis_showscale=False,
        )
        fig_earn.update_yaxes(tickfont=dict(size=13))
        st.plotly_chart(fig_earn, use_container_width=True)

    # Chart: Business indicators
    with col_c:
        st.markdown('<p class="chart-title">Business Costs vs Surplus (Index 2024Q1=100)</p>', unsafe_allow_html=True)
        fig_biz_c = go.Figure()
        fig_biz_c.add_trace(go.Scatter(
            x=df_biz["quarter"], y=df_biz["input_costs"],
            name="Input costs", mode="lines+markers",
            line=dict(color=RED, width=2.5), marker=dict(size=6),
        ))
        fig_biz_c.add_trace(go.Scatter(
            x=df_biz["quarter"], y=df_biz["wages_bill"],
            name="Wages bill", mode="lines+markers",
            line=dict(color=AMBER, width=2.5), marker=dict(size=6),
        ))
        fig_biz_c.add_trace(go.Scatter(
            x=df_biz["quarter"], y=df_biz["gross_surplus"],
            name="Gross surplus", mode="lines+markers",
            line=dict(color=GREEN, width=2.5), marker=dict(size=6),
        ))
        fig_biz_c.update_layout(**base_layout(280))
        fig_biz_c.update_yaxes(showgrid=True, gridcolor=_GRID, tickfont=dict(size=12))
        fig_biz_c.update_xaxes(tickfont=dict(size=12))
        st.plotly_chart(fig_biz_c, use_container_width=True)

    # ── Workforce map (responds to selected_states + salary_range + map_quarter) ──
    st.markdown(
        f'<p class="chart-title">Workforce Purchasing Power Map — {map_quarter}'
        ' &nbsp;·&nbsp; Filter state, salary band, and quarter in sidebar</p>',
        unsafe_allow_html=True,
    )

    if df_emp_f.empty:
        st.warning("No employees match the selected filters. Adjust states or salary range in the sidebar.")
    else:
        emp_colorscale = [[0.00, RED],[0.35, "#F4A07A"],[0.65,"#FFF3E0"],[0.85,"#6ECBA8"],[1.00, GREEN]]
        fig_map = px.scatter_mapbox(
            df_emp_f,
            lat="lat", lon="lon",
            color="purchasing_power_index",
            hover_name="employee_id",
            custom_data=["state","weekly_wage","real_weekly_wage",
                         "cpi_yoy_pct","wage_yoy_pct","purchasing_power_index","base_weekly_wage"],
            color_continuous_scale=emp_colorscale,
            range_color=[88, 112],
            zoom=3.3,
            center=dict(lat=-27, lon=133.5),
            mapbox_style="carto-positron",
            labels={"purchasing_power_index": "PP Index"},
        )
        fig_map.update_traces(
            marker=dict(size=10, opacity=0.90),
            hovertemplate=(
                "<b>%{hovertext}</b> · %{customdata[0]}<br>"
                "Base: <b>$%{customdata[6]:,}/wk</b> → Nominal: <b>$%{customdata[1]:,}/wk</b><br>"
                "Real (adj.): <b>$%{customdata[2]:,}/wk</b><br>"
                "CPI YoY: <b>%{customdata[3]:.1f}%</b> · Wage: <b>%{customdata[4]:.1f}%</b><br>"
                "PP Index: <b>%{customdata[5]:.1f}</b>"
                "<extra></extra>"
            ),
        )
        fig_map.update_layout(
            height=380, margin=dict(t=0,b=0,l=0,r=0),
            paper_bgcolor=WHITE,
            font=dict(family=_FONT, size=13),
            coloraxis_colorbar=dict(
                title="PP Index", thickness=14, len=0.65,
                tickvals=[88,94,100,106,112],
                ticktext=["88","94","100","106","112"],
                tickfont=dict(size=12, family=_FONT),
                title_font=dict(size=13, family=_FONT),
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# TAB 3 — WHAT IF?
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="page-h">What if we acted?</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Adjust the relief package in the sidebar — every chart updates in real time.</div>', unsafe_allow_html=True)

    roi_style = "hero" if roi_ratio >= 1 else "alert"
    roi_sub   = f"${roi_ratio:.1f} returned per $1 spent" if roi_ratio >= 1 else "below breakeven — adjust parameters"

    col_h, col1, col2, col3 = st.columns([1.5, 1, 1, 1])
    col_h.markdown(kpi("ROI Ratio", f"{roi_ratio:.1f}×", roi_sub, style=roi_style), unsafe_allow_html=True)
    col1.markdown(kpi("Total Package Cost",   f"${total_pkg_cost:,.0f}"), unsafe_allow_html=True)
    col2.markdown(kpi("Est. Turnover Saving", f"${turnover_saving:,.0f}",
                      f'<span class="d-up">▲ est. retention uplift</span>'), unsafe_allow_html=True)
    col3.markdown(kpi("Est. Productivity Saving", f"${productivity_saving:,.0f}",
                      f'<span class="d-up">▲ per annum</span>'), unsafe_allow_html=True)

    if roi_ratio >= 2:
        st.markdown(
            f'<div class="callout">✅ At <strong>${relief_amount:,}/employee</strong> covering '
            f'<strong>{num_employees:,} employees</strong>, the package returns '
            f'<strong>${roi_ratio:.1f} for every $1 spent</strong>. This is not a cost — it\'s an investment.</div>',
            unsafe_allow_html=True,
        )
    elif roi_ratio >= 1:
        st.markdown(
            '<div class="callout-warn">The package breaks even at this configuration. '
            'Increase coverage or relief amount to improve ROI.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="callout-warn">⚠️ Below breakeven at current settings. Adjust parameters in the sidebar.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="chart-title">Projected Purchasing Power — With vs Without Relief</p>', unsafe_allow_html=True)
        quarters_proj = list(df["quarter_label"]) + ["2025Q3","2025Q4","2026Q1","2026Q2"]
        pp_actual  = list(df["purchasing_power_index"])
        n_actual   = len(pp_actual)

        baseline_proj = pp_actual.copy()
        for _ in range(4):
            baseline_proj.append(round(baseline_proj[-1] * 0.998, 2))

        boost_pct   = (relief_amount / 52) / AVG_WEEKLY * 100
        relief_proj = pp_actual.copy()
        for _ in range(4):
            relief_proj.append(round(relief_proj[-1] * (1 + boost_pct / 400), 2))

        fig_proj = go.Figure()
        fig_proj.add_hrect(y0=101.0, y1=102.5,
                           fillcolor="rgba(10,138,85,0.08)", layer="below", line_width=0)
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[:n_actual], y=pp_actual,
            name="Actual", mode="lines+markers",
            line=dict(color=GRAY, width=2), marker=dict(size=5),
        ))
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[n_actual-1:], y=baseline_proj[n_actual-1:],
            name="No relief (projected)", mode="lines",
            line=dict(color=RED, width=2.5, dash="dot"),
        ))
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[n_actual-1:], y=relief_proj[n_actual-1:],
            name="With relief (projected)", mode="lines",
            fill="tonexty", fillcolor="rgba(10,138,85,0.08)",
            line=dict(color=GREEN, width=2.5),
        ))
        fig_proj.add_shape(
            type="line",
            x0=quarters_proj[n_actual-1], x1=quarters_proj[n_actual-1],
            y0=0, y1=1, xref="x", yref="paper",
            line=dict(color=PURPLE, width=2, dash="dash"),
        )
        fig_proj.add_annotation(
            x=quarters_proj[n_actual-1], y=1, yref="paper",
            text="  Now", showarrow=False, xanchor="left",
            font=dict(size=13, family=_FONT, color=PURPLE),
        )
        fig_proj.update_layout(**base_layout(320))
        fig_proj.update_yaxes(showgrid=True, gridcolor=_GRID, tickfont=dict(size=12))
        fig_proj.update_xaxes(tickfont=dict(size=12))
        st.plotly_chart(fig_proj, use_container_width=True)

    with col_b:
        st.markdown('<p class="chart-title">Cost vs Saving — Waterfall</p>', unsafe_allow_html=True)
        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute","relative","relative","total"],
            x=["Package cost","Turnover saving","Productivity saving","Net benefit"],
            y=[-total_pkg_cost, turnover_saving, productivity_saving, net_benefit],
            connector=dict(line=dict(color=LGRAY, width=1)),
            decreasing=dict(marker_color=RED),
            increasing=dict(marker_color=GREEN),
            totals=dict(marker_color=PURPLE),
            text=[
                f"-${total_pkg_cost:,.0f}",
                f"+${turnover_saving:,.0f}",
                f"+${productivity_saving:,.0f}",
                f"${net_benefit:,.0f}",
            ],
            textposition="outside",
            textfont=dict(size=13, color="#111110", family=_FONT),
        ))
        fig_wf.update_layout(**base_layout(320, hmode="closest"), showlegend=False)
        fig_wf.update_xaxes(tickfont=dict(size=13))
        fig_wf.update_yaxes(title="AUD ($)", showgrid=True, gridcolor=_GRID)
        st.plotly_chart(fig_wf, use_container_width=True)

    # ── Package breakdown ──
    st.markdown('<p class="chart-title">Suggested Relief Package Composition</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.markdown(kpi("Transport Subsidy",
                      f"${relief_amount*TRANSPORT_SHARE:,.0f} / yr",
                      "40% of package · commuting costs"), unsafe_allow_html=True)
    col2.markdown(kpi("Grocery Allowance",
                      f"${relief_amount*GROCERY_SHARE:,.0f} / yr",
                      "33% of package · tax-effective vouchers"), unsafe_allow_html=True)
    col3.markdown(kpi("Energy Bill Offset",
                      f"${relief_amount*ENERGY_SHARE:,.0f} / yr",
                      "27% of package · highest CPI category"), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="font-size:12px;color:#5A574F;text-align:center;font-family:\'Inter\',sans-serif">'
    "Sources: ABS Cat. 6401.0 (CPI) · 6345.0 (WPI) · 8501.0 (Retail Trade) · 5676.0 (Business Indicators) "
    "· AHRI · APA Financial Wellbeing Report 2024. Employee map is simulated for illustrative purposes."
    "</p>",
    unsafe_allow_html=True,
)
