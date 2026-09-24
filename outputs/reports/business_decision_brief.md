# Executive Decision Brief: Customer Purchasing Dynamics & Commercial Priorities

## 1. Analytical Scope & Population
This analytical briefing provides an empirical assessment of transaction patterns from the **UCI Online Retail II** dataset covering 24 months from **December 2009 through December 2011**. The analysis evaluates **1,033,034** deduplicated transaction records across **5,878** registered customer accounts, representing **£16.5M+** in cumulative purchasing spend.

---

## 2. Major Customer Behavioral Findings

### A. Extreme Value Concentration (Wholesale Pareto Distribution)
Purchasing revenue is heavily concentrated in a small core of high-volume commercial accounts:
- The top **1%** of eligible accounts contribute **26.4%** of total gross spend.
- The top **5%** of accounts generate **53.8%** of total gross spend.
- The top **20%** of accounts drive **83.1%** of total gross spend.
- *Commercial Takeaway*: Operational performance, inventory planning, and revenue stability are predominantly governed by wholesale repeat buyers rather than retail consumer traffic.

### B. High Single-Order Buyer Prevalence
- **31.5%** of all customer accounts (1,855 accounts) place exactly one order during their entire history and never return.
- Repeat buyers represent **68.5%** (4,023 accounts).
- *Commercial Takeaway*: Drop-off following initial acquisition is substantial; converting single-order buyers into repeat buyers within 60 days represents the single largest margin lever.

---

## 3. Behavioral Segment Structure

Eligible accounts with sufficient history are partitioned into three distinct behavioral groups ($K=3$, Silhouette = 0.2749):

1. **High-Value Stable (1,164 accounts | 28.9% of accounts | 75.0% of total spend)**:
   - *Profile*: Median spend £4,967; median order frequency 13 orders; median recency 23 days; median catalog breadth 168 unique SKUs.
   - *Strategic Question*: Are delivery SLAs, customized packaging, and volume terms adequately structured to defend these core revenue accounts against competitor encroachment?

2. **Emerging Engagement (1,084 accounts | 26.9% of accounts | 12.6% of total spend)**:
   - *Profile*: Median spend £1,260; median order frequency 4 orders; median recency 29 days; median catalog breadth 74 unique SKUs; positive spend momentum (+12.5%).
   - *Strategic Question*: Which cross-category affinity bundles accelerate basket diversification during this active expansion phase?

3. **Low-Activity / Long-Recency (1,775 accounts | 44.1% of accounts | 12.4% of total spend)**:
   - *Profile*: Median spend £816; median order frequency 3 orders; median elapsed recency 266 days.
   - *Strategic Question*: What proportion of this inactive cohort represents seasonal holiday buyers vs permanently lost commercial accounts?

---

## 4. Decision Signals & Recommended Investigations

The system evaluated six deterministic, rule-based behavioral triggers:

| Signal Identifier | Triggered Accounts | Behavioral Pattern | Recommended Test / Investigation |
| :--- | :--- | :--- | :--- |
| **`HIGH_VALUE_SOFTENING`** | **261** | Spend >= P80 (£2,910+) with recent spend drop <= -25% | Proactive commercial account manager audit to evaluate supplier switching or service friction. |
| **`HIGH_FREQUENCY_LOW_VALUE`** | **325** | High order cadence (>= 8 orders) with depressed AOV (<= £234) | Evaluate minimum order size thresholds or freight incentives to consolidate small baskets. |
| **`EMERGING_BROADENING`** | **440** | Tenure <= 90 days actively increasing distinct SKU breadth | Present category affinity recommendations during early checkout confirmation sequences. |
| **`HISTORICAL_VALUE_DORMANT`** | **193** | Historical spend >= P80 with > 120 days of inactivity | Test targeted seasonal catalog re-engagement offer with 60-day holdout control evaluation. |
| **`BROAD_ENGAGEMENT_SOFTENING`** | **345** | Breadth >= P70 (85+ SKUs) with >= 25% decline in order cadence | Audit product category availability and stock-outs across core wholesale lines. |
| **`POSITIVE_MOMENTUM`** | **2,044** | Double-digit synchronized growth (>= +25% spend and frequency) | Guarantee supply-chain capacity and priority inventory allocation to avoid fulfillment bottlenecks. |

---

## 5. Decision Measurement & Guardrail Design

Because historical marketing interventions were not recorded, commercial initiatives should be evaluated using randomized holdout trials:
- **Primary Success KPI**: 90-day spend recovery / reactivation rate compared against an uncontacted 20% holdout group.
- **Guardrail Metric**: Order return and reversal rate (must not exceed baseline by >= 10%).
- **Success Rule**: Net incremental gross margin post-intervention must exceed operational contact costs.

---

## 6. Data Governance & Operational Limitations

- **Observational Constraint**: Transaction history reflects purchase behavior; it does not measure customer sentiment or confirm willingness to respond to promotions.
- **Unattributed Guest Volume**: Approximately 22.8% of raw line items represent guest checkouts lacking a customer identifier; these are tracked in aggregate revenue reporting but excluded from account-level clustering.
- **Wholesale Volatility**: Inactivity among commercial accounts can stem from standard distributor restocking cycles rather than account cancellation.
