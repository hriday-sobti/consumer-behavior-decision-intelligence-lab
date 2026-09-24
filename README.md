# Consumer Behavior Decision Intelligence Lab (CBDIL)

An end-to-end customer analytics, behavioral segmentation, and decision-support system built around transactional purchasing behavior.

---

## 1. Overview & Analytical Objective

The Consumer Behavior Decision Intelligence Lab (CBDIL) answers a practical progression of commercial inquiries:
1. What does the customer base look like across structural spend and order dimensions?
2. How active and concentrated is purchasing value across accounts?
3. Which behavioral customer groups are genuinely distinct across value, cadence, breadth, stability, and momentum?
4. How do accounts migrate between behavioral lifecycle states month-over-month?
5. Where do acute signals of deceleration or expansion emerge, and what testable actions should commercial teams evaluate?

Rather than compressing customer behavior into a single score, the system represents customer behavior across five measurable dimensions:
1. **Value**: Cumulative revenue, Average Order Value (AOV), median order spend.
2. **Activity**: Recency intervals (elapsed days since last purchase), transaction counts, active months.
3. **Breadth**: Unique catalog SKUs purchased, average items per basket.
4. **Stability**: Interpurchase gap variation and order interval predictability.
5. **Momentum**: Recent 90-day vs prior 90-day trajectory across spend, frequency, and SKU breadth.

---

## 2. Dataset & Provenance

The system is built on the official **UCI Online Retail II** longitudinal transaction dataset covering two continuous years of transaction activity (December 1, 2009 to December 9, 2011).

- **Official Citation DOI**: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D)
- **Raw Records**: 1,067,371 rows across two sheets (`Year 2009-2010` and `Year 2010-2011`).
- **Cleaned Valid Purchases**: 779,423 line items representing 36,969 validated orders across 5,878 distinct customer accounts.
- **Provenance Rules**: Raw files in `data/raw/` are strictly read-only and immutable. All transformations are applied downstream.

---

## 3. Analytical Pipeline Architecture

The end-to-end pipeline enforces strict separation across analytical layers:

```
RAW WORKBOOK (data/raw/)
  ↓
PROFILING & EVENT PRECEDENCE CLASSIFICATION (Class 1-4)
  ↓
DEDUPLICATION & STAGING (PostgreSQL: staging.raw_retail_transactions)
  ↓
STAR SCHEMA MODEL (analytics.dim_* & analytics.fact_*)
  ↓
5-DIMENSIONAL FEATURE ENGINEERING (analytics.customer_behavior_features)
  ↓
K-MEANS BEHAVIORAL SEGMENTATION (analytics.customer_segment)
  ↓
LONGITUDINAL MONTHLY SNAPSHOTS (analytics.customer_monthly_snapshot)
  ↓
LIFECYCLE STATE MACHINE & TRANSITIONS (analytics.state_transition_matrix)
  ↓
DETERMINISTIC DECISION SIGNALS (analytics.customer_decision_signal)
  ↓
REPORTING EXPORTS & AUDIT CONTROLS (reporting.summary views & CSVs)
  ↓
INTERACTIVE WORKBENCHES (Streamlit Application & Power BI Semantic Model)
```

---

## 4. Key Analytical Discoveries

All findings originate strictly from verified pipeline outputs:

1. **Severe Revenue Concentration (Pareto Distribution)**:
   - The top **1%** of eligible accounts generate **26.4%** of total spend.
   - The top **5%** generate **53.8%** of total spend.
   - The top **20%** generate **83.1%** of total spend.
   - The business exhibits wholesale B2B dynamics requiring dedicated key-account protections.

2. **High-Value Account Deceleration (`HIGH_VALUE_SOFTENING`)**:
   - **261 accounts** in the top spend quintile (spend $\ge$ £2,910) show a $\ge 25\%$ contraction in recent 90-day spend.
   - These accounts represent over **£1.2 million** in historical revenue exposure.

3. **Single-Order Buyer Prevalence**:
   - **31.5%** of all identified customer accounts (1,855 customers) placed exactly one order and never returned over 24 months.
   - Repeat customer rate is **68.5%** (4,023 multi-order accounts).

4. **Behavioral Segment Structure ($K=3$)**:
   - **High-Value Stable** (28.9% of accounts, 75.0% of total spend): Median spend £4,967, median 13 orders, median recency 23 days.
   - **Emerging Engagement** (26.9% of accounts, 12.6% of spend): Median spend £1,260, median 4 orders, median recency 29 days.
   - **Low-Activity / Long-Recency** (44.1% of accounts, 12.4% of spend): Median spend £816, median 3 orders, median recency 266 days.

---

## 5. Quickstart & Reproduction Commands

### Prerequisites
- Python 3.12+ (tested on Python 3.14.6 x64 Windows)
- Git

