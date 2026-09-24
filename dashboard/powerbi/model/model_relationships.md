# Power BI Semantic Model & Relationship Specifications

## 1. Relational Schema Architecture (Star / Constellation)

The Power BI analytical model is constructed from verified, standardized reporting exports generated in `dashboard/powerbi/data_exports/`.

### 1.1 Dimension Tables
- **`dim_customer`** (Grain: 1 row per customer ID)
  - Primary Key: `customer_id`
  - Attributes: `primary_country`, `segment_name`, `behavioral_state`, `insufficient_history`
- **`dim_segment`** (Grain: 1 row per behavioral segment)
  - Primary Key: `segment_name`
  - Attributes: `primary_behavior`, `secondary_behavior`, `interpretation`, `possible_business_question`
- **`dim_date`** (Grain: 1 row per calendar day)
  - Primary Key: `full_date` / `date_key`
  - Attributes: `year_month`, `year_num`, `month_num`, `is_weekend`

### 1.2 Fact & Analytical Tables
- **`customer_summary`** (Grain: 1 row per customer account)
  - Key: `customer_id` (1-to-1 with `dim_customer`)
  - Measures: `lifetime_orders`, `total_value`, `recency_days`, `average_order_value`, `recent_90d_value`, `prior_90d_value`, `value_momentum_pct`
- **`monthly_summary`** (Grain: 1 row per calendar month)
  - Key: `year_month`
  - Measures: `active_customers`, `total_orders`, `total_items`, `total_value`, `average_order_value`
- **`state_transitions`** (Grain: 1 row per previous_state x current_state x month pair)
  - Keys: `previous_month`, `current_month`, `previous_state`, `current_state`
  - Measures: `customer_count`, `customer_share`
- **`decision_signals`** (Grain: 1 row per customer per triggered signal)
  - Foreign Key: `customer_id` (Many-to-1 to `customer_summary`)
  - Attributes: `signal_name`, `signal_strength`, `evidence_metric_1`, `evidence_metric_2`, `explanation`, `signal_limitation`
- **`data_controls`** (Grain: 1 row per audit control check)
  - Primary Key: `control_id`
  - Attributes: `control_name`, `population_affected`, `affected_pct`, `severity`, `status`, `impact`, `recommended_resolution`

---

## 2. Model Relationships & Cardinality

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `decision_signals` | `customer_id` | `customer_summary` | `customer_id` | Many to 1 (*:1) | Single (`customer_summary` filters `decision_signals`) |
| `customer_summary` | `segment_name` | `segment_summary` | `segment_name` | Many to 1 (*:1) | Both (Bidirectional for interactive slicing) |
| `state_transitions` | `current_month` | `monthly_summary` | `year_month` | Many to 1 (*:1) | Single |
| `cohort_summary` | `order_month` | `monthly_summary` | `year_month` | Many to 1 (*:1) | Single |

---

## 3. Storage & Refresh Recommendations
- **Import Mode**: Recommended for all dimension and aggregated summary tables. Total compressed footprint is < 15 MB.
- **DirectQuery**: Supported via PostgreSQL connector (`cbdil_analytics` database) for live audit queries against `staging.raw_retail_transactions`.
