# Consumer Behavior Decision Intelligence Lab (CBDIL)

## Deliverables

* **Interactive Streamlit Decision Workbench**: Launch locally via `streamlit run app/app.py`
* **Detailed Project Report**: [Customer Behavior Decision Intelligence Report (PDF)](docs/customer_behavior_decision_intelligence_report.pdf)
* **Project Repository**: [https://github.com/hriday-sobti/consumer-behavior-decision-intelligence-lab](https://github.com/hriday-sobti/consumer-behavior-decision-intelligence-lab)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.0+-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Ready-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](dashboard/powerbi/)
[![Tests](https://img.shields.io/badge/Tests-229_Passing-2EA44F?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Reconciliation](https://img.shields.io/badge/Reconciliation-Multi--Engine_Validated-1F4E78?style=for-the-badge)](src/validation/reconciliation.py)
[![Author](https://img.shields.io/badge/Author-Hriday_Singh_Sobti-0F172A?style=for-the-badge&logo=github&logoColor=white)](https://github.com/hriday-sobti)

---
## Overview

The Consumer Behavior Decision Intelligence Lab (CBDIL) converts raw transactional sales records into an auditable customer behavioral modeling and commercial decision-support system. Built around longitudinal purchase ledgers from a UK-based merchant, the system addresses a fundamental limitation of traditional transaction reporting: raw invoice rows record discrete sales events, but fail to provide visibility into customer-level concentration, order cadence decay, catalog drift, or actionable decision triggers.

Rather than compressing customer behavior into a single score, the system models accounts across five measurable dimensions:
1. **Value**: Cumulative gross revenue, Average Order Value (AOV), and median basket spend.
2. **Activity**: Recency intervals (elapsed days since last purchase), transaction counts, and active months.
3. **Breadth**: Unique catalog SKUs purchased and average items per order.
4. **Stability**: Interpurchase gap variation and order interval predictability ($\sigma_{\text{gap}} / \mu_{\text{gap}}$).
5. **Momentum**: Recent 90-day vs prior 90-day trajectory across spend, frequency, and SKU breadth.

---

## Analytical Problem

In commercial wholesale and retail operations, gross sales totals frequently conceal underlying account volatility:
* **The Concentration Dilemma**: A small fraction of wholesale commercial buyers generates the majority of revenue, but their order patterns are naturally lumpy, making standard monthly averages misleading.
* **The Static RFM Flaw**: Classical recency, frequency, and monetary scores measure lifetime totals but cannot detect whether an account is actively accelerating or in acute contraction relative to its own baseline.
* **The Churn Blind Spot**: When a major client reduces order volume by 50%, traditional transaction dashboards fail to trigger an alert until the account has already lapsed into complete dormancy.
* **The Need for Decision Intelligence**: Operational teams require deterministic, rule-based behavioral signals tied directly to testable commercial playbooks with holdout control group designs.

---

## What the Project Does

The system moves through an auditable analytical chain:
1. **Data Ingestion & Integrity**: Ingests 1,067,371 raw records from the official UCI Online Retail II repository without modifying source bytes, applying exact composite-key deduplication (removing 34,337 duplicate lines).
2. **Event Classification**: Enforces a 4-tier precedence rule (`CANCELLATION` > `REVERSAL_OR_RETURN` > `VALID_PURCHASE` > `INVALID_OR_UNUSABLE`), cleanly isolating 779,423 valid purchases while preserving 19,494 cancellations to compute customer return rates.
3. **Relational Dimensional Modeling**: Implements a star-schema architecture in PostgreSQL (`staging`, `analytics`, `reporting` schemas) with surrogate keys, separating line-item transactions (779k rows) from order headers (36,969 orders) and customer entities (5,878 accounts).
4. **Behavioral Feature Engineering**: Calculates 32 behavioral features per customer relative to a fixed reference date (`2011-12-10 00:00:00`), isolating single-order and new accounts (31.5% of population) via an explicit eligibility gate (`insufficient_history = TRUE`).
5. **Silhouette-Optimized Clustering**: Evaluates K-Means across $K \in \{3, 4, 5, 6\}$, selecting $K=3$ deterministically based on peak silhouette score (0.2749) and minimum cluster share constraints ($\ge 5\%$).
6. **Dynamic Lifecycle Snapshots**: Vectorizes 98,557 monthly customer snapshots across 25 calendar months, tracking month-over-month transitions across 5 lifecycle states (`REACTIVATED` > `EMERGING` > `DORMANT` > `SOFTENING` > `ENGAGED`).
7. **Decision Signal Engine**: Evaluates 6 deterministic behavioral signals across all accounts, mapping identified cohorts to structured decision playbooks with 20% holdout control testing designs.

---

## Cross-Engine Reconciliation (PostgreSQL & DuckDB)

To verify analytical integrity and eliminate grain mismatch, CBDIL implements multi-engine cross-validation comparing PostgreSQL relational queries directly against DuckDB vector queries across raw Parquet and CSV artifacts (`src/validation/reconciliation.py`):

| Analytical Metric Dimension | PostgreSQL (Engine) | DuckDB (Parquet Artifacts) | Variance | Audit Status |
| :--- | :--- | :--- | :--- | :--- |
| **Cleaned Transactions (Staging)** | 1,033,034 | 1,033,034 | 0.0 | **MATCH** |
| **Staging Gross Line Value** | £18,854,981.85 | £18,854,981.85 | 0.0 | **MATCH** |
| **Valid Purchase Lines** | 779,423 | 779,423 | 0.0 | **MATCH** |
| **Total Invoices (Order Grain)** | 36,969 | 36,969 | 0.0 | **MATCH** |
| **Gross Valid Purchase Spend** | £17,374,252.42 | £17,374,252.42 | 0.0 | **MATCH** |
| **Total Identified Customers** | 5,878 | 5,878 | 0.0 | **MATCH** |
| **Customer Feature Spend Total** | £17,374,252.42 | £17,374,252.42 | 0.0 | **MATCH** |
| **Eligible Clustered Accounts** | 4,023 | 4,023 | 0.0 | **MATCH** |
| **Segmented Spend Contribution** | £16,549,691.51 | £16,549,691.51 | 0.0 | **MATCH** |

---
## New Contributions and Improvements

| Analytical Dimension | Standard Baseline Approach | CBDIL Systematic Contribution |
| :--- | :--- | :--- |
| **Event Classification** | Cancellations deleted or mixed into sales | Enforces 4-tier precedence; captures return rates without deflating historical order frequency. |
| **Behavioral Modeling** | Single composite RFM score | Constructs a 5-dimensional behavioral vector: Value, Activity, Breadth, Stability, Momentum. |
| **Eligibility Governance** | Single-order accounts deleted arbitrarily | Isolates single-order accounts (31.5%) via metadata flags; retains them in reporting totals while protecting clustering models. |
| **Model Selection** | Subjective cluster count selection | Automated rule: smallest $K$ with silhouette $\ge 90\%$ of peak and all cluster shares $\ge 5\%$. |
| **Lifecycle Analysis** | Static lifetime snapshot | 98,557 monthly customer snapshots tracking month-over-month state transitions. |
| **Decision Support** | Raw descriptive dashboards | Evaluates 6 rule-based decision signals linked to holdout testing playbooks with guardrail KPIs. |
| **Quality Audit** | Ad-hoc or missing validation | Embedded audit layer evaluating 6 data-quality controls directly in the database. |

---

## Key Findings

1. **Extreme Value Concentration (Pareto Distribution)**:
   * The top **1%** of accounts generate **26.4%** of gross purchasing value.
   * The top **5%** generate **53.8%** of gross purchasing value.
   * The top **20%** drive **83.1%** of gross purchasing value (£13.75M of £16.55M eligible spend).
   * *Business Takeaway*: Revenue stability is governed by wholesale repeat buyers, confirming the need for key-account capacity protection.

2. **High-Value Deceleration Risk (`HIGH_VALUE_SOFTENING`)**:
   * **261 accounts** in the top spend quintile (spend $\ge$ £2,910) show a $\ge 25\%$ drop in recent 90-day spend relative to baseline.
   * These accounts represent over **£2.56 million** in historical revenue exposure, warranting proactive commercial check-ins.

3. **Prevalence of One-Time Purchasers**:
   * **31.5%** of all customer accounts (1,855 out of 5,878) place exactly one order during their entire history and never return. Repeat customer rate is **68.5%**.

4. **Behavioral Segment Structure ($K=3$)**:
   * **High-Value Stable** (1,164 accounts | 28.9% share | 75.0% spend): Median spend £4,967; median 13 orders; median recency 23 days; median 173 unique SKUs.
   * **Emerging Engagement** (1,084 accounts | 27.0% share | 12.6% spend): Median spend £1,260; median 4 orders; median recency 29 days; median +100% momentum.
   * **Low-Activity / Long-Recency** (1,775 accounts | 44.1% share | 12.4% spend): Median spend £816; median 3 orders; median recency 266 days.

---

## Dashboards

### 1. Streamlit Decision Intelligence Workbench (`app/app.py`)
Provides an interactive multi-view decision interface connected directly to cached analytical exports:
* **Page 1: Executive Overview**: Top KPIs, monthly spend/order trends, empirical Lorenz concentration curve, and verified operational findings.
* **Page 2: Behavioral Segments**: Comparative metrics matrix, log-spend vs recency scatter plot, SKU breadth boxplots, and strategic inquiry cards.
* **Page 3: Segment Deep Dive**: Recent vs prior 90-day spend comparison, active monthly trends, and segment-specific decision questions.
* **Page 4: Behavior Over Time**: Monthly stacked state area charts, interactive state migration heatmap, and cohort retention grid.
* **Page 5: Decision Signals**: Inventory of rule-based triggers by severity with complete customer-level evidence breakdowns.
* **Page 6: Customer Explorer**: Individual account diagnostic card detailing historical spend, order cadence, spend momentum, classification rationale, and active trigger limitations.

### 2. Power BI Reporting Suite (`dashboard/powerbi/`)
* **Semantic Star Model**: Relational model connecting `dim_customer`, `dim_product`, `dim_date`, `dim_country`, and fact tables.
* **DAX Measure Catalog**: 16 formatted measures (`dax/measures.dax`) utilizing safe division and filter context modification.
* **Visual Blueprints**: 7 detailed page layout specifications (`page_specs/page_layout_specs.md`).

---

## Data Quality & Controls

The data governance layer evaluates 6 continuous controls (`reporting.data_control_summary`):
* **`CTRL-01` (Unattributed Guest Transactions)**: Flags 243,007 rows (22.77%) lacking customer IDs. Status: **WARNING**. Preserved in staging for gross accounting while isolated from account-level clustering.
* **`CTRL-02` (Corrupted Negative Unit Prices)**: Identifies 5 bad debt adjustment lines (-£53k). Status: **PASS**. Filtered via Class 4 precedence.
* **`CTRL-03` (Transaction Deduplication)**: Detects 34,337 duplicate lines (3.22%). Status: **PASS**. Deduplicated via composite key hash.
* **`CTRL-04` (Longitudinal Eligibility Filter)**: Flags 1,855 accounts (31.56%) with $< 2$ orders or $< 90$d tenure. Status: **PASS**. Preserved in summary totals while excluded from K-Means.
* **`CTRL-05` (Elevated Reversal Distortion)**: Tracks 335 accounts (5.7%) with return spend exceeding 10%. Status: **WARNING**. Attached as limitation metadata to decision signal records.
* **`CTRL-06` (Segment Share Viability)**: Confirms no selected cluster contains $< 5\%$ of eligible accounts. Status: **PASS** (smallest cluster represents 26.95%).

---

## Reproducibility & Commands

### Prerequisites
* Python 3.10+ (tested on Python 3.14.6 x64)
* Git

### Step-by-Step Execution
```bash
# 1. Clone repository & create virtual environment
git clone https://github.com/hriday-sobti/consumer-behavior-decision-intelligence-lab.git
cd consumer_behavior_decision_intelligence_lab
python -m venv .venv

# 2. Activate virtual environment (Windows)
.venv\Scripts\activate
# (Linux/macOS)
# source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -e .

# 4. Acquire raw dataset
python scripts/acquire_data.py

# 5. Run end-to-end analytical pipeline
python scripts/run_pipeline.py

# 6. Run automated test suite (229 tests)
pytest -q

# 7. Launch Streamlit Decision Workbench
streamlit run app/app.py
```

---

## Limitations

1. **Merchant Domain Scope**: The dataset represents a commercial UK-based giftware distributor; reorder intervals and basket sizes cannot be generalized to consumer banking, FMCG, or SaaS subscriptions.
2. **Wholesale Purchase Lumpiness**: Inactivity intervals of 60–90 days frequently reflect standard distributor restocking cycles rather than account cancellation.
3. **Observational Bounds**: Marketing interventions are unobserved in the source data; decision signals define hypotheses for testing rather than guaranteed causal uplifts.
4. **Guest Checkout Dilution**: 22.8% of raw transaction records lack customer identifiers, meaning walk-in revenue cannot be tracked longitudinally at the account grain.
