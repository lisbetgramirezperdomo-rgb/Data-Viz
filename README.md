# Cost of Living Crisis — Australia
### DVN Assignment 3 · Streamlit Dashboard

A data narrative exploring how the cost of living crisis is affecting Australian workers,
built as a pitch to corporate HR leadership for a cost-of-living relief package.

---

## Deployment

```bash
pip install -r requirements.txt

# Place CSV files in same folder as app.py
# - combined_data-2024.csv
# - recent_data_for_AT3-2024.csv

streamlit run app.py
```

For Streamlit Cloud: push to GitHub, connect repo at share.streamlit.io.
Update the file paths in `load_main()` to match your repo structure (e.g. `data/combined_data-2024.csv`).

---

## Narrative Arc

**The Sparkline** — showing the gap between what workers have and what they could have.

| Dashboard | Story point | Narrative role |
|---|---|---|
| 1 · The Gap | Entry | What is happening — wages vs CPI |
| 2 · Human Cost | Middle | So what — business and worker impact |
| 3 · What If? | Exit | What next — model the relief package ROI |

---

## Advanced Features (Assignment requirement: 3 of 5)

| # | Feature | Implementation |
|---|---|---|
| 1 | **Context-aware filtering** | State multiselect in sidebar filters the choropleth map, bar chart, and narrative callout text dynamically. Category toggle filters the CPI chart and updates the insight text. |
| 2 | **What-if parameterization** | Relief amount slider ($0–$3,000) and employee count input update the ROI waterfall chart, purchasing power projection, and all metric cards in real time. |
| 3 | **Narrative scrollytelling** | Three-page structure (sidebar radio) guides the user through a structured narrative arc. Each page has dynamic callout text that changes based on filters and parameters. |

---

## Data Dictionary

### combined_data-2024.csv / recent_data_for_AT3-2024.csv
*Source: ABS. Transformed and joined from multiple ABS releases.*

| Field | Type | Description | Source |
|---|---|---|---|
| `quarter` | string | Quarter label (e.g. 2024Q1) | Derived |
| `cpi_index` | float | All groups CPI index value | ABS Cat. 6401.0 |
| `quarter_end` | date | Last day of the quarter | Derived |
| `wage_index` | float | Wage Price Index (total hourly rates) | ABS Cat. 6345.0 |
| `retail_turnover_quarterly` | float | Retail turnover, quarterly total ($M) | ABS Cat. 8501.0 |
| `retail_turnover_monthly_avg` | float | Average monthly retail turnover ($M) | Derived |
| `months_in_quarter` | int | Always 3 | Derived |
| `year` | int | Calendar year | Derived |
| `quarter_num` | int | Quarter number (1–4) | Derived |
| `quarter_label` | string | Human-readable quarter label | Derived |
| `cpi_qoq_pct` | float | CPI % change quarter-on-quarter | Derived |
| `cpi_yoy_pct` | float | CPI % change year-on-year | Derived |
| `wage_qoq_pct` | float | Wage index % change QoQ | Derived |
| `wage_yoy_pct` | float | Wage index % change YoY | Derived |
| `retail_qoq_pct` | float | Retail turnover % change QoQ | Derived |
| `retail_yoy_pct` | float | Retail turnover % change YoY | Derived |
| `real_wage_gap_yoy` | float | Wage YoY minus CPI YoY (percentage points) | Derived |
| `wage_to_cpi_ratio` | float | Wage index / CPI index | Derived |
| `purchasing_power_index` | float | Purchasing power relative to 2024Q1 (base=100) | Derived |

### Supplementary datasets (embedded in app.py)

**CPI by category** — ABS Cat. 6401.0 Table 3, December 2024.
Annual % change by expenditure group. Used in Dashboard 1 bar chart.

**State retail & earnings** — ABS Cat. 8501.0 Table 5 + ABS Cat. 6302.0.
Nominal and real retail change by state/territory. Average weekly earnings by state.
Used in Dashboard 2 choropleth and bar chart.

**Business indicators** — ABS Cat. 5676.0, December 2024.
Input costs, wages bill, and gross operating surplus index (base = 2024Q1 = 100).
Used in Dashboard 2 line chart.

---

## Credits

| Role | Contribution |
|---|---|
| Data sourcing & cleaning | ABS public releases (links below) |
| Dashboard development | Streamlit + Plotly |
| Narrative design | Sparkline arc — gap between current and possible |

**ABS Data Links**
- CPI: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia
- WPI: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia
- Retail Trade: https://www.abs.gov.au/statistics/industry/retail-and-wholesale-trade/retail-trade-australia
- Business Indicators: https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia
