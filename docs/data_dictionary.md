# Data Dictionary

## Table Grain Architecture Overview

| Table Name | Schema | Grain | Record Count | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `raw_retail_transactions` | `staging` | 1 transaction line item | 1,033,034 | Deduplicated raw staging table retaining event classification. |
| `dim_customer` | `analytics` | 1 customer account | 5,878 | Master customer entity with longitudinal bounds. |
| `dim_product` | `analytics` | 1 stock code | 5,305 | Distinct catalog products and fee classifications. |
| `dim_date` | `analytics` | 1 calendar day | 739 | Full date dimensional lookup across observation span. |
| `dim_country` | `analytics` | 1 billing country | 43 | Sovereign market reference entity. |
| `fact_order` | `analytics` | 1 invoice / basket | 36,969 | Order-grain transaction header with rolled-up spend and line count. |
| `fact_transaction` | `analytics` | 1 invoice line item | 779,423 | Valid purchase line items for behavioral aggregation. |
| `customer_behavior_features` | `analytics` | 1 customer account | 5,878 | 5-dimensional customer behavioral representation. |
| `customer_rfm` | `analytics` | 1 customer account | 5,878 | Supporting quintile RFM scores and composite codes. |
| `customer_segment` | `analytics` | 1 eligible customer | 4,023 | K-Means behavioral segment assignment and coordinates. |
| `segment_profile` | `analytics` | 1 behavioral segment | 3 | Behavioral cluster profiles, medians, and business inquiries. |
| `customer_monthly_snapshot`| `analytics` | 1 customer-month | 98,557 | Longitudinal monthly customer activity and state tracking. |
| `customer_state_history` | `analytics` | 1 month transition | 92,679 | Month-over-month individual customer state changes. |
| `state_transition_matrix` | `analytics` | 1 state pair / month | 233 | Aggregated state migration counts and transition shares. |
| `customer_decision_signal` | `analytics` | 1 triggered signal | 3,608 | Deterministic behavioral decision flags with severity and audit limits. |
| `decision_strategy` | `analytics` | 1 strategic playbook | 6 | Decision-strategy catalog linking signals to testing designs. |

---

## Detailed Column Specifications

### `analytics.customer_behavior_features`
- **`customer_id`** (VARCHAR(64), PK): Unique customer identifier.
- **`first_purchase_date`** (TIMESTAMP, NOT NULL): Earliest recorded valid purchase timestamp.
- **`last_purchase_date`** (TIMESTAMP, NOT NULL): Latest recorded valid purchase timestamp.
- **`customer_lifetime_days`** (INTEGER, NOT NULL): Elapsed calendar days between first purchase and reference date (`2011-12-10`).
- **`recency_days`** (INTEGER, NOT NULL): Elapsed calendar days between last purchase and reference date.
- **`transaction_count`** (INTEGER, NOT NULL): Total distinct valid purchase orders placed across full history.
- **`active_month_count`** (INTEGER, NOT NULL): Number of distinct calendar months with at least one valid purchase.
- **`frequency_per_active_month`** (NUMERIC(10, 4), NOT NULL): Ratio of total transactions to active months.
- **`total_value`** (NUMERIC(14, 4), NOT NULL): Cumulative monetary spend across all valid purchases (£).
- **`average_order_value`** (NUMERIC(14, 4), NOT NULL): Mean order value (`total_value / transaction_count`).
- **`median_order_value`** (NUMERIC(14, 4), NOT NULL): Median order value.
- **`average_items_per_order`** (NUMERIC(12, 4), NOT NULL): Mean total units purchased per order.
- **`product_count`** (INTEGER, NOT NULL): Total count of distinct stock codes purchased across full history.
- **`purchase_day_count`** (INTEGER, NOT NULL): Count of distinct calendar days with transactions.
- **`mean_interpurchase_days`** (NUMERIC(10, 2), NULL): Average elapsed days between successive transaction dates.
- **`median_interpurchase_days`** (NUMERIC(10, 2), NULL): Median elapsed days between successive transaction dates.
- **`interpurchase_gap_std`** (NUMERIC(10, 2), NULL): Standard deviation of interpurchase intervals.
- **`interpurchase_gap_cv`** (NUMERIC(10, 4), NULL): Coefficient of variation of interpurchase intervals (`std / mean`).
- **`recent_90d_value`** (NUMERIC(14, 4), NOT NULL): Total spend in the 90 days ending one day before reference date.
- **`prior_90d_value`** (NUMERIC(14, 4), NOT NULL): Total spend in the 90-day baseline preceding the recent window.
- **`recent_90d_transactions`** (INTEGER, NOT NULL): Order count in recent 90-day window.
- **`prior_90d_transactions`** (INTEGER, NOT NULL): Order count in prior 90-day baseline.
- **`value_change_pct`** (NUMERIC(10, 4), NULL): Percentage spend momentum `(recent - prior) / prior`.
- **`frequency_change_pct`** (NUMERIC(10, 4), NULL): Percentage frequency momentum.
- **`product_breadth_change_pct`** (NUMERIC(10, 4), NULL): Percentage SKU breadth momentum.
- **`reversal_line_count`** (INTEGER, NOT NULL): Count of cancellation or reversal line items.
- **`reversal_value`** (NUMERIC(14, 4), NOT NULL): Absolute gross value of cancellations and reversals (£).
- **`reversal_rate`** (NUMERIC(10, 4), NOT NULL): Ratio of reversal value to gross spend `reversal / (spend + reversal)`.
- **`country`** (VARCHAR(128), NOT NULL): Primary geographic billing country.
- **`insufficient_history`** (BOOLEAN, NOT NULL): Flag indicating customer has < 2 orders or < 90 days tenure.
