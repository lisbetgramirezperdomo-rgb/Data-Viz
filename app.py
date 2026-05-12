import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cost of Living — Australia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# DESIGN SYSTEM (kept lightweight, same as yours but cleaner)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp { background-color: #F5F4F0; }

.block-container { padding-top: 1rem; }

.kpi {
    background: white;
    border-radius: 12px;
    padding: 14px 16px;
    border: 1px solid #E6E2DA;
}

.kpi h3 { margin: 0; font-size: 12px; color: #5A574F; }
.kpi h1 { margin: 4px 0 0 0; font-size: 28px; }

.small { color:#5A574F; font-size:13px; }

hr { border: none; border-top: 1px solid #E6E2DA; }

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER (VERY IMPORTANT FOR PITCH)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:22px;background:#111110;color:white;border-radius:12px;margin-bottom:15px'>
<h1 style='margin:0;font-size:34px'>Australia’s Cost of Living Crisis</h1>
<p style='margin-top:8px;color:#CFCAC2;font-size:16px'>
From inflation to wages: what changed, who is affected, and what employers can do.
</p>
<p style='margin-top:6px;color:#9ED8C0;font-size:14px'>
Designed for HR & policy decision-makers
</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA (KEEP YOUR EXISTING LOAD FUNCTIONS HERE)
# ─────────────────────────────────────────────────────────────
# 👉 ASSUMPTION: your original load_* functions remain unchanged
# df, df_cpi_cat, df_states, df_biz, df_emp, etc.

# (KEEP YOUR DATA LOADING CODE EXACTLY AS IS)
# ----------------------------------------------------------------

# ─────────────────────────────────────────────────────────────
# SIDEBAR (SIMPLIFIED FOR PITCH)
# ─────────────────────────────────────────────────────────────
st.sidebar.markdown("## Filters")

selected_states = st.sidebar.multiselect(
    "States",
    df_states["state"].tolist(),
    default=df_states["state"].tolist()
)

show_essential_only = st.sidebar.toggle("Essential CPI only", False)

relief_amount = st.sidebar.slider("Relief per employee ($)", 0, 3000, 1500, 100)
num_employees = st.sidebar.number_input("Employees", 10, 100000, 500, 50)

# ─────────────────────────────────────────────────────────────
# FILTERS (same logic, cleaner)
# ─────────────────────────────────────────────────────────────
df_sf = df_states[df_states["state"].isin(selected_states)]

# ─────────────────────────────────────────────────────────────
# TABS (MARTINI GLASS STRUCTURE)
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "1️⃣ The Crisis",
    "2️⃣ Why It Matters",
    "3️⃣ The Business Case"
])

# ═════════════════════════════════════════════════════════════
# TAB 1 — THE CRISIS
# ═════════════════════════════════════════════════════════════
with tab1:

    latest_gap = df["real_wage_gap_yoy"].iloc[-1]

    st.markdown(f"""
    ### Workers are earning more — but affording less.

    <div class='small'>
    Inflation has outpaced wage growth across most of 2021–2024, creating a persistent gap in purchasing power.
    </div>
    """, unsafe_allow_html=True)

    # KPIs simplified
    col1, col2, col3 = st.columns(3)

    col1.metric("Real Wage Gap", f"{latest_gap:.2f} pp")
    col2.metric("Peak Inflation Pressure", "7.8%")
    col3.metric("Purchasing Power Index", f"{df['purchasing_power_index'].iloc[-1]:.1f}")

    st.markdown("---")

    # MAIN CHART (CLEANER + SHOCK VISUAL)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["quarter_label"],
        y=df["cpi_yoy_pct"],
        name="Inflation",
        line=dict(color="#C0390A", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=df["quarter_label"],
        y=df["wage_yoy_pct"],
        name="Wage Growth",
        line=dict(color="#0A8A55", width=3)
    ))

    # Crisis highlight
    fig.add_vrect(
        x0="2022Q1", x1="2023Q4",
        fillcolor="rgba(192,57,10,0.08)",
        layer="below",
        line_width=0
    )

    fig.update_layout(height=350, margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.info("Inflation exceeded wage growth for most of 2022–2023, creating sustained real income pressure.")

# ═════════════════════════════════════════════════════════════
# TAB 2 — WHY IT MATTERS
# ═════════════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    ### This is no longer just a household problem — it is a business problem.

    Financial stress translates directly into productivity loss and workforce instability.
    """)

    col1, col2, col3 = st.columns(3)

    col1.metric("1 in 3 Workers", "Financial Stress")
    col2.metric("Productivity Loss", "$3,400 / worker")
    col3.metric("Turnover Cost", "$40K–$80K")

    st.markdown("---")

    fig2 = px.bar(
        df_sf,
        x="real_change_pct",
        y="state",
        orientation="h",
        color="real_change_pct",
        color_continuous_scale=["#C0390A","#F5E6A0","#0A8A55"]
    )

    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

    st.info("Several Australian states show negative real spending growth after inflation adjustment.")

    # MAP moved to expander (IMPORTANT FOR CLEAN DEMO)
    with st.expander("Explore workforce distribution map"):
        st.map(df_emp[["lat","lon"]])

# ═════════════════════════════════════════════════════════════
# TAB 3 — BUSINESS CASE
# ═════════════════════════════════════════════════════════════
with tab3:

    total_cost = relief_amount * num_employees
    benefit = num_employees * 3400 * 0.33
    roi = benefit / total_cost if total_cost > 0 else 0

    st.markdown("""
    ### What if employers acted?

    Targeted cost-of-living relief can reduce turnover and improve productivity.
    """)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Cost", f"${total_cost:,.0f}")
    col2.metric("Estimated Benefit", f"${benefit:,.0f}")
    col3.metric("ROI", f"{roi:.2f}x")

    st.markdown("---")

    fig3 = go.Figure(go.Waterfall(
        x=["Cost","Productivity Gain","Turnover Savings","Net Impact"],
        y=[-total_cost, benefit*0.6, benefit*0.4, benefit-total_cost],
        increasing=dict(marker_color="#0A8A55"),
        decreasing=dict(marker_color="#C0390A"),
        totals=dict(marker_color="#4A43A0")
    ))

    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

    if roi > 1:
        st.success("This intervention generates positive ROI for employers.")
    else:
        st.warning("Adjust parameters to reach breakeven.")

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-size:12px;color:#5A574F;text-align:center'>
ABS 2024–2025 | CPI, Retail Trade, Business Indicators | Scenario modelling included
</div>
""", unsafe_allow_html=True)
