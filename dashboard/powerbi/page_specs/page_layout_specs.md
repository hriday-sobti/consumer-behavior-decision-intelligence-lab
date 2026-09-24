# Power BI Visual & Page Layout Specifications

This guide provides exact visual component specifications for reproducing the 7-page analytical workbook in Power BI Desktop.

---

## Page 1: Customer Overview
- **Header KPI Cards (Top Bar)**:
  1. `[Total Customers]`
  2. `[Active Customers]` (with subtitle: `% of Total`)
  3. `[Total Value]` (Formatted as Currency `£#,##0`)
  4. `[Total Orders]`
  5. `[Average Order Value]` (Formatted as Currency `£#,##0.00`)
- **Visual 1 (Main Left, Line & Clustered Column Chart)**:
  - X-Axis: `monthly_summary[year_month]`
  - Column Values: `monthly_summary[total_value]` (Dark Blue `#1F4E78`)
  - Line Values: `monthly_summary[total_orders]` (Amber `#D97706`)
  - Title: *"Monthly spend and order volume trend"*
- **Visual 2 (Main Right, Clustered Bar Chart)**:
  - Y-Axis: `segment_summary[segment_name]`
  - X-Axis: `segment_summary[total_value]`
  - Data Label: `segment_summary[value_share]`
  - Title: *"Value contribution by behavioral segment"*
- **Visual 3 (Bottom Left, Line Chart - Empirical Lorenz Curve)**:
  - X-Axis: `Cumulative Customer %`
  - Y-Axis: `Cumulative Spend %`
  - Title: *"Customer value concentration (Lorenz curve)"*
- **Visual 4 (Bottom Right, Stacked Bar Chart)**:
  - X-Axis: `customer_summary[behavioral_state]`
  - Y-Axis: `Count of Customers`
  - Title: *"Current customer lifecycle state distribution"*
- **Text Box ("What stands out")**:
  - Concise bullet points reflecting verified findings (53.8% value in top 5%, 261 softening accounts, 31.5% single-order buyers).

---

## Page 2: Behavioral Segments
- **Slicers (Top Left)**: `segment_summary[segment_name]`
- **Visual 1 (Top Grid, Matrix Table)**:
  - Rows: `segment_name`
  - Columns: `Customer Count`, `Customer Share`, `Total Spend`, `Spend Share`, `Median Recency`, `Median Orders`, `AOV`
- **Visual 2 (Bottom Left, Scatter Plot)**:
  - X-Axis: `customer_summary[recency_days]`
  - Y-Axis: `customer_summary[total_value]` (Logarithmic scale enabled)
  - Legend: `customer_summary[segment_name]`
  - Title: *"Recency vs spend distribution by segment"*
- **Visual 3 (Bottom Right, Box / Distribution Plot)**:
  - Category: `customer_summary[segment_name]`
  - Metric: `customer_summary[product_count]`
  - Title: *"Catalog SKU breadth variation across segments"*

---

## Page 3: Segment Deep Dive
- **Selected Segment Card**: Dynamic card displaying selected segment title and business description.
- **Visual 1 (Left, Clustered Column Chart)**:
  - Recent vs Prior 90-Day spend comparison: `[Recent Value]` vs `[Prior Value]`.
- **Visual 2 (Right, Monthly Trend Line)**:
  - Active customer count and spend for selected segment across calendar months.
- **Narrative Section ("Questions worth investigating")**:
  - Displays `possible_business_question` mapped dynamically from `segment_profile`.

---

## Page 4: Behavior Over Time
- **Visual 1 (Top, 100% Stacked Area Chart)**:
  - X-Axis: `monthly_summary[year_month]`
  - Values: `Engaged`, `Emerging`, `Reactivated`, `Softening`, `Dormant` customer counts.
  - Title: *"Monthly customer lifecycle state composition"*
- **Visual 2 (Bottom, Matrix Heatmap - Transition Matrix)**:
  - Rows: `state_transitions[previous_state]`
  - Columns: `state_transitions[current_state]`
  - Values: `AVERAGE(state_transitions[customer_share])` (Formatted as Percentage, conditional background blue data bar).
  - Title: *"Month-over-month state transition probability matrix"*

---

## Page 5: Decision Signals
- **Summary Cards**:
  - Signal counts by severity: `High Severity`, `Medium Severity`, `Low Severity`.
- **Visual 1 (Left, Horizontal Bar Chart)**:
  - Y-Axis: `decision_signals[signal_name]`
  - X-Axis: `Count of Triggered Accounts`
  - Legend: `decision_signals[signal_strength]`
- **Visual 2 (Main Table, Customer Drill-Down Table)**:
  - Columns: `customer_id`, `signal_name`, `signal_strength`, `segment`, `behavioral_state`, `evidence_metric_1`, `evidence_metric_2`, `explanation`, `signal_limitation`.
  - Filter: Searchable by `customer_id` and dropdown filter by `signal_name`.

---

## Page 6: Customer Explorer
- **Slicer**: Single-select dropdown for `customer_summary[customer_id]`.
- **Diagnostic Cards**:
  - Customer ID, Primary Country, Segment Name, Current State, Lifetime Spend, Lifetime Orders, Recency (Days), Spend Momentum.
- **Transaction History Sub-Table**:
  - Linked order history and invoice dates for the selected customer.
- **Callout Box**:
  - "Why this customer is classified this way" displaying deterministic metric reasons.

---

## Page 7: Data & Controls
- **Audit Cards**:
  - Source Period: *2009-12-01 to 2011-12-09*
  - Total Raw Records: *1,067,371*
  - Cleaned Records: *1,033,034*
  - Valid Purchases: *779,423*
  - Eligible Accounts: *4,023*
  - Ineligible Accounts: *1,855*
- **Audit Control Table**:
  - Rows from `data_controls.csv` displaying `control_id`, `control_name`, `affected_pct`, `severity`, `status`, `impact`, `recommended_resolution`.
  - Conditional formatting on `status`: Green for PASS, Amber for WARNING, Red for FAIL.
