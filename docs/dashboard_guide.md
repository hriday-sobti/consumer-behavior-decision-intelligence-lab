# Dashboard Implementation Guide

This guide describes how to interact with the **Streamlit Decision Intelligence Application** and configure the **Power BI Desktop Report**.

---

## 1. Streamlit Interactive Application

The Streamlit workbench provides a responsive, live decision-support interface connected directly to the processed analytical outputs.

### Launching the Application
From the repository root with the virtual environment activated:
```bash
streamlit run app/app.py
```

### Application Page Navigation:
1. **Overview**: Executive KPIs, spend trends, Lorenz concentration curve, and verified stand-out observations.
2. **Behavioral Segments**: Comparative distribution matrices across recency, frequency, spend, and catalog breadth, complete with strategic inquiry cards.
3. **Behavior Over Time**: Longitudinal state composition stacked area charts, month-over-month state transition probability matrices, and acquisition cohort retention heatmaps.
4. **Decision Signals**: Inventory of rule-based triggers by severity with complete customer-level evidence breakdowns.
5. **Customer Explorer**: Diagnostic lookup card for individual customer IDs detailing classification rationale, metric values, and active trigger limitations.
6. **Methodology & Controls**: Complete audit gate statuses, lineage diagrams, and documented data limitations.

---

## 2. Power BI Desktop Implementation

The repository provides a complete star-schema model, pre-calculated DAX measure definitions, and visual page specifications.

### Steps to Open and Refresh Power BI:
1. Launch **Power BI Desktop**.
2. Open or create a new `.pbix` report.
3. In Power BI, select **Get Data &rarr; Folder** or **Text/CSV**, pointing to:
   ```
   dashboard/powerbi/data_exports/
   ```
4. Load the following verified CSV exports:
   - `customer_summary.csv`
   - `segment_summary.csv`
   - `monthly_summary.csv`
   - `state_transitions.csv`
   - `decision_signals.csv`
   - `data_controls.csv`
   - `cohort_summary.csv`
   - `country_summary.csv`
   - `product_summary.csv`
5. Apply the official theme file from:
   ```
   dashboard/powerbi/theme/cbdil_theme.json
   ```
   *(View tab &rarr; Themes dropdown &rarr; Browse for themes)*
6. Copy the standardized DAX measures from:
   ```
   dashboard/powerbi/dax/measures.dax
   ```
7. Lay out visuals following the page blueprints in:
   ```
   dashboard/powerbi/page_specs/page_layout_specs.md
   ```
