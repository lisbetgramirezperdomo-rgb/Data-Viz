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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, label, p, div {
    font-family: 'Inter', sans-serif !important;
}
.stApp { background-color: #f8f7f4; }
[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e8e6df; }

/* Uniform KPI card base */
.kpi-card {
    border-radius: 8px;
    padding: 10px 14px;
    height: 100%;
    box-sizing: border-box;
    min-height: 82px;
}
.kpi-card .k-lbl {
    font-size: 10px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; font-family: 'Inter', sans-serif;
    margin-bottom: 4px; line-height: 1.3;
}
.kpi-card .k-val {
    font-size: 22px; font-weight: 700;
    font-family: 'Inter', sans-serif; line-height: 1.1;
}
.kpi-card .k-sub {
    font-size: 11px; font-family: 'Inter', sans-serif; margin-top: 3px;
}
/* Variants */
.kpi-default { background:#ffffff; border:0.5px solid #dddbd2; }
.kpi-default .k-lbl { color:#888780; }
.kpi-default .k-val { color:#1A1A18; }
.kpi-default .k-sub { color:#888780; }
.kpi-hero { background:#1D3A2F; border:none; }
.kpi-hero .k-lbl { color:#7FCDB0; }
.kpi-hero .k-val { color:#ffffff; font-size:26px; }
.kpi-hero .k-sub { color:#A8D8C8; }
.kpi-alert { background:#3D1E0F; border:none; }
.kpi-alert .k-lbl { color:#E8A87C; }
.kpi-alert .k-val { color:#ffffff; font-size:26px; }
.kpi-alert .k-sub { color:#D4956A; }

/* Delta indicators */
.d-up   { color:#1D9E75; font-size:11px; }
.d-down { color:#D85A30; font-size:11px; }
.d-neu  { color:#888780; font-size:11px; }

.chart-title {
    font-size: 10px; font-weight: 600; letter-spacing: 0.09em;
    color: #aaa8a2; text-transform: uppercase; margin-bottom: 2px;
    font-family: 'Inter', sans-serif;
}
.block-container { padding-top: 0.6rem !important; padding-bottom: 0.2rem !important; }
[data-testid="stTabs"] { margin-top: 2rem; }
/* Tab pill navigation */
[data-baseweb="tab-list"] {
    background: #1D3A2F !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #7FCDB0 !important;
    border-radius: 6px !important;
    padding: 7px 20px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    border: none !important;
}
[data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #ffffff !important;
    color: #1D3A2F !important;
}
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
}
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Palette & shared layout ────────────────────────────────────────
CORAL  = "#D85A30"
TEAL   = "#1D9E75"
AMBER  = "#BA7517"
PURPLE = "#7F77DD"
BLUE   = "#378ADD"
GRAY   = "#888780"
_FONT  = "Inter, sans-serif"
_GRID  = "#f0ede6"

BASE_LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family=_FONT, size=11, color="#2C2C2A"),
)
_M  = dict(t=8, b=8, l=8, r=8)     # default margin
_ML = dict(t=8, b=8, l=8, r=100)   # right margin for labels


def kpi(label, value, sub="", style="default"):
    sub_html = f'<div class="k-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card kpi-{style}">'
        f'<div class="k-lbl">{label}</div>'
        f'<div class="k-val">{value}</div>'
        f'{sub_html}</div>'
    )


# ── Shared index constants (used by both loaders) ──────────────────
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
_HIST_Q = list(WAGE_IDX.keys())[:12]


@st.cache_data
def load_main():
    hist = pd.DataFrame({
        "quarter":       _HIST_Q,
        "quarter_label": _HIST_Q,
        "quarter_end": [
            "2021-03-31","2021-06-30","2021-09-30","2021-12-31",
            "2022-03-31","2022-06-30","2022-09-30","2022-12-31",
            "2023-03-31","2023-06-30","2023-09-30","2023-12-31",
        ],
        "year":        [2021]*4+[2022]*4+[2023]*4,
        "quarter_num": [1,2,3,4]*3,
        "cpi_index":   [CPI_IDX[q] for q in _HIST_Q],
        "wage_index":  [WAGE_IDX[q] for q in _HIST_Q],
        "cpi_qoq_pct":  [0.6,0.9,0.8,1.0,2.0,3.4,1.8,0.9,0.3,0.3,0.3,0.3],
        "cpi_yoy_pct":  [CPI_YOY[q] for q in _HIST_Q],
        "wage_qoq_pct": [0.5,0.7,0.6,0.7,0.6,0.8,1.1,1.0,1.3,1.7,1.6,1.5],
        "wage_yoy_pct": [WAGE_YOY[q] for q in _HIST_Q],
        "real_wage_gap_yoy": [0.3,-2.1,-1.1,-1.2,-2.7,-3.5,-4.2,-4.5,-3.3,-2.3,-1.4,0.1],
        "wage_to_cpi_ratio": [1.560,1.557,1.553,1.549,1.528,1.490,1.478,1.481,1.495,1.516,1.535,1.554],
        "purchasing_power_index": [99.10,98.88,98.66,98.37,97.05,94.62,93.91,94.06,94.98,96.29,97.53,98.70],
        "retail_turnover_quarterly":   [90000]*12,
        "retail_turnover_monthly_avg": [30000]*12,
        "months_in_quarter":           [3]*12,
        "retail_qoq_pct": [None]*12,
        "retail_yoy_pct": [None]*12,
    })
    recent = pd.read_csv("combined_data-2024.csv")
    recent["quarter_end"] = pd.to_datetime(recent["quarter_end"])
    hist["quarter_end"]   = pd.to_datetime(hist["quarter_end"])
    df = pd.concat([hist, recent], ignore_index=True).sort_values("quarter_end").reset_index(drop=True)
    for qtr, vals in {
        "2024Q1":{"cpi_yoy_pct":3.6,"wage_yoy_pct":4.1,"real_wage_gap_yoy":0.5},
        "2024Q2":{"cpi_yoy_pct":3.8,"wage_yoy_pct":4.0,"real_wage_gap_yoy":0.2},
        "2024Q3":{"cpi_yoy_pct":2.8,"wage_yoy_pct":3.6,"real_wage_gap_yoy":0.8},
        "2024Q4":{"cpi_yoy_pct":2.4,"wage_yoy_pct":3.5,"real_wage_gap_yoy":1.1},
    }.items():
        mask = df["quarter_label"] == qtr
        for col, val in vals.items():
            df.loc[mask, col] = val
    return df


@st.cache_data
def load_cpi_categories():
    quarters = list(WAGE_IDX.keys())  # 2021Q1 → 2025Q2 (18 quarters)
    # Cumulative % change from 2021Q1 baseline, one value per quarter per category.
    # Based on ABS category-level CPI trajectories; electricity/gas reflects the
    # 2022-23 energy crisis + gov relief offsets; transport mirrors fuel price volatility.
    cfg = [
        ("Housing",                        False, [0,0.5,1.1,1.9,3.2,5.0,6.8,8.5,10.0,11.4,12.6,13.6,14.7,15.8,16.7,17.6,18.5,19.2]),
        ("Electricity & gas",              False, [0,0.3,0.5,1.0,2.5,8.0,15.0,22.0,30.0,36.0,40.0,43.0,45.0,46.5,47.5,48.2,49.0,49.5]),
        ("Food & non-alcoholic beverages", False, [0,0.5,1.0,1.5,2.5,4.5,7.0,9.5,12.0,13.5,14.5,15.0,15.5,16.0,16.4,16.7,17.0,17.2]),
        ("Insurance & fin. services",      False, [0,0.8,1.5,2.2,3.5,5.5,8.0,10.5,13.0,15.5,17.5,19.0,20.5,22.0,23.2,24.2,25.0,25.6]),
        ("Health",                         False, [0,0.4,0.8,1.2,1.8,2.5,3.3,4.2,5.0,5.8,6.5,7.0,7.5,8.0,8.5,8.9,9.2,9.4]),
        ("Transport",                      False, [0,0.8,1.5,2.0,4.0,7.5,11.0,13.0,13.5,13.0,12.5,12.0,12.5,13.0,13.5,13.8,14.0,14.2]),
        ("Alcohol & tobacco",              True,  [0,0.6,1.3,2.0,3.2,5.0,7.0,9.0,11.0,12.8,14.2,15.5,16.7,17.8,18.7,19.5,20.3,21.0]),
        ("Education",                      False, [0,0.3,0.8,1.5,2.5,4.0,5.5,7.0,8.5,10.0,11.0,12.0,13.0,14.0,14.8,15.4,15.9,16.2]),
        ("Recreation & culture",           True,  [0,0.2,0.4,0.5,0.8,1.2,1.8,2.5,3.2,3.8,4.2,4.5,4.8,5.0,5.2,5.4,5.6,5.7]),
        ("Clothing & footwear",            True,  [0,0.1,0.2,0.1,0.3,0.5,0.7,0.6,0.5,0.5,0.7,0.8,1.0,1.2,1.4,1.5,1.7,1.8]),
    ]
    rows = []
    for q_idx, q in enumerate(quarters):
        for cat, disc, vals in cfg:
            rows.append({"quarter": q, "category": cat,
                         "cpi_change": vals[q_idx], "discretionary": disc})
    return pd.DataFrame(rows)


@st.cache_data
def load_state_data():
    return pd.DataFrame({
        "state": ["NSW","VIC","QLD","WA","SA","TAS","ACT","NT"],
        "retail_change_pct": [4.8,3.9,6.1,7.2,4.3,2.1,3.5,5.8],
        "real_change_pct":   [1.2,0.3,2.5,3.6,0.7,-1.5,-0.1,2.2],
        "avg_weekly_earnings": [1820,1750,1680,1950,1620,1490,2010,1880],
    })


@st.cache_data
def load_business_indicators():
    return pd.DataFrame({
        "quarter": ["2024Q1","2024Q2","2024Q3","2024Q4","2025Q1","2025Q2"],
        "input_costs":   [100.0,101.8,103.2,104.1,105.3,106.2],
        "gross_surplus": [100.0,100.6,100.9,101.0,101.2,101.3],
        "wages_bill":    [100.0,101.1,102.6,103.3,104.2,104.9],
    })


@st.cache_data
def load_employee_map_data():
    np.random.seed(42)
    state_cfg = {
        "NSW": {"lat":-33.0, "lon":147.0, "n":26,"avg":1820,"std":420,"jlat":2.5,"jlon":3.5},
        "VIC": {"lat":-37.2, "lon":144.5, "n":20,"avg":1750,"std":380,"jlat":1.5,"jlon":2.0},
        "QLD": {"lat":-22.5, "lon":144.5, "n":16,"avg":1680,"std":360,"jlat":4.5,"jlon":5.0},
        "WA":  {"lat":-26.0, "lon":121.0, "n": 9,"avg":1950,"std":430,"jlat":4.0,"jlon":5.5},
        "SA":  {"lat":-30.5, "lon":136.0, "n": 6,"avg":1620,"std":340,"jlat":2.5,"jlon":3.0},
        "TAS": {"lat":-42.0, "lon":146.5, "n": 2,"avg":1490,"std":280,"jlat":0.6,"jlon":0.8},
        "ACT": {"lat":-35.28,"lon":149.13,"n": 2,"avg":2010,"std":180,"jlat":0.1,"jlon":0.1},
        "NT":  {"lat":-20.0, "lon":133.5, "n": 1,"avg":1880,"std":300,"jlat":0.5,"jlon":0.5},
    }
    base_wage = WAGE_IDX["2021Q1"]
    base_cpi  = CPI_IDX["2021Q1"]
    quarters  = list(CPI_IDX.keys())
    rows = []
    emp_id = 1
    for state, cfg in state_cfg.items():
        n = cfg["n"]
        base_wages     = np.random.normal(cfg["avg"], cfg["std"], n).clip(800, 4500).round()
        lats           = (cfg["lat"] + np.random.uniform(-cfg["jlat"], cfg["jlat"], n)).round(3)
        lons           = (cfg["lon"] + np.random.uniform(-cfg["jlon"], cfg["jlon"], n)).round(3)
        indiv_modifier = np.random.uniform(0.88, 1.12, n)
        for i in range(n):
            bw = base_wages[i]
            for q in quarters:
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


df         = load_main()
df_cpi_cat = load_cpi_categories()
df_states  = load_state_data()
df_biz     = load_business_indicators()
df_emp     = load_employee_map_data()

# ── Sidebar ────────────────────────────────────────────────────────
st.sidebar.markdown("## 🇦🇺 Cost of Living Crisis")
st.sidebar.caption("Australia · ABS Data · 2021–2025")
st.sidebar.divider()

st.sidebar.markdown("**Filters**")
selected_states = st.sidebar.multiselect(
    "States / Territories",
    options=df_states["state"].tolist(),
    default=df_states["state"].tolist(),
)
show_essential_only = st.sidebar.toggle("Essential categories only", value=False)

st.sidebar.divider()
st.sidebar.markdown("**Workforce Map — Salary Band**")
w_min = int(df_emp["base_weekly_wage"].min())
w_max = int(df_emp["base_weekly_wage"].max())
salary_range = st.sidebar.slider(
    "Base weekly wage ($)",
    min_value=w_min, max_value=w_max,
    value=(w_min, w_max), step=50,
)

st.sidebar.divider()
st.sidebar.markdown("**What-if: Relief Package**")
relief_amount = st.sidebar.slider("Annual relief per employee ($)", 0, 3000, 1500, 100)
num_employees = st.sidebar.number_input("Employees covered", min_value=10, max_value=100000, value=500, step=50)

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

tab1, tab2, tab3 = st.tabs(["The Gap", "Human Cost", "What If?"])


# ══════════════════════════════════════════════════════════════════
# TAB 1 — THE GAP
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Your employees are earning more — and affording less.")

    latest      = df.iloc[-1]
    gap_series  = df["real_wage_gap_yoy"].dropna()
    latest_gap  = gap_series.iloc[-1] if not gap_series.empty else 0.0
    gap_sign    = "+" if latest_gap >= 0 else ""
    gap_style   = "hero" if latest_gap >= 0 else "alert"
    peak_gap    = df["real_wage_gap_yoy"].min()
    peak_gap_q  = df.loc[df["real_wage_gap_yoy"].idxmin(), "quarter_label"]
    trough_pp   = df["purchasing_power_index"].min()

    cpi_val   = latest["cpi_yoy_pct"]
    wage_val  = latest["wage_yoy_pct"]
    cpi_qoq   = latest["cpi_qoq_pct"]
    wage_qoq  = latest["wage_qoq_pct"]
    current_pp = latest["purchasing_power_index"]
    trough_q   = df.loc[df["purchasing_power_index"].idxmin(), "quarter_label"]

    # CPI: subir = malo (rojo), bajar = bueno (verde)
    if pd.notna(cpi_qoq):
        cpi_qoq_str = (
            f'<span class="d-down">▲ {cpi_qoq:.2f}% QoQ</span>' if cpi_qoq > 0
            else f'<span class="d-up">▼ {abs(cpi_qoq):.2f}% QoQ</span>'
        )
    else:
        cpi_qoq_str = ""

    # Salarios: subir = bueno (verde), bajar = malo (rojo)
    if pd.notna(wage_qoq):
        wage_qoq_str = (
            f'<span class="d-up">▲ {wage_qoq:.2f}% QoQ</span>' if wage_qoq > 0
            else f'<span class="d-down">▼ {abs(wage_qoq):.2f}% QoQ</span>'
        )
    else:
        wage_qoq_str = ""

    col_h, col1, col2, col3 = st.columns([1.4, 1, 1, 1])
    col_h.markdown(kpi(
        "Real Wage Gap — Latest",
        f"{gap_sign}{latest_gap:.2f}pp",
        f"Peak deficit: {abs(peak_gap):.1f}pp · {peak_gap_q}",
        style=gap_style,
    ), unsafe_allow_html=True)
    # Sparkline shows the full wage-gap trajectory beneath the hero KPI (P2.3)
    _sp_df    = df.dropna(subset=["real_wage_gap_yoy"])
    _sp_qs    = _sp_df["quarter_label"].tolist()
    _sp_vs    = _sp_df["real_wage_gap_yoy"].tolist()
    _sp_color = CORAL if latest_gap < 0 else TEAL
    _sp = go.Figure()
    _sp.add_trace(go.Scatter(
        x=_sp_qs, y=_sp_vs, mode="lines",
        line=dict(color=_sp_color, width=1.5), showlegend=False,
        hovertemplate="%{x}: %{y:+.2f}pp<extra></extra>",
    ))
    _sp.add_trace(go.Scatter(
        x=[_sp_qs[-1]], y=[_sp_vs[-1]],
        mode="markers", marker=dict(color=_sp_color, size=6),
        showlegend=False, hoverinfo="skip",
    ))
    _sp.add_hline(y=0, line_color=GRAY, line_width=0.8, line_dash="dot")
    _sp.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=2, b=2, l=4, r=4), height=68,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        hovermode="x unified",
    )
    col_h.plotly_chart(_sp, use_container_width=True, config={"displayModeBar": False})
    col1.markdown(kpi(
        "CPI Inflation (YoY)",
        f"{cpi_val:.1f}%" if pd.notna(cpi_val) else "—",
        cpi_qoq_str,
    ), unsafe_allow_html=True)
    col2.markdown(kpi(
        "Wage Growth (YoY)",
        f"{wage_val:.2f}%" if pd.notna(wage_val) else "—",
        wage_qoq_str,
    ), unsafe_allow_html=True)
    pp_cls   = "d-up"  if current_pp >= 100 else "d-down"
    pp_arrow = "▲" if current_pp >= 100 else "▼"
    col3.markdown(kpi(
        "Purchasing Power — Latest",
        f"{current_pp:.1f}",
        f'<span class="{pp_cls}">{pp_arrow} vs 100 baseline · trough {trough_pp:.1f} ({trough_q})</span>',
    ), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
    # Scrollytelling callout — guides the user into the animated chart below
    _ess_note = " Toggle <b>Essential categories only</b> in the sidebar to isolate unavoidable pressures." if not show_essential_only else " You are viewing <b>essential categories only</b> — housing, energy, food, and transport."
    st.markdown(
        f'<div style="background:#f0f8f5;border-left:3px solid {TEAL};'
        f'padding:8px 12px;border-radius:4px;margin:0 0 8px 0;'
        f'font-size:12px;color:#444;font-family:Inter,sans-serif;">'
        f'<b>How to read this:</b> Use the animated chart below to trace the crisis quarter by quarter. '
        f'The dashed teal line marks cumulative wage growth — any bar extending past it represents a category '
        f'where costs outpaced pay.{_ess_note}'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="chart-title">CPI vs Wage Growth — YoY % (2021–2025)</p>', unsafe_allow_html=True)
        df_yoy = df.dropna(subset=["cpi_yoy_pct","wage_yoy_pct"]).copy()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_yoy["quarter_label"], y=df_yoy["cpi_yoy_pct"],
            name="CPI (inflation)", mode="lines+markers",
            line=dict(color=CORAL, width=2.5), marker=dict(size=5),
        ))
        fig1.add_trace(go.Scatter(
            x=df_yoy["quarter_label"], y=df_yoy["wage_yoy_pct"],
            name="Wage growth", mode="lines+markers",
            line=dict(color=TEAL, width=2.5), marker=dict(size=5),
            fill="tonexty", fillcolor="rgba(216,90,48,0.10)",
        ))
        fig1.add_annotation(
            x="2022Q4", y=7.8, text="Peak gap: −4.5pp",
            showarrow=True, arrowhead=2, arrowcolor=CORAL,
            font=dict(size=10, color=CORAL, family=_FONT), ax=40, ay=-25,
        )
        fig1.update_layout(
            **BASE_LAYOUT, margin=_M,
            yaxis=dict(title="", showgrid=True, gridcolor=_GRID, ticksuffix="%"),
            legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="left", x=0,
                        bgcolor="rgba(255,255,255,0.85)", font=dict(size=10, family=_FONT),
                        borderwidth=0),
            height=245, hovermode="x unified",
        )
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown('<p class="chart-title">Purchasing Power Index (base = 2021Q1 = 100)</p>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_hrect(
            y0=float(df["purchasing_power_index"].min()) - 0.5, y1=100,
            fillcolor="rgba(216,90,48,0.06)", layer="below", line_width=0,
        )
        fig2.add_hline(
            y=100, line_dash="dash", line_color=GRAY,
            annotation_text="Baseline", annotation_position="top left",
            annotation_font=dict(size=10, family=_FONT),
        )
        pp_vals = df["purchasing_power_index"].tolist()
        fig2.add_trace(go.Scatter(
            x=df["quarter_label"], y=pp_vals,
            mode="lines+markers",
            line=dict(color=TEAL, width=2.5),
            marker=dict(size=6, color=[CORAL if v < 100 else TEAL for v in pp_vals]),
            showlegend=False,
        ))
        trough_idx = df["purchasing_power_index"].idxmin()
        fig2.add_annotation(
            x=df.loc[trough_idx,"quarter_label"],
            y=df.loc[trough_idx,"purchasing_power_index"],
            text=f"Trough: {df.loc[trough_idx,'purchasing_power_index']:.1f}",
            showarrow=True, arrowhead=2, arrowcolor=CORAL,
            font=dict(size=10, color=CORAL, family=_FONT), ax=40, ay=25,
        )
        fig2.update_layout(
            **BASE_LAYOUT, margin=_M,
            yaxis=dict(title="", showgrid=True, gridcolor=_GRID),
            height=245, hovermode="x unified",
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<p class="chart-title">CPI Cumulative Change by Expenditure Category — vs 2021Q1 Baseline</p>', unsafe_allow_html=True)

    # Fixed sort order (by last quarter values) so bars don't jump during animation
    last_q = df_cpi_cat["quarter"].max()
    df_last_q = df_cpi_cat[df_cpi_cat["quarter"] == last_q]
    if show_essential_only:
        df_last_q = df_last_q[~df_last_q["discretionary"]]
    cat_order = df_last_q.sort_values("cpi_change", ascending=True)["category"].tolist()

    filtered_cat = (
        df_cpi_cat if not show_essential_only
        else df_cpi_cat[~df_cpi_cat["discretionary"]]
    ).copy()
    filtered_cat["label"] = filtered_cat["cpi_change"].map(lambda v: f"+{v:.1f}%" if v > 0 else f"{v:.1f}%")

    x_max = filtered_cat["cpi_change"].max()

    fig3 = px.bar(
        filtered_cat, x="cpi_change", y="category", orientation="h",
        color="discretionary",
        color_discrete_map={True: AMBER, False: CORAL},
        animation_frame="quarter",
        animation_group="category",
        category_orders={"category": cat_order},
        labels={"cpi_change": "", "category": "", "discretionary": "Discretionary"},
        text="label",
        range_x=[0, x_max * 1.18],
    )
    fig3.update_traces(texttemplate="%{text}", textposition="outside")

    # Cumulative wage growth per quarter — used as animated reference line
    _base_w = WAGE_IDX["2021Q1"]
    wage_cum_by_q = {q: (WAGE_IDX[q] / _base_w - 1) * 100 for q in WAGE_IDX}

    def _wage_shape(wc):
        return dict(type="line", x0=wc, x1=wc, y0=0, y1=1,
                    xref="x", yref="paper",
                    line=dict(color=TEAL, width=1.5, dash="dash"))

    def _wage_annotation(wc):
        return dict(x=wc, y=1.0, xref="x", yref="paper",
                    text=f"Wages +{wc:.1f}%", showarrow=False,
                    xanchor="left", font=dict(size=9, color=TEAL, family=_FONT))

    for frame in fig3.frames:
        wc = wage_cum_by_q.get(frame.name, 0)
        frame.layout = go.Layout(shapes=[_wage_shape(wc)], annotations=[_wage_annotation(wc)])

    fig3.update_layout(
        **BASE_LAYOUT,
        height=340, margin=dict(t=8, b=8, l=8, r=65),
        shapes=[_wage_shape(0)],
        legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="left", x=0,
                    title_text="", bgcolor="rgba(255,255,255,0.85)",
                    font=dict(size=10, family=_FONT), borderwidth=0),
        hovermode="y unified",
        xaxis=dict(showgrid=True, gridcolor=_GRID, ticksuffix="%"),
        yaxis=dict(title=""),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 2 — HUMAN COST
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### The squeeze isn't just a household problem — it's a workforce problem.")

    latest_q = df_emp["quarter"].max()
    df_emp_latest = df_emp[df_emp["quarter"].eq(latest_q) & df_emp["state"].isin(selected_states)]
    affected_rate = (df_emp_latest["purchasing_power_index"] < 100).mean() if not df_emp_latest.empty else STRESSED_PCT
    affected_n    = int(round(affected_rate * num_employees))

    col1, col2, col3 = st.columns(3)
    col1.markdown(kpi("Financial Stress", f"{affected_n:,}",
                      f"employees with reduced purchasing power ({affected_rate:.0%})", style="alert"), unsafe_allow_html=True)
    col2.markdown(kpi("Productivity Loss / Stressed Worker", "$3,400 / yr",
                      '<span class="d-down">▼ per annum · APA 2024</span>'), unsafe_allow_html=True)
    col3.markdown(kpi("Employee Replacement Cost", "$40K–$80K",
                      '<span class="d-neu">AHRI estimate</span>'), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

    df_sf = df_states[df_states["state"].isin(selected_states)].copy()

    # Context-aware callout: updates every time state filter or employee count changes
    _sel_label  = (", ".join(selected_states) if len(selected_states) <= 4
                   else f"{len(selected_states)} states/territories")
    _worst_st   = (df_sf.loc[df_sf["real_change_pct"].idxmin(), "state"]
                   if not df_sf.empty else "—")
    st.markdown(
        f'<div style="background:#fff8f5;border-left:3px solid {CORAL};'
        f'padding:8px 12px;border-radius:4px;margin:0 0 8px 0;'
        f'font-size:12px;color:#444;font-family:Inter,sans-serif;">'
        f'Across <b>{_sel_label}</b>: an estimated <b>{affected_n:,}</b> of your '
        f'<b>{num_employees:,}</b> covered employees ({affected_rate:.0%}) '
        f'have lost real purchasing power in the latest quarter. '
        f'Real retail spending is most pressured in <b>{_worst_st}</b>. '
        f'Change the <b>States / Territories</b> or <b>Salary Band</b> filters in the sidebar '
        f'to explore specific workforce cohorts.'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown('<p class="chart-title">Retail Turnover: Nominal vs Real (2024)</p>', unsafe_allow_html=True)
        df_sm = df_sf.sort_values("real_change_pct", ascending=True)
        fig_ret = go.Figure()
        fig_ret.add_trace(go.Bar(
            y=df_sm["state"], x=df_sm["retail_change_pct"],
            name="Nominal", orientation="h",
            marker_color=BLUE, opacity=0.55,
            text=[f"{v:+.1f}%" for v in df_sm["retail_change_pct"]],
            textposition="outside",
        ))
        fig_ret.add_trace(go.Bar(
            y=df_sm["state"], x=df_sm["real_change_pct"],
            name="Real (infl. adj.)", orientation="h",
            marker_color=[CORAL if v < 0 else TEAL for v in df_sm["real_change_pct"]],
            text=[f"{v:+.1f}%" for v in df_sm["real_change_pct"]],
            textposition="outside",
        ))
        fig_ret.add_vline(x=0, line_color=GRAY, line_width=1)
        fig_ret.update_layout(
            **BASE_LAYOUT,
            barmode="group", height=255,
            margin=dict(t=8, b=8, l=8, r=45),
            legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="left", x=0,
                        title_text="", bgcolor="rgba(255,255,255,0.85)",
                        font=dict(size=9, family=_FONT), borderwidth=0),
            hovermode="y unified",
            xaxis=dict(title="", showgrid=True, gridcolor=_GRID, zeroline=False),
            yaxis=dict(title=""),
        )
        st.plotly_chart(fig_ret, use_container_width=True)

    with col_b:
        st.markdown('<p class="chart-title">Avg Weekly Earnings by State</p>', unsafe_allow_html=True)
        df_earn = df_sf.sort_values("avg_weekly_earnings")
        fig_earn = px.bar(
            df_earn, x="avg_weekly_earnings", y="state", orientation="h",
            color="real_change_pct",
            color_continuous_scale=["#E24B4A","#F5C4B3","#1D9E75"],
            text="avg_weekly_earnings",
        )
        fig_earn.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_earn.update_layout(
            **BASE_LAYOUT,
            height=255,
            margin=dict(t=8, b=8, l=8, r=95),
            showlegend=False, coloraxis_showscale=False,
            xaxis=dict(title=""), yaxis=dict(title=""),
        )
        st.plotly_chart(fig_earn, use_container_width=True)

    with col_c:
        st.markdown('<p class="chart-title">Business Costs vs Surplus</p>', unsafe_allow_html=True)
        fig_biz_c = go.Figure()
        fig_biz_c.add_trace(go.Scatter(
            x=df_biz["quarter"], y=df_biz["input_costs"],
            name="Input costs", mode="lines+markers",
            line=dict(color=CORAL, width=2), marker=dict(size=5),
        ))
        fig_biz_c.add_trace(go.Scatter(
            x=df_biz["quarter"], y=df_biz["wages_bill"],
            name="Wages bill", mode="lines+markers",
            line=dict(color=AMBER, width=2), marker=dict(size=5),
        ))
        fig_biz_c.add_trace(go.Scatter(
            x=df_biz["quarter"], y=df_biz["gross_surplus"],
            name="Surplus", mode="lines+markers",
            line=dict(color=TEAL, width=2), marker=dict(size=5),
        ))
        fig_biz_c.update_layout(
            **BASE_LAYOUT, margin=_M,
            yaxis=dict(title="", showgrid=True, gridcolor=_GRID),
            height=255,
            legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="left", x=0,
                        bgcolor="rgba(255,255,255,0.85)", font=dict(size=9, family=_FONT),
                        borderwidth=0),
            hovermode="x unified",
        )
        st.plotly_chart(fig_biz_c, use_container_width=True)

    st.markdown(
        '<p class="chart-title">Workforce Purchasing Power Map — By Quarter (2021–2025)'
        ' &nbsp;|&nbsp; Filter salary band in sidebar</p>',
        unsafe_allow_html=True,
    )

    df_emp_f = df_emp[
        df_emp["state"].isin(selected_states) &
        (df_emp["base_weekly_wage"] >= salary_range[0]) &
        (df_emp["base_weekly_wage"] <= salary_range[1])
    ].copy()

    emp_colorscale = [
        [0.00,"#D32F2F"],[0.32,CORAL],
        [0.65,"#FFF3E0"],[0.87,"#A5D6A7"],[1.00,TEAL],
    ]

    if df_emp_f.empty:
        st.info("No employees match the selected salary range and states.")
    else:
        fig_map = px.scatter_mapbox(
            df_emp_f,
            lat="lat", lon="lon",
            color="purchasing_power_index",
            animation_frame="quarter",
            hover_name="employee_id",
            custom_data=[
                "state","weekly_wage","real_weekly_wage",
                "cpi_yoy_pct","wage_yoy_pct","real_wage_gap_pp",
                "purchasing_power_index","base_weekly_wage",
            ],
            color_continuous_scale=emp_colorscale,
            range_color=[88, 112],
            zoom=3.3,
            center=dict(lat=-27, lon=133.5),
            mapbox_style="carto-positron",
            labels={"purchasing_power_index":"PP Index"},
        )
        fig_map.update_traces(
            marker=dict(size=9, opacity=0.88),
            hovertemplate=(
                "<b>%{hovertext}</b> · %{customdata[0]}<br>"
                "Base: <b>$%{customdata[7]:,}/wk</b> → Nominal: <b>$%{customdata[1]:,}/wk</b><br>"
                "Real (adj.): <b>$%{customdata[2]:,}/wk</b><br>"
                "CPI YoY: <b>%{customdata[3]:.1f}%</b> · Wage: <b>%{customdata[4]:.1f}%</b><br>"
                "PP Index: <b>%{customdata[6]:.1f}</b>"
                "<extra></extra>"
            ),
        )
        fig_map.update_layout(
            height=360,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor="white",
            font=dict(family=_FONT, size=11, color="#2C2C2A"),
            coloraxis_colorbar=dict(
                title="PP<br>Index",
                thickness=12, len=0.65,
                yanchor="middle", y=0.5,
                tickvals=[88,94,100,106,112],
                ticktext=["88","94","100","106","112"],
                tickfont=dict(size=9, family=_FONT),
                title_font=dict(size=10, family=_FONT),
            ),
        )
        with st.spinner("Rendering workforce map…"):
            st.plotly_chart(fig_map, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 3 — WHAT IF?
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### What if we acted?")

    roi_style = "hero" if roi_ratio >= 1 else "alert"
    roi_sub   = f"${roi_ratio:.1f} returned per $1 spent" if roi_ratio > 1 else "below breakeven — adjust parameters"

    col_h, col1, col2, col3 = st.columns([1.4, 1, 1, 1])
    col_h.markdown(kpi("ROI Ratio", f"{roi_ratio:.1f}×", roi_sub, style=roi_style),
                   unsafe_allow_html=True)
    col1.markdown(kpi("Total Package Cost", f"${total_pkg_cost:,.0f}"), unsafe_allow_html=True)
    col2.markdown(kpi("Turnover Saving", f"${turnover_saving:,.0f}",
                      '<span class="d-up">▲ est. retention uplift</span>'), unsafe_allow_html=True)
    col3.markdown(kpi("Productivity Saving", f"${productivity_saving:,.0f}",
                      '<span class="d-up">▲ est. per annum</span>'), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="chart-title">Projected Purchasing Power — With vs Without Relief</p>', unsafe_allow_html=True)
        quarters_proj = list(df["quarter_label"]) + ["2025Q3","2025Q4","2026Q1","2026Q2"]
        pp_actual  = list(df["purchasing_power_index"])
        n_actual   = len(pp_actual)

        baseline_proj = pp_actual.copy()
        for _ in range(4):
            baseline_proj.append(round(baseline_proj[-1] * 0.998, 2))

        relief_weekly = relief_amount / 52
        boost_pct     = (relief_weekly / AVG_WEEKLY) * 100
        relief_proj   = pp_actual.copy()
        for _ in range(4):
            relief_proj.append(round(relief_proj[-1] * (1 + boost_pct / 400), 2))

        fig_proj = go.Figure()
        fig_proj.add_hrect(y0=101.0, y1=102.5,
                           fillcolor="rgba(29,158,117,0.08)", layer="below", line_width=0)
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[:n_actual], y=pp_actual,
            name="Actual", mode="lines+markers",
            line=dict(color=GRAY, width=2), marker=dict(size=4),
        ))
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[n_actual-1:], y=baseline_proj[n_actual-1:],
            name="No relief", mode="lines",
            line=dict(color=CORAL, width=2, dash="dot"),
        ))
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[n_actual-1:], y=relief_proj[n_actual-1:],
            name="With relief", mode="lines",
            line=dict(color=TEAL, width=2.5),
            fill="tonexty", fillcolor="rgba(29,158,117,0.07)",
        ))
        fig_proj.add_shape(
            type="line",
            x0=quarters_proj[n_actual-1], x1=quarters_proj[n_actual-1],
            y0=0, y1=1, xref="x", yref="paper",
            line=dict(color=PURPLE, width=1.5, dash="dash"),
        )
        fig_proj.add_annotation(
            x=quarters_proj[n_actual-1], y=1, yref="paper",
            text="Now", showarrow=False, xanchor="left",
            font=dict(size=10, family=_FONT, color=PURPLE),
        )
        fig_proj.update_layout(
            **BASE_LAYOUT, margin=_M,
            yaxis=dict(title="", showgrid=True, gridcolor=_GRID),
            legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="left", x=0,
                        bgcolor="rgba(255,255,255,0.85)", font=dict(size=10, family=_FONT),
                        borderwidth=0),
            height=300, hovermode="x unified",
        )
        st.plotly_chart(fig_proj, use_container_width=True)

    with col_b:
        st.markdown('<p class="chart-title">Cost vs Saving — Waterfall</p>', unsafe_allow_html=True)
        fig_roi = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute","relative","relative","total"],
            x=["Package cost","Turnover saving","Productivity saving","Net benefit"],
            y=[-total_pkg_cost, turnover_saving, productivity_saving, net_benefit],
            connector=dict(line=dict(color=GRAY, width=0.5)),
            decreasing=dict(marker_color=CORAL),
            increasing=dict(marker_color=TEAL),
            totals=dict(marker_color=PURPLE),
            text=[
                f"-${total_pkg_cost:,.0f}",
                f"+${turnover_saving:,.0f}",
                f"+${productivity_saving:,.0f}",
                f"${net_benefit:,.0f}",
            ],
            textposition="outside",
            textfont=dict(size=10, family=_FONT),
        ))
        fig_roi.update_layout(
            **BASE_LAYOUT, margin=_M,
            yaxis=dict(title="AUD ($)", showgrid=True, gridcolor=_GRID),
            height=300, showlegend=False,
        )
        st.plotly_chart(fig_roi, use_container_width=True)

    # P3.2 — Real wage gap: historical trajectory + projected recovery with/without relief.
    # The relief_amount slider drives _relief_boost, so this chart reacts to the sidebar.
    st.markdown(
        '<p class="chart-title">Real Wage Gap — Historical Trend &amp; Projected Recovery With Relief</p>',
        unsafe_allow_html=True,
    )
    _gh_df   = df.dropna(subset=["real_wage_gap_yoy"])
    _gh_qs   = _gh_df["quarter_label"].tolist()
    _gh_vs   = _gh_df["real_wage_gap_yoy"].tolist()
    _base_gv = _gh_vs[-1]
    _proj_qs = ["2025Q3", "2025Q4", "2026Q1", "2026Q2"]
    # No-relief: gap improves slowly at the current rate (wage > CPI by ~1.2pp)
    _no_rel  = [round(_base_gv + 0.12 * (i + 1), 2) for i in range(4)]
    # With-relief: relief_weekly / avg_weekly boosts effective take-home above CPI each quarter
    _rel_boost_pp = (relief_amount / 52) / AVG_WEEKLY * 100
    _with_rel = [round(_base_gv + (0.12 + _rel_boost_pp / 4) * (i + 1), 2) for i in range(4)]

    fig_gap_rec = go.Figure()
    fig_gap_rec.add_trace(go.Scatter(
        x=_gh_qs, y=_gh_vs, name="Historical gap", mode="lines+markers",
        line=dict(color=GRAY, width=2),
        marker=dict(size=4, color=[CORAL if v < 0 else TEAL for v in _gh_vs]),
        hovertemplate="%{x}: %{y:+.2f}pp<extra></extra>",
    ))
    fig_gap_rec.add_trace(go.Scatter(
        x=[_gh_qs[-1]] + _proj_qs, y=[_base_gv] + _no_rel,
        name="No relief", mode="lines",
        line=dict(color=CORAL, width=2, dash="dot"),
        hovertemplate="%{x}: %{y:+.2f}pp<extra></extra>",
    ))
    fig_gap_rec.add_trace(go.Scatter(
        x=[_gh_qs[-1]] + _proj_qs, y=[_base_gv] + _with_rel,
        name="With relief", mode="lines",
        line=dict(color=TEAL, width=2.5),
        fill="tonexty", fillcolor="rgba(29,158,117,0.08)",
        hovertemplate="%{x}: %{y:+.2f}pp<extra></extra>",
    ))
    fig_gap_rec.add_hline(
        y=0, line_color=GRAY, line_width=0.8, line_dash="dot",
        annotation_text="Wages = CPI", annotation_position="top left",
        annotation_font=dict(size=9, family=_FONT),
    )
    fig_gap_rec.add_shape(
        type="line",
        x0=_gh_qs[-1], x1=_gh_qs[-1], y0=0, y1=1, xref="x", yref="paper",
        line=dict(color=PURPLE, width=1.2, dash="dash"),
    )
    fig_gap_rec.add_annotation(
        x=_gh_qs[-1], y=1, yref="paper", text="Now",
        showarrow=False, xanchor="left",
        font=dict(size=10, family=_FONT, color=PURPLE),
    )
    fig_gap_rec.update_layout(
        **BASE_LAYOUT, margin=_M,
        yaxis=dict(title="Real wage gap (pp)", showgrid=True, gridcolor=_GRID,
                   ticksuffix="pp", zeroline=False),
        legend=dict(orientation="h", yanchor="top", y=1.0, xanchor="left", x=0,
                    bgcolor="rgba(255,255,255,0.85)", font=dict(size=10, family=_FONT),
                    borderwidth=0),
        height=240, hovermode="x unified",
    )
    st.plotly_chart(fig_gap_rec, use_container_width=True, config={"displayModeBar": False})

    # State-level CPI pressure for the three relief categories (annual %, current period).
    # SA/TAS: high electricity. NT: high food & transport (remote). QLD: gov energy rebates.
    _STATE_CAT_CPI = {
        #         energy   food  transport
        "NSW": (  7.5,     3.9,  4.5),
        "VIC": (  8.8,     3.7,  4.0),
        "QLD": (  6.0,     4.1,  4.8),
        "WA":  (  9.2,     4.4,  5.1),
        "SA":  ( 12.5,     3.8,  4.2),
        "TAS": ( 10.8,     4.5,  5.5),
        "ACT": (  5.5,     3.5,  3.8),
        "NT":  (  7.8,     5.2,  6.0),
    }

    # National average shares (mean of state CPI rates → proportional allocation)
    _nat_e = sum(v[0] for v in _STATE_CAT_CPI.values()) / len(_STATE_CAT_CPI)
    _nat_f = sum(v[1] for v in _STATE_CAT_CPI.values()) / len(_STATE_CAT_CPI)
    _nat_t = sum(v[2] for v in _STATE_CAT_CPI.values()) / len(_STATE_CAT_CPI)
    _nat_tot = _nat_e + _nat_f + _nat_t
    nat_t_share = _nat_t / _nat_tot
    nat_f_share = _nat_f / _nat_tot
    nat_e_share = _nat_e / _nat_tot

    # Per-state amounts for each category
    def _state_rows(cat_idx):
        rows = []
        for state, cpis in _STATE_CAT_CPI.items():
            e, f, t = cpis
            tot   = e + f + t
            cpi   = cpis[cat_idx]
            share = cpi / tot
            rows.append({"state": state, "cpi": cpi, "share": share,
                         "amount": relief_amount * share})
        return sorted(rows, key=lambda r: r["amount"])   # ascending → highest at top in H bar

    def _render_breakdown(rows):
        df_bd   = pd.DataFrame(rows)
        amounts = df_bd["amount"].tolist()
        labels  = [f"  ${v:,.0f}  ({r:.0%})" for v, r in zip(df_bd["amount"], df_bd["share"])]
        fig = go.Figure(go.Bar(
            x=amounts, y=df_bd["state"], orientation="h",
            marker=dict(
                color=amounts,
                colorscale=[[0, TEAL], [0.5, "#F5C4B3"], [1, CORAL]],
                cmin=min(amounts), cmax=max(amounts), showscale=False,
            ),
            text=labels, textposition="outside",
            textfont=dict(size=10, family=_FONT, color="#2C2C2A"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Amount: $%{x:,.0f}/yr<br>"
                "CPI: %{customdata:.1f}%"
                "<extra></extra>"
            ),
            customdata=df_bd["cpi"].tolist(),
        ))
        fig.update_layout(
            **BASE_LAYOUT,
            height=220, margin=dict(t=4, b=4, l=8, r=100),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                       range=[0, max(amounts) * 1.45]),
            yaxis=dict(title=""),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<p class="chart-title">Suggested Relief Package Composition</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(kpi(
            "Transport Subsidy",
            f"${relief_amount * nat_t_share:,.0f} / yr",
            f"Avg {nat_t_share:.0%} of package · national",
        ), unsafe_allow_html=True)
        with st.expander("State breakdown"):
            _render_breakdown(_state_rows(2))

    with col2:
        st.markdown(kpi(
            "Grocery Allowance",
            f"${relief_amount * nat_f_share:,.0f} / yr",
            f"Avg {nat_f_share:.0%} of package · national",
        ), unsafe_allow_html=True)
        with st.expander("State breakdown"):
            _render_breakdown(_state_rows(1))

    with col3:
        st.markdown(kpi(
            "Energy Bill Offset",
            f"${relief_amount * nat_e_share:,.0f} / yr",
            f"Avg {nat_e_share:.0%} of package · national",
        ), unsafe_allow_html=True)
        with st.expander("State breakdown"):
            _render_breakdown(_state_rows(0))

# ── Footer ─────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="font-size:11px;color:#aaa8a2;text-align:center;font-family:\'Inter\',sans-serif">'
    "Sources: ABS Cat. 6401.0 (CPI) · 6345.0 (WPI) · 8501.0 (Retail Trade) · 5676.0 (Business Indicators) "
    "· AHRI · APA Financial Wellbeing Report 2024. Projections are modelled estimates."
    "</p>",
    unsafe_allow_html=True,
)
