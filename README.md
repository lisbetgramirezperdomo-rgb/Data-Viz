# Cost of Living Crisis — Australia
### DVN Assignment 3 · UTS · Streamlit Dashboard

A data narrative exploring how the cost-of-living crisis is affecting Australian workers,
built as a pitch to corporate HR leadership to justify a cost-of-living relief package.

---

## Run locally

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

> **Note:** The plain `streamlit` command may not work if the Scripts directory is not in PATH.  
> Place `combined_data-2024.csv` in the same folder as `app.py` before running.

For Streamlit Cloud: push to GitHub and connect the repo at share.streamlit.io.

---

## Narrative Arc

The dashboard tells a single story across three tabs, each building on the last:

| Tab | Story beat | Narrative role |
|---|---|---|
| 1 · The Gap | Entry | What is happening — wages vs CPI, 2021–2025 |
| 2 · Human Cost | Middle | So what — business and workforce impact |
| 3 · What If? | Exit | What next — model the relief package ROI |

---

## Advanced Features

*Assignment requirement: implement at least 3 of the 5 listed advanced features.*

| # | Feature | Implementation |
|---|---|---|
| 1 | **Context-Aware Filtering** | The **States / Territories** multiselect and **Salary Band** slider in the sidebar simultaneously update: the Financial Stress KPI count, all state-level bar charts, the animated workforce map, and a dynamic narrative callout block in Tab 2 that rewrites its insight sentence to reflect the selected cohort. The **Essential categories only** toggle in Tab 1 filters the animated CPI chart and updates the scrollytelling callout text. |
| 2 | **What-If Parameterization** | The **Annual relief per employee** slider ($0–$3,000) and **Employees covered** input drive: the ROI waterfall chart, the projected purchasing power trajectory, the wage gap recovery projection (Tab 3 — slider connected to gap chart), and all four KPI cards in real time. Changing the slider updates every downstream calculation simultaneously. |
| 3 | **Narrative Scrollytelling** | Each tab opens with a headline that frames the narrative ("Your employees are earning more — and affording less"). Contextual callout blocks between sections guide the reader: Tab 1 explains how to read the animated chart; Tab 2 provides a data-driven insight sentence that changes with filter selections. The animated bar chart is itself a scroll-through-time experience, tracing the crisis quarter by quarter from 2021 to 2025. |
| 4 | **Visual Tooltips / Rich Hover** | The animated workforce map uses a fully custom `hovertemplate` that surfaces six data fields per employee dot (base wage, nominal wage, real wage, CPI YoY, wage YoY, PP index). The hero KPI card in Tab 1 is paired with a **sparkline** showing the full wage-gap trajectory with an interactive hover. All line charts use `hovermode="x unified"` for cross-trace comparison on hover. |

---

## Data Dictionary

### `combined_data-2024.csv` — Main quarterly time series
*Source: ABS. Transformed and joined from multiple ABS releases.*

| Field | Type | Description | Source |
|---|---|---|---|
| `quarter` | string | Quarter label e.g. `2024Q1` | Derived |
| `quarter_label` | string | Human-readable quarter label (same as `quarter`) | Derived |
| `quarter_end` | date | Last calendar day of the quarter | Derived |
| `year` | int | Calendar year | Derived |
| `quarter_num` | int | Quarter number 1–4 | Derived |
| `cpi_index` | float | All-groups CPI index value | ABS Cat. 6401.0 |
| `wage_index` | float | Wage Price Index — total hourly rates of pay | ABS Cat. 6345.0 |
| `cpi_qoq_pct` | float | CPI % change quarter-on-quarter | Derived |
| `cpi_yoy_pct` | float | CPI % change year-on-year | ABS / Derived |
| `wage_qoq_pct` | float | Wage index % change QoQ | Derived |
| `wage_yoy_pct` | float | Wage index % change YoY | ABS / Derived |
| `real_wage_gap_yoy` | float | `wage_yoy_pct − cpi_yoy_pct` in percentage points | Derived |
| `wage_to_cpi_ratio` | float | `wage_index / cpi_index` | Derived |
| `purchasing_power_index` | float | Real purchasing power relative to 2021Q1 = 100 | Derived |
| `retail_turnover_quarterly` | float | Retail turnover, quarterly total (A$M) | ABS Cat. 8501.0 |
| `retail_turnover_monthly_avg` | float | Average monthly retail turnover (A$M) | Derived |
| `months_in_quarter` | int | Always 3 | Derived |
| `retail_qoq_pct` | float | Retail turnover % change QoQ | Derived |
| `retail_yoy_pct` | float | Retail turnover % change YoY | Derived |

### Supplementary datasets (embedded in `app.py`)

#### `load_cpi_categories()` — CPI by expenditure category
*Source: ABS Cat. 6401.0 Table 3, modelled from published category-level trajectories.*

| Field | Type | Description |
|---|---|---|
| `quarter` | string | Quarter label (2021Q1 – 2025Q2, 18 quarters) |
| `category` | string | ABS expenditure group name (10 categories) |
| `cpi_change` | float | Cumulative % change from 2021Q1 baseline |
| `discretionary` | bool | `True` = discretionary spending; `False` = essential |

**Categories:** Housing · Electricity & gas · Food & non-alcoholic beverages · Insurance & financial services · Health · Transport · Alcohol & tobacco · Education · Recreation & culture · Clothing & footwear

#### `load_state_data()` — State-level retail and earnings
*Source: ABS Cat. 8501.0 Table 5 (retail) + ABS Cat. 6302.0 (earnings).*

