# Stakeholder Questions & Analytical Mapping

This document provides non-technical and executive stakeholders with an explicit mapping between strategic business inquiries, the answering dashboard page, source tables, and key metrics.

| Strategic Stakeholder Question | Answering Surface | Source Database Table | Primary Metric / Dimension |
| :--- | :--- | :--- | :--- |
| **"How large is our active customer base and what is our gross revenue trajectory?"** | Dashboard Page 1: Overview | `reporting.monthly_summary` | `active_customers`, `total_value`, `total_orders`, `average_order_value` |
| **"How heavily concentrated is total revenue across our top buyers?"** | Dashboard Page 1: Overview | `reporting.customer_summary` | Cumulative Lorenz curve; Top 5% spend share (`53.8%`) and Top 20% share (`83.1%`) |
| **"Which behavioral customer groups are genuinely distinct, and how much value does each contribute?"** | Dashboard Page 2: Segments | `analytics.segment_profile` | `segment_name`, `customer_count`, `value_share`, `median_recency`, `median_frequency` |
| **"Which specific catalog product categories drive engagement across each segment?"** | Dashboard Page 3: Segment Deep Dive | `reporting.product_summary` | `product_count`, `total_quantity`, `revenue_share` |
| **"Where is customer behavior moving over time, and what proportion of accounts lapse into dormancy each month?"** | Dashboard Page 4: Behavior Over Time | `analytics.state_transition_matrix` | Month-over-month state transitions (`previous_state` &rarr; `current_state`) |
| **"Which historically high-value accounts show severe recent contractions in purchasing cadence?"** | Dashboard Page 5: Decision Signals | `analytics.customer_decision_signal` | Signal `HIGH_VALUE_SOFTENING` (`261` accounts; spend $\ge$ P80 and momentum $\le -25\%$) |
| **"Why is a specific customer classified under a particular segment or signal?"** | Dashboard Page 6: Customer Explorer | `reporting.customer_summary` & `customer_decision_signal` | Customer diagnostic card: recency, frequency, spend momentum, and audit limitations |
| **"What data-quality or sampling issues could make our analytical conclusions unreliable?"** | Dashboard Page 7: Data & Controls | `reporting.data_control_summary` | Control audit statuses (`PASS`, `WARNING`, `FAIL`), unassigned customer rate, and reversal rates |
| **"How should we measure whether a proposed account intervention actually worked?"** | Documentation: Decision Framework | `analytics.decision_strategy` | Primary recovery KPI vs matched holdout control group; guardrail reversal rate |
