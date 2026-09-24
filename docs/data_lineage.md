# Data Lineage Architecture

This document tracks the complete end-to-end data lineage for all critical reporting metrics from raw ingestion through to final decision views.

---

## 1. Lineage Matrix

### Total Historical Spend (`total_value`)
- **Source Field**: `Quantity` and `Price` in sheet `Year 2009-2010` and `Year 2010-2011` of `data/raw/online_retail_II.xlsx`.
- **Transformation 1 (Ingestion & Cleaning)**: Computed as `line_value = Quantity * Price` using explicit numeric casting.
- **Transformation 2 (Classification)**: Filtered to `event_class = 'VALID_PURCHASE'` where `Quantity > 0`, `Price > 0`, `customer_id IS NOT NULL`, and invoice does not start with `C`.
- **Transformation 3 (Aggregation)**: Summed per customer: `SUM(line_value) GROUP BY customer_id`.
- **Destination Table**: `analytics.customer_behavior_features.total_value` &rarr; `reporting.customer_summary.total_value`.

### Recency Days (`recency_days`)
- **Source Field**: `InvoiceDate` in raw workbook.
- **Transformation 1**: Extracted latest purchase timestamp per customer: `max_date = MAX(invoice_date)`.
- **Transformation 2**: Fixed analytical reference date: `ref_date = MAX(valid_invoice_date) + 1 day = 2011-12-10 00:00:00`.
- **Transformation 3**: Elapsed integer days: `DATEDIFF(ref_date, max_date)`.
- **Destination Table**: `analytics.customer_behavior_features.recency_days`.

### Spend Momentum % (`value_change_pct`)
- **Source Field**: `InvoiceDate` and `line_value` in `fact_transaction`.
- **Transformation 1**: Aggregated spend in recent 90-day window (`2011-09-11` to `2011-12-09`): `recent_90d_value`.
- **Transformation 2**: Aggregated spend in prior 90-day baseline window (`2011-06-13` to `2011-09-10`): `prior_90d_value`.
- **Transformation 3**: Safe division percentage calculation:
  $$\text{value\_change\_pct} = \begin{cases} \frac{\text{recent} - \text{prior}}{\text{prior}} & \text{if } \text{prior} > 0 \\ 1.0 & \text{if } \text{prior} = 0 \land \text{recent} > 0 \\ 0.0 & \text{otherwise} \end{cases}$$
- **Destination Table**: `analytics.customer_behavior_features.value_change_pct`.

### Behavioral Lifecycle State (`behavioral_state`)
- **Source Field**: Aggregated order history over calendar months.
- **Transformation**: Evaluated under deterministic priority rules:
  1. `REACTIVATED` (Recent purchase + zero orders in preceding 120d + prior history)
  2. `EMERGING` (Acquisition tenure $\le 90$ days)
  3. `DORMANT` (Elapsed recency $> 120$ days)
  4. `SOFTENING` (Recency $\le 120$ days, prior orders $> 0$, and order drop $\ge 25\%$)
  5. `ENGAGED` (All remaining active accounts)
- **Destination Table**: `analytics.customer_monthly_snapshot.behavioral_state`.

### Behavioral Segment (`segment_name`)
- **Source Field**: Primary 7-feature standardized vector from `analytics.customer_behavior_features`.
- **Transformation**: K-Means clustering ($K=3$, seed `42`), evaluated via silhouette maximization rule, followed by behavior-based descriptive naming.
- **Destination Table**: `analytics.customer_segment.segment_name`.