| Field | Type | Description |
|---|---|---|
| `state` | string | State/territory abbreviation (NSW VIC QLD WA SA TAS ACT NT) |
| `retail_change_pct` | float | Nominal retail turnover % change, 2024 |
| `real_change_pct` | float | Real (inflation-adjusted) retail % change, 2024 |
| `avg_weekly_earnings` | int | Average weekly earnings (A$), 2024 |

#### `load_business_indicators()` — Business cost and surplus index
*Source: ABS Cat. 5676.0, December 2024. Index base = 2024Q1 = 100.*

| Field | Type | Description |
|---|---|---|
| `quarter` | string | Quarter label (2024Q1 – 2025Q2) |
| `input_costs` | float | Input cost index |
| `gross_surplus` | float | Gross operating surplus index |
| `wages_bill` | float | Total wages bill index |

#### `load_employee_map_data()` — Synthetic workforce (82 employees × 18 quarters)
*Synthetic data generated with `numpy.random.seed(42)` to simulate a realistic workforce distribution. State proportions match ABS labour force shares. Individual wages drawn from normal distributions calibrated to ABS average weekly earnings by state.*

| Field | Type | Description |
|---|---|---|
| `employee_id` | string | Unique ID e.g. `EMP-001` |
| `state` | string | State/territory |
| `lat` / `lon` | float | Jittered coordinates within state bounds (for map display) |
| `quarter` | string | Quarter label |
| `base_weekly_wage` | int | Employee's 2021Q1 base weekly wage (A$) |
| `weekly_wage` | int | Nominal weekly wage in this quarter (base × WPI ratio × modifier) |
| `real_weekly_wage` | int | Real weekly wage adjusted for CPI (nominal / CPI ratio) |
| `purchasing_power_index` | float | Individual PP index relative to 2021Q1 = 100 |
| `cpi_yoy_pct` | float | National CPI YoY % for this quarter |
| `wage_yoy_pct` | float | National wage YoY % for this quarter |
| `real_wage_gap_pp` | float | `wage_yoy_pct − cpi_yoy_pct` for this quarter |

### Embedded scalar constants (in `app.py`)

| Constant | Value | Basis |
|---|---|---|
| `PRODUCTIVITY_LOSS` | $3,400 / yr | APA Financial Wellbeing Report 2024 |
| `TURNOVER_COST` | $55,000 (midpoint) | AHRI — $40K–$80K replacement cost range |
| `STRESSED_PCT` | 33% | APA 2024 baseline financial stress rate |
| `AVG_WEEKLY` | $1,750 | ABS average weekly earnings, 2024 |

---

## Code annotations

Key non-obvious implementation decisions are annotated inline in `app.py`:

- **`load_main()` patch block** — 2024 YoY values overwritten post-merge because the CSV contains raw index values; YoY rates come from the separate ABS release and are injected here to avoid two-file joins at runtime.
- **`load_employee_map_data()` PP formula** — `pp_index = (wage_idx_t / base_wage_idx) / (cpi_idx_t / base_cpi_idx) × modifier × 100`. The individual modifier (0.88–1.12) simulates wage dispersion within a state; without it all employees in a state would have identical trajectories.
- **`load_cpi_categories()` sort order** — Category order is fixed by the final quarter's values before the animation starts. Without this, bars jump position between frames because Plotly re-sorts each frame independently.
- **`wage_cum_by_q` shapes loop** — Plotly animated frames don't inherit the parent layout's shapes; each frame needs its own wage-line shape injected via `frame.layout`.
- **Sparkline (P2.3)** — Rendered as a separate `go.Figure` inside `col_h` directly after the HTML KPI card. Plotly doesn't support embedding charts inside HTML strings.
- **P3.2 wage gap recovery** — `_rel_boost_pp = (relief_amount / 52) / AVG_WEEKLY × 100` converts annual relief to a weekly purchasing-power boost expressed in percentage points, then compounds quarterly.

---

## Credits

| Role | Detail |
|---|---|
| **Author** |Maria Rodriguez Alliende, Geraldine Ramírez, Xiaofei Jia, Akhil Chauhuab, Mukesh Murugesan, The Vinh Bui, Turki Al Hajri|
| **Course** | DVN — Data Visualisation · UTS Master of Data Science and Innovation |
| **Dashboard framework** | [Streamlit](https://streamlit.io) |
| **Charting library** | [Plotly](https://plotly.com/python/) |
| **Map tiles** | Carto Positron via Mapbox (Plotly scatter_mapbox) |
| **Typeface** | Inter — Google Fonts |

### ABS Data Sources

| Dataset | ABS Catalogue | URL |
|---|---|---|
| Consumer Price Index | 6401.0 | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia |
| Wage Price Index | 6345.0 | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia |
| Retail Trade | 8501.0 | https://www.abs.gov.au/statistics/industry/retail-and-wholesale-trade/retail-trade-australia |
| Average Weekly Earnings | 6302.0 | https://www.abs.gov.au/statistics/labour/earnings-and-working-conditions/average-weekly-earnings-australia |
| Business Indicators | 5676.0 | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia |

### Other references

- APA Financial Wellbeing Report 2024 — productivity loss per financially stressed employee ($3,400/yr)
- AHRI (Australian HR Institute) — employee replacement cost range ($40K–$80K)
- ABS Labour Force (6202.0) — state employment proportions used to size the synthetic workforce
