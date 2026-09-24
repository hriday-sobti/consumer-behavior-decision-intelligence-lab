# Comprehensive Methodological Insights & Decision Register

## Overview

The Consumer Behavior Decision Intelligence Lab generates deterministic insights by evaluating mathematically rigorous conditions against the empirical customer distributions. No synthetic narratives or unverified assertions are permitted.

Every analytical finding adheres to the locked six-part structure:
1. **OBSERVATION**: What happened empirically?
2. **EVIDENCE**: Which metric and dataset proves it?
3. **INTERPRETATION**: What does the pattern mean descriptively?
4. **DECISION QUESTION**: What should an operational or commercial team investigate?
5. **POSSIBLE ACTION**: What targeted intervention could reasonably be evaluated?
6. **MEASUREMENT & GUARDRAIL**: How would success or unintended friction be quantified?
7. **LIMITATION**: What data or behavioral factors could make the conclusion unreliable?

---

### Finding 1: Extreme Value Concentration (Wholesale Pareto Distribution)

- **OBSERVATION**: Historical purchasing value is heavily concentrated in a tiny fraction of top-tier commercial accounts.
- **EVIDENCE**: 
  - Top 1% of eligible accounts generate **26.4%** of total gross purchase value.
  - Top 5% generate **53.8%** of total gross purchase value.
  - Top 20% generate **83.1%** of total gross purchase value.
  - Source: `analytics.customer_behavior_features` and `outputs/tables/customer_summary.csv`.
- **INTERPRETATION**: The business exhibits a wholesale/B2B dynamic where overall financial performance is governed by key commercial accounts rather than high-volume retail consumer traffic.
- **DECISION QUESTION**: Are account management, contract pricing, and inventory buffers prioritized for the top 5% revenue-generating accounts?
- **POSSIBLE ACTION**: Investigate establishing a dedicated Key Account desk with guaranteed inventory allocation and personalized fulfillment SLAs.
- **MEASUREMENT**: 
  - *Primary KPI*: Key-account on-time in-full (OTIF) fulfillment rate.
  - *Secondary KPI*: 90-day retention and reorder cadence.
  - *Guardrail*: Account-level cost-to-serve ratio to ensure support overhead remains accretive.
- **LIMITATION**: Observational purchase records do not reveal customer internal business solvency or distributor end-client churn.

---

### Finding 2: Deceleration Among High-Value Accounts (High-Value Softening)

- **OBSERVATION**: A critical cohort of top-quintile spenders is exhibiting severe contractions in recent purchasing velocity.
- **EVIDENCE**: 
  - **261 accounts** in the top 20% lifetime spend tier (lifetime value >= £2,910) show a >= 25% drop in recent 90-day spend relative to the prior 90-day baseline.
  - These accounts collectively account for over **£1.2 million** in historical revenue.
  - Source: `analytics.customer_decision_signal` (Signal `HIGH_VALUE_SOFTENING`).
- **INTERPRETATION**: Established commercial buyers are reducing order frequency or average order sizes, representing substantial revenue exposure.
- **DECISION QUESTION**: Did product stock-outs, shipping delays, or competitive supplier shifts cause order reductions for these accounts?
- **POSSIBLE ACTION**: Conduct proactive commercial account reviews and investigate SKU-level purchasing gaps for the 261 identified accounts.
- **MEASUREMENT**:
  - *Primary KPI*: 90-day spend recovery percentage post-review.
  - *Secondary KPI*: Reorder interval normalization.
  - *Guardrail*: Gross margin preservation (avoid uncoordinated price discounting).
- **LIMITATION**: Contraction may reflect lumpy wholesale inventory cycles or advance seasonal forward-buying rather than structural dissatisfaction.

---

### Finding 3: High Single-Order Customer Prevalence

- **OBSERVATION**: Nearly one-third of all identified customer accounts place exactly one order during the 24-month observation window and never transact again.
- **EVIDENCE**: 
  - Single-order customer rate is **31.5%** (1,855 out of 5,878 customer accounts).
  - Repeat customer rate is **68.5%** (4,023 multi-order accounts).
  - Source: `analytics.customer_behavior_features`.
- **INTERPRETATION**: While repeat customer rate is healthy for a wholesale distributor, initial acquisition has a significant drop-off before reaching a sustainable repeat cadence.
- **DECISION QUESTION**: What products or customer origins are disproportionately linked to single-order drop-offs?
- **POSSIBLE ACTION**: Test targeted second-order replenishment incentives between day 30 and day 60 post-acquisition for high-propensity catalog categories.
- **MEASUREMENT**:
  - *Primary KPI*: Second-order conversion rate within 60 days.
  - *Secondary KPI*: 90-day customer cumulative spend.
  - *Guardrail*: Return and cancellation rates on promotional second orders.
- **LIMITATION**: Some single-order purchasers are international retail gift-buyers with no structural intent to establish ongoing commercial trade.

---

### Finding 4: Emerging Customer Product Diversification

- **OBSERVATION**: A subset of newly acquired accounts rapidly broadens the variety of product categories purchased within their first 90 days.
- **EVIDENCE**: 
  - **440 emerging accounts** demonstrate positive product breadth momentum (>0% increase in unique SKUs).
  - Source: `analytics.customer_decision_signal` (Signal `EMERGING_BROADENING`).
- **INTERPRETATION**: New accounts that diversify their initial catalog purchasing establish deeper operational ties and higher long-term lifetime value.
- **DECISION QUESTION**: Can curated multi-category sample bundles accelerate catalog breadth for newly registered accounts?
- **POSSIBLE ACTION**: Implement category affinity recommendations during early checkout confirmation sequences.
- **MEASUREMENT**:
  - *Primary KPI*: Multi-category adoption rate within 90 days.
  - *Secondary KPI*: 180-day customer lifetime spend.
  - *Guardrail*: Customer unsubscribes or complaints regarding unsolicited suggestions.
- **LIMITATION**: Early SKU diversity can reflect one-time exploratory sampling rather than sustained reorder intent.