### 1. Clone & Set Up Environment
```bash
git clone <repo-url>
cd consumer_behavior_decision_intelligence_lab

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# (or Windows Command Prompt)
.venv\Scripts\activate.bat
# (or Linux / macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Acquire Raw Data
```bash
python scripts/acquire_data.py
```

### 3. Run Complete End-to-End Analytical Pipeline
```bash
python scripts/run_pipeline.py
```
*(Executes profiling, event classification, deduplication, feature engineering, clustering, monthly snapshots, state transitions, decision signals, database loads, reporting exports, and validation checks).*

### 4. Run Automated Test Suite
```bash
pytest -v
```

### 5. Launch Interactive Streamlit Workbench
```bash
streamlit run app/app.py
```

---

## 6. Project Directory Layout

```
consumer_behavior_decision_intelligence_lab/
├── README.md                           # System overview, findings, reproduction instructions
├── LICENSE                             # MIT Open Source License
├── pyproject.toml                      # Build specifications & pytest configurations
├── requirements.txt                    # Locked core dependencies
├── .env.example                        # Database and environment template
│
├── data/
│   ├── raw/                            # Immutable raw workbook & provenance metadata
│   ├── interim/                        # Cleaned parquet staging caches
│   └── processed/                      # Analytical parquet tables
│
├── sql/                                # Production PostgreSQL DDL and audit queries
│   ├── 00_database_setup.sql           # Schema isolation (staging, analytics, reporting)
│   ├── 01_staging_tables.sql           # Raw staging loads with event classes
│   ├── 02_dimension_tables.sql         # Customer, Product, Date, Country dimensions
│   ├── 03_fact_tables.sql              # Fact Order & Fact Transaction
│   ├── 04_customer_features.sql        # 5-dimensional customer behavioral table
│   ├── 05_rfm.sql                      # Supporting RFM quintile model
│   ├── 06_behavioral_segments.sql      # Segment profiles & customer assignments
│   ├── 07_monthly_snapshots.sql        # Longitudinal monthly customer snapshots
│   ├── 08_state_transitions.sql        # Transition matrix & individual history
│   ├── 09_opportunity_flags.sql        # Decision signals & strategy catalog
│   ├── 10_reporting_views.sql          # Executive summary reporting tables
│   └── 11_validation_queries.sql       # Automated integrity & constraint checks
│
├── src/                                # Reusable modular engineering core
│   ├── config.py                       # Analytical thresholds & time windows
│   ├── logging_config.py               # Structured logging setup
│   ├── ingestion/                      # Data loaders and PostgreSQL engine
│   ├── cleaning/                       # Precedence classification & deduplication
│   ├── validation/                     # Data profiling and quality checks
│   ├── features/                       # 5-dimensional features & RFM logic
│   ├── segmentation/                   # K-Means clustering & silhouette selection
│   ├── lifecycle/                      # Vectorized snapshots & lifecycle states
│   ├── decisions/                      # Decision signals & deterministic insights
│   └── reporting/                      # Standardized reporting exports & figures
│
├── scripts/                            # Pipeline execution entry points
│   ├── acquire_data.py                 # Direct archive download
│   ├── profile_data.py                 # Data profiling runner
│   ├── clean_data.py                   # Event classification & cleaning
│   ├── build_features.py               # Customer features & RFM
│   ├── run_segmentation.py             # Behavioral clustering
│   ├── build_snapshots.py              # Snapshots & state transitions
│   ├── build_decision_signals.py       # Decision signals engine
│   ├── export_reporting_data.py        # CSV exports & insights
│   ├── load_database.py                # PostgreSQL bulk loader
│   ├── validate_all.py                 # Full database & constraint audit
│   └── run_pipeline.py                 # Single-command end-to-end master runner
│
├── app/                                # Streamlit decision intelligence app
│   └── app.py                          # 6-view interactive decision workbench
│
├── notebooks/                          # Initial EDA & hypothesis verification
│   └── 01_initial_exploration.ipynb    # Visual checks across 5 dimensions
│
├── dashboard/powerbi/                  # Power BI reporting layer
│   ├── data_exports/                   # Verified CSV reporting datasets
│   ├── dax/measures.dax                # Pre-built DAX measure definitions
│   ├── theme/cbdil_theme.json          # Muted executive color theme
│   ├── model/                          # Star schema relationship specs
│   └── page_specs/                     # 7-page visual layout blueprints
│
├── tests/                              # Comprehensive test suite (16 tests)
│   ├── test_ingestion.py               # Provenance & raw validation
│   ├── test_cleaning.py                # Precedence rules & deduplication
│   ├── test_features.py                # Reference date & eligibility
│   ├── test_rfm.py                     # Quintile score bounds
│   ├── test_segments.py                # Seed stability & clustering
│   ├── test_states.py                  # Lifecycle state precedence
│   ├── test_decisions.py               # Signal triggers & severity
│   ├── test_database.py                # PostgreSQL integrity queries
│   └── test_pipeline.py                # Export verification
│
├── docs/                               # Complete analytical documentation
│   ├── data_source.md                  # Provenance, citations, and DOI
│   ├── data_dictionary.md              # Table grains, definitions, and types
│   ├── methodology.md                  # Feature formulas, windows, and rules
│   ├── data_quality.md                 # Profiling anomalies & audit controls
│   ├── architecture.md                 # System components & data flow
│   ├── research_log.md                 # Technical decisions & engine constraints
│   ├── insight_log.md                  # 6-part decision register
│   ├── decision_framework.md           # Decision strategy testing designs
│   ├── dashboard_guide.md              # Streamlit & Power BI guides
│   ├── stakeholder_questions.md        # Business question mapping
│   ├── data_lineage.md                 # Metric transformations matrix
│   └── limitations.md                  # Domain & observational bounds
│
└── outputs/
    ├── figures/                        # Interactive Plotly HTML visuals
    ├── tables/                         # Profiles, insights, and transition matrices
    ├── exports/                        # Standardized reporting CSVs
    └── reports/                        # Business brief & run reports
```

---

## 7. Controls & Limitations

- **Observational Nature**: The dataset reflects historical purchasing logs without randomized promotional campaigns. Decision signals define hypotheses for testing rather than guaranteed revenue uplifts.
- **Wholesale Reseller Footprint**: Many high-spending accounts operate as commercial retailers with seasonal, lumpy purchasing intervals.
- **Unattributed Records (22.77%)**: Walk-in POS and guest transactions lacking customer identifiers are isolated in staging to prevent distorting account-level longitudinal histories.
