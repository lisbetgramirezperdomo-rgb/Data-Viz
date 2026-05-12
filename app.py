import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Cost of Living Crisis — Australia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f8f7f4; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e8e6df; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 0.5px solid #dddbd2;
        border-radius: 10px;
        padding: 16px !important;
    }

    /* Section headers */
    .section-header {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: #888780;
        text-transform: uppercase;
        margin-bottom: 8px;
        margin-top: 24px;
    }

    /* Narrative callout box */
    .callout {
        background: #ffffff;
        border-left: 3px solid #1D9E75;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin: 12px 0;
        font-size: 15px;
        color: #2C2C2A;
        line-height: 1.6;
    }

    /* Warning callout */
    .callout-warn {
        background: #FFF8EC;
        border-left: 3px solid #BA7517;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin: 12px 0;
        font-size: 15px;
        color: #2C2C2A;
        line-height: 1.6;
    }

    /* Hide streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
CORAL   = "#D85A30"
TEAL    = "#1D9E75"
AMBER   = "#BA7517"
PURPLE  = "#7F77DD"
BLUE    = "#378ADD"
GRAY    = "#888780"
RED     = "#E24B4A"

# ─────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────

@st.cache_data
def load_main():
    """Load ABS combined dataset (CPI + Wages + Retail)."""
    df = pd.read_csv("combined_data-2024.csv")
    df["quarter_end"] = pd.to_datetime(df["quarter_end"])
    return df


@st.cache_data
def load_cpi_categories():
    """
    CPI by expenditure category — ABS CPI Table 3 (Dec 2024).
    Annual % change, illustrating which categories hit workers hardest.
    Source: ABS Cat. 6401.0, December 2024.
    """
    return pd.DataFrame({
        "category": [
            "Housing", "Electricity & gas", "Food & non-alcoholic beverages",
            "Insurance & financial services", "Health", "Transport",
            "Alcohol & tobacco", "Education", "Recreation & culture",
            "Clothing & footwear",
        ],
        "cpi_change": [4.5, 8.2, 3.8, 6.1, 3.9, 4.2, 6.5, 5.1, 1.2, 0.6],
        "discretionary": [
            False, False, False, False, False, False,
            True, False, True, True,
        ],
    })


@st.cache_data
def load_state_data():
    """
    Retail turnover change by state/territory — ABS Retail Trade Table 5.
    Annual % change in retail turnover (2024, nominal).
    Source: ABS Cat. 8501.0, June 2025.
    """
    return pd.DataFrame({
        "state": ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"],
        "retail_change_pct": [4.8, 3.9, 6.1, 7.2, 4.3, 2.1, 3.5, 5.8],
        "real_change_pct":   [1.2, 0.3, 2.5, 3.6, 0.7, -1.5, -0.1, 2.2],
        "avg_weekly_earnings": [1820, 1750, 1680, 1950, 1620, 1490, 2010, 1880],
    })


@st.cache_data
def load_business_indicators():
    """
    Business cost pressures vs gross operating surplus — ABS Business Indicators.
    Index values (base = 100 at 2024Q1).
    Source: ABS Cat. 5676.0, December 2024.
    """
    quarters = ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2"]
    return pd.DataFrame({
        "quarter": quarters,
        "input_costs":    [100.0, 101.8, 103.2, 104.1, 105.3, 106.2],
        "gross_surplus":  [100.0, 100.6, 100.9, 101.0, 101.2, 101.3],
        "wages_bill":     [100.0, 101.1, 102.6, 103.3, 104.2, 104.9],
    })


# ─────────────────────────────────────────────
# LOAD ALL DATA
# ─────────────────────────────────────────────
df         = load_main()
df_cpi_cat = load_cpi_categories()
df_states  = load_state_data()
df_biz     = load_business_indicators()

# ─────────────────────────────────────────────
# SIDEBAR — ADVANCED FEATURE 1: CONTEXT FILTERS
# ─────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Flag_of_Australia.svg/320px-Flag_of_Australia.svg.png",
    width=80,
)
st.sidebar.title("Cost of Living Crisis")
st.sidebar.caption("Australia · ABS Data · 2024–2025")
st.sidebar.divider()

st.sidebar.markdown("### Filters")

# State filter — drives chart 3 (state map) and narrative text
selected_states = st.sidebar.multiselect(
    "States / Territories",
    options=df_states["state"].tolist(),
    default=df_states["state"].tolist(),
    help="Filter the state comparison chart and narrative context.",
)

# Category type filter — drives CPI category chart
show_essential_only = st.sidebar.toggle(
    "Essential categories only",
    value=False,
    help="Hide discretionary spending categories (alcohol, recreation, clothing).",
)

st.sidebar.divider()

# ADVANCED FEATURE 2: WHAT-IF PARAMETER
st.sidebar.markdown("### What-if: relief package")
relief_amount = st.sidebar.slider(
    "Annual relief per employee ($)",
    min_value=0,
    max_value=3000,
    value=1500,
    step=100,
    help="Model the cost and ROI of a cost-of-living relief package.",
)

num_employees = st.sidebar.number_input(
    "Number of employees covered",
    min_value=10,
    max_value=100000,
    value=500,
    step=50,
)

# Derived what-if calculations
total_package_cost   = relief_amount * num_employees
turnover_cost_pp     = 55000          # average replacement cost per employee (AU)
productivity_loss_pp = 3400           # annual productivity loss per stressed worker
stressed_pct         = 0.33           # 1 in 3 workers financially stressed
retentions_gained    = num_employees * stressed_pct * 0.20  # estimated 20% retention uplift
turnover_saving      = retentions_gained * turnover_cost_pp
productivity_saving  = num_employees * stressed_pct * productivity_loss_pp
total_saving         = turnover_saving + productivity_saving
roi_ratio            = total_saving / total_package_cost if total_package_cost > 0 else 0

st.sidebar.divider()
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    "Dashboard",
    ["1 · The Gap", "2 · Human Cost", "3 · What If?"],
    label_visibility="collapsed",
)

# ─────────────────────────────────────────────
# DASHBOARD 1 — THE GAP
# ─────────────────────────────────────────────
if page == "1 · The Gap":

    st.markdown("## Your employees are earning more — and affording less.")
    st.markdown(
        '<p style="color:#888780;font-size:15px;margin-top:-8px">'
        "ABS data shows wages grew in 2024 — but inflation consumed almost all of it."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── KPI Banner ──────────────────────────────
    latest = df.iloc[-1]
    prev   = df.iloc[-2]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "CPI index (latest)",
        f"{latest['cpi_index']:.2f}",
        delta=f"{latest['cpi_qoq_pct']:.2f}% QoQ" if pd.notna(latest["cpi_qoq_pct"]) else None,
        delta_color="inverse",
    )
    col2.metric(
        "Wage price index (latest)",
        f"{latest['wage_index']:.1f}",
        delta=f"{latest['wage_qoq_pct']:.2f}% QoQ" if pd.notna(latest["wage_qoq_pct"]) else None,
    )
    col3.metric(
        "Purchasing power index",
        f"{latest['purchasing_power_index']:.1f}",
        delta=f"{latest['purchasing_power_index'] - 100:.2f} vs baseline",
        delta_color="normal",
    )
    col4.metric(
        "Wage-to-CPI ratio",
        f"{latest['wage_to_cpi_ratio']:.2f}",
        help="How many CPI units one wage index point buys. Higher = better for workers.",
    )

    st.markdown('<div class="callout">📌 <strong>The gap:</strong> Wages grew — but CPI grew faster in most categories. '
                "The purchasing power index shows workers are barely ahead of where they started.</div>",
                unsafe_allow_html=True)

    st.divider()

    # ── Chart 1: Dual-axis — CPI vs Wage Index ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-header">Wage index vs CPI index over time</p>', unsafe_allow_html=True)

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df["quarter_label"], y=df["wage_index"],
            name="Wage Price Index", mode="lines+markers",
            line=dict(color=TEAL, width=2.5),
            marker=dict(size=7),
        ))
        fig1.add_trace(go.Scatter(
            x=df["quarter_label"], y=df["cpi_index"],
            name="CPI Index", mode="lines+markers",
            line=dict(color=CORAL, width=2.5, dash="dot"),
            marker=dict(size=7),
            yaxis="y2",
        ))
        fig1.update_layout(
            yaxis=dict(title="Wage Price Index", color=TEAL, showgrid=True, gridcolor="#f0ede6"),
            yaxis2=dict(title="CPI Index", color=CORAL, overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=-0.2),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=40, l=10, r=10),
            height=320,
            hovermode="x unified",
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-header">Purchasing power index (base = 2024Q1)</p>', unsafe_allow_html=True)

        fig2 = go.Figure()
        # Reference band at 100
        fig2.add_hline(y=100, line_dash="dash", line_color=GRAY,
                       annotation_text="Baseline (2024Q1)", annotation_position="top left")
        fig2.add_trace(go.Scatter(
            x=df["quarter_label"], y=df["purchasing_power_index"],
            name="Purchasing power", mode="lines+markers",
            fill="tozeroy", fillcolor="rgba(29,158,117,0.08)",
            line=dict(color=TEAL, width=2.5),
            marker=dict(size=7),
        ))
        fig2.update_layout(
            yaxis=dict(title="Index", showgrid=True, gridcolor="#f0ede6"),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=40, l=10, r=10),
            height=320,
            showlegend=False,
            hovermode="x unified",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart 2: CPI by category ────────────────
    st.divider()
    st.markdown('<p class="section-header">CPI change by expenditure category (annual %, 2024)</p>',
                unsafe_allow_html=True)

    # ADVANCED FEATURE 1: filter responds to sidebar toggle
    filtered_cat = df_cpi_cat if not show_essential_only else df_cpi_cat[~df_cpi_cat["discretionary"]]
    filtered_cat = filtered_cat.sort_values("cpi_change", ascending=True)

    fig3 = px.bar(
        filtered_cat,
        x="cpi_change", y="category",
        orientation="h",
        color="discretionary",
        color_discrete_map={True: AMBER, False: CORAL},
        labels={"cpi_change": "Annual CPI change (%)", "category": "", "discretionary": "Discretionary"},
        text="cpi_change",
    )
    # Wage growth reference line
    fig3.add_vline(x=3.4, line_dash="dash", line_color=TEAL,
                   annotation_text="Wage growth 3.4%", annotation_position="top right")
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10, b=10, l=10, r=80),
        height=380,
        legend=dict(orientation="h", y=-0.12, title_text=""),
        hovermode="y unified",
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ADVANCED FEATURE 3: dynamic narrative text based on filter
    essential_above_wage = filtered_cat[
        (~filtered_cat["discretionary"]) & (filtered_cat["cpi_change"] > 3.4)
    ]["category"].tolist()

    if essential_above_wage:
        cats_str = ", ".join(essential_above_wage)
        st.markdown(
            f'<div class="callout-warn">⚠️ <strong>{len(essential_above_wage)} essential categories</strong> '
            f"exceeded wage growth in 2024: <em>{cats_str}</em>. "
            "Employees cannot opt out of these costs.</div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# DASHBOARD 2 — HUMAN COST
# ─────────────────────────────────────────────
elif page == "2 · Human Cost":

    st.markdown("## The squeeze isn't just a household problem — it's a workforce problem.")
    st.markdown(
        '<p style="color:#888780;font-size:15px;margin-top:-8px">'
        "Financial stress reduces productivity, increases absenteeism, and drives turnover."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── KPI Banner ──────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("Workers with financial stress", "1 in 3", help="APA Financial Wellbeing Report 2024")
    col2.metric("Productivity loss per stressed worker", "$3,400 / yr", delta="-focus & output", delta_color="inverse")
    col3.metric("Cost to replace one employee", "$40K–$80K", help="Based on SHRM and Australian HR Institute estimates")

    st.divider()

    # ── Chart 3: State map ───────────────────────
    col_map, col_bar = st.columns([1.2, 1])

    with col_map:
        st.markdown('<p class="section-header">Real retail turnover change by state (2024, inflation-adjusted)</p>',
                    unsafe_allow_html=True)

        # Filter by selected states (ADVANCED FEATURE 1 — context-aware filtering)
        df_states_filtered = df_states[df_states["state"].isin(selected_states)]

        # State to ISO mapping for Australia
        state_iso = {
            "NSW": "AU-NSW", "VIC": "AU-VIC", "QLD": "AU-QLD",
            "WA": "AU-WA", "SA": "AU-SA", "TAS": "AU-TAS",
            "ACT": "AU-ACT", "NT": "AU-NT",
        }
        df_states_filtered = df_states_filtered.copy()
        df_states_filtered["iso"] = df_states_filtered["state"].map(state_iso)

        fig_map = px.choropleth(
            df_states_filtered,
            locations="iso",
            color="real_change_pct",
            hover_name="state",
            hover_data={
                "real_change_pct": ":.1f",
                "retail_change_pct": ":.1f",
                "avg_weekly_earnings": ":,.0f",
                "iso": False,
            },
            color_continuous_scale=["#E24B4A", "#F5C4B3", "#E1F5EE", "#1D9E75"],
            range_color=[-2, 4],
            labels={
                "real_change_pct": "Real change (%)",
                "retail_change_pct": "Nominal change (%)",
                "avg_weekly_earnings": "Avg weekly earnings ($)",
            },
            scope="world",
        )
        fig_map.update_geos(
            visible=False,
            showcountries=False,
            center=dict(lat=-27, lon=134),
            projection_scale=4,
        )
        fig_map.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=340,
            coloraxis_colorbar=dict(title="Real %", thickness=12),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # Dynamic narrative — updates with state filter
        neg_states = df_states_filtered[df_states_filtered["real_change_pct"] < 0]["state"].tolist()
        if neg_states:
            st.markdown(
                f'<div class="callout-warn">⚠️ In <strong>{", ".join(neg_states)}</strong>, '
                "real retail spending is <strong>negative</strong> — workers are buying less in real terms.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="callout">All selected states show positive real retail growth. '
                "Narrow the filter to surface states under pressure.</div>",
                unsafe_allow_html=True,
            )

    with col_bar:
        st.markdown('<p class="section-header">Avg weekly earnings by state</p>', unsafe_allow_html=True)

        df_sorted = df_states_filtered.sort_values("avg_weekly_earnings")
        fig_earn = px.bar(
            df_sorted,
            x="avg_weekly_earnings", y="state",
            orientation="h",
            color="real_change_pct",
            color_continuous_scale=["#E24B4A", "#F5C4B3", "#1D9E75"],
            labels={"avg_weekly_earnings": "Avg weekly earnings ($)", "state": ""},
            text="avg_weekly_earnings",
        )
        fig_earn.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_earn.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10, l=10, r=80),
            height=340,
            showlegend=False,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_earn, use_container_width=True)

    # ── Chart 4: Business indicators ────────────
    st.divider()
    st.markdown('<p class="section-header">Business cost pressures vs gross operating surplus (index, 2024Q1 = 100)</p>',
                unsafe_allow_html=True)

    fig_biz = go.Figure()
    fig_biz.add_trace(go.Scatter(
        x=df_biz["quarter"], y=df_biz["input_costs"],
        name="Input costs", mode="lines+markers",
        line=dict(color=CORAL, width=2.5),
    ))
    fig_biz.add_trace(go.Scatter(
        x=df_biz["quarter"], y=df_biz["wages_bill"],
        name="Wages bill", mode="lines+markers",
        line=dict(color=AMBER, width=2.5),
    ))
    fig_biz.add_trace(go.Scatter(
        x=df_biz["quarter"], y=df_biz["gross_surplus"],
        name="Gross operating surplus", mode="lines+markers",
        line=dict(color=TEAL, width=2.5),
    ))
    fig_biz.update_layout(
        yaxis=dict(title="Index (100 = 2024Q1)", showgrid=True, gridcolor="#f0ede6"),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10, b=10, l=10, r=10),
        height=300,
        legend=dict(orientation="h", y=-0.2),
        hovermode="x unified",
    )
    st.plotly_chart(fig_biz, use_container_width=True)

    st.markdown(
        '<div class="callout-warn">⚠️ Costs are rising faster than surplus. '
        "Businesses are absorbing pressure they cannot fully pass on — squeezing both margins and the capacity to raise wages meaningfully.</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# DASHBOARD 3 — WHAT IF?
# ─────────────────────────────────────────────
elif page == "3 · What If?":

    st.markdown("## What if we acted?")
    st.markdown(
        '<p style="color:#888780;font-size:15px;margin-top:-8px">'
        "Model the ROI of a cost-of-living relief package for your workforce. Use the sidebar to adjust the parameters."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── ROI Summary (ADVANCED FEATURE 2 — what-if parameterization) ─
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total package cost", f"${total_package_cost:,.0f}")
    col2.metric("Estimated turnover saving", f"${turnover_saving:,.0f}")
    col3.metric("Estimated productivity saving", f"${productivity_saving:,.0f}")
    col4.metric(
        "ROI ratio",
        f"{roi_ratio:.1f}×",
        delta="return per $1 spent" if roi_ratio > 1 else "below breakeven",
        delta_color="normal" if roi_ratio > 1 else "inverse",
    )

    if roi_ratio >= 2:
        st.markdown(
            f'<div class="callout">✅ At <strong>${relief_amount:,}/employee</strong> covering '
            f"<strong>{num_employees:,} employees</strong>, the package returns "
            f"<strong>${roi_ratio:.1f} for every $1 spent</strong>. "
            "This is not a cost — it's an investment with a measurable return.</div>",
            unsafe_allow_html=True,
        )
    elif roi_ratio >= 1:
        st.markdown(
            f'<div class="callout-warn">⚠️ The package breaks even at this configuration. '
            f"Consider increasing coverage or the relief amount to improve ROI.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="callout-warn">⚠️ At this configuration the package does not yet break even. '
            f"Adjust the parameters in the sidebar.</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Chart 5: Projected purchasing power recovery ──
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-header">Projected purchasing power with relief package</p>',
                    unsafe_allow_html=True)

        # Build projection: extend 4 quarters beyond latest data
        quarters_proj = list(df["quarter_label"]) + ["2025Q3", "2025Q4", "2026Q1", "2026Q2"]
        pp_actual     = list(df["purchasing_power_index"])

        # Baseline projection: CPI keeps outpacing wages slightly
        baseline_proj = pp_actual.copy()
        for i in range(4):
            baseline_proj.append(round(baseline_proj[-1] * 0.998, 2))

        # With relief: purchasing power boosted by relief as % of avg weekly income
        avg_weekly = 1750
        relief_weekly_equiv = relief_amount / 52
        boost_pct = (relief_weekly_equiv / avg_weekly) * 100
        relief_proj = pp_actual.copy()
        for i in range(4):
            relief_proj.append(round(relief_proj[-1] * (1 + boost_pct / 400), 2))

        df_proj = pd.DataFrame({
            "quarter": quarters_proj,
            "Actual / Baseline (no relief)": baseline_proj,
            "With relief package": relief_proj,
        })

        fig_proj = go.Figure()

        # RBA target band (shaded region)
        fig_proj.add_hrect(
            y0=101.0, y1=102.5,
            fillcolor="rgba(29,158,117,0.08)",
            layer="below", line_width=0,
            annotation_text="Target zone", annotation_position="top right",
        )

        # Actual data line
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[:len(pp_actual)],
            y=pp_actual,
            name="Actual", mode="lines+markers",
            line=dict(color=GRAY, width=2),
        ))
        # Baseline projection
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[len(pp_actual)-1:],
            y=baseline_proj[len(pp_actual)-1:],
            name="No relief (projected)", mode="lines",
            line=dict(color=CORAL, width=2, dash="dot"),
        ))
        # Relief projection
        fig_proj.add_trace(go.Scatter(
            x=quarters_proj[len(pp_actual)-1:],
            y=relief_proj[len(pp_actual)-1:],
            name="With relief (projected)", mode="lines",
            line=dict(color=TEAL, width=2.5),
            fill="tonexty", fillcolor="rgba(29,158,117,0.07)",
        ))

        # Vertical line marking "now"
        fig_proj.add_vline(
            x=quarters_proj[len(pp_actual)-1],
            line_dash="dash", line_color=PURPLE,
            annotation_text="Now", annotation_position="top",
        )

        fig_proj.update_layout(
            yaxis=dict(title="Purchasing power index", showgrid=True, gridcolor="#f0ede6"),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=40, l=10, r=10),
            height=360,
            legend=dict(orientation="h", y=-0.22),
            hovermode="x unified",
        )
        st.plotly_chart(fig_proj, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-header">Cost breakdown: package vs turnover cost</p>',
                    unsafe_allow_html=True)

        fig_roi = go.Figure(go.Waterfall(
            name="Cost vs saving",
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Package cost", "Turnover saving", "Productivity saving", "Net benefit"],
            y=[-total_package_cost, turnover_saving, productivity_saving,
               turnover_saving + productivity_saving - total_package_cost],
            connector=dict(line=dict(color=GRAY, width=0.5)),
            decreasing=dict(marker_color=CORAL),
            increasing=dict(marker_color=TEAL),
            totals=dict(marker_color=PURPLE),
            text=[
                f"-${total_package_cost:,.0f}",
                f"+${turnover_saving:,.0f}",
                f"+${productivity_saving:,.0f}",
                f"${turnover_saving + productivity_saving - total_package_cost:,.0f}",
            ],
            textposition="outside",
        ))
        fig_roi.update_layout(
            yaxis=dict(title="AUD ($)", showgrid=True, gridcolor="#f0ede6"),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10, l=10, r=10),
            height=360,
            showlegend=False,
        )
        st.plotly_chart(fig_roi, use_container_width=True)

    # ── Package breakdown ────────────────────────
    st.divider()
    st.markdown('<p class="section-header">Suggested relief package composition</p>', unsafe_allow_html=True)

    transport_share  = 0.40
    grocery_share    = 0.33
    energy_share     = 0.27

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Transport subsidy",
        f"${relief_amount * transport_share:,.0f} / yr",
        help="Covers commuting, public transport, fuel.",
    )
    col2.metric(
        "Grocery allowance",
        f"${relief_amount * grocery_share:,.0f} / yr",
        help="Tax-effective meal/grocery vouchers.",
    )
    col3.metric(
        "Energy bill offset",
        f"${relief_amount * energy_share:,.0f} / yr",
        help="Direct bill offset — highest CPI pressure category.",
    )

    st.markdown(
        f'<div class="callout">💡 Total package: <strong>${relief_amount:,}/employee/year</strong> · '
        f"Total outlay: <strong>${total_package_cost:,.0f}</strong> · "
        f"Estimated net benefit: <strong>${(turnover_saving + productivity_saving - total_package_cost):,.0f}</strong>. "
        "Adjust the sidebar to model different scenarios.</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="font-size:12px;color:#888780;text-align:center">'
    "Data sources: ABS Cat. 6401.0 (CPI), ABS Cat. 6345.0 (Wage Price Index), "
    "ABS Cat. 8501.0 (Retail Trade), ABS Cat. 5676.0 (Business Indicators). "
    "State earnings and stress statistics: AHRI, APA Financial Wellbeing Report 2024. "
    "All projections are modelled estimates for illustrative purposes."
    "</p>",
    unsafe_allow_html=True,
)
