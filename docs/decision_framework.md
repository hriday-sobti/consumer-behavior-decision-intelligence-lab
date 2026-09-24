# Decision-Strategy Catalog & Testing Framework

## 1. Principles of Decision Measurement

In observational commercial transaction datasets, **treatment assignment and marketing interventions are not observed**. Therefore:
- The system **never claims causal effects** from historical correlations.
- The system **never promises guaranteed revenue uplifts**.
- Instead, each decision strategy establishes a structured, testable **measurement design** that defines target eligibility, control group concepts, primary success KPIs, and guardrail metrics.

---

## 2. Decision Strategy Catalog

| Strategy ID | Strategy Name | Target Behavioral Signal | Primary KPI | Secondary KPI | Guardrail Metric | Evaluation Window |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **STRAT-01** | High-Value Account Outreach & Service Audit | `HIGH_VALUE_SOFTENING` | 90-day spend recovery % | Order cadence stabilization rate | Return and reversal rate on subsequent orders | 90 Days post-outreach |
| **STRAT-02** | Basket Expansion & Minimum Tier Incentives | `HIGH_FREQUENCY_LOW_VALUE` | Average Order Value (AOV) | Gross revenue per shipment | Overall order frequency (ensure order count does not drop faster than AOV rises) | 60 Days post-launch |
| **STRAT-03** | Onboarding Cross-Category Nurturing | `EMERGING_BROADENING` | Repeat purchase rate within 60 days | Catalog breadth (unique categories) | Return rates on newly introduced categories | 60 Days post-onboarding |
| **STRAT-04** | Tier-1 Dormancy Reactivation Campaign | `HISTORICAL_VALUE_DORMANT` | Account reactivation rate | Incremental 90-day order value | Discount margin erosion / low-value redemptions | 60 Days post-campaign |
| **STRAT-05** | Broad Catalog Engagement Retention | `BROAD_ENGAGEMENT_SOFTENING`| Order frequency recovery | Active category retention rate | Cancellation rate on backordered SKUs | 90 Days post-audit |
| **STRAT-06** | High-Momentum VIP Capacity & Fulfillment Protection | `POSITIVE_MOMENTUM` | OTIF order fulfillment rate | 90-day spend continuity | Delivery delay rate and backorder complaints | Ongoing quarterly monitoring |

---

## 3. Testing Design Template

For every prospective commercial trial, teams should follow this standardized evaluation template:

1. **Target Population**: Strictly defined by deterministic SQL selection against `analytics.customer_decision_signal`.
2. **Control Concept**: Hold out a randomized 20% matched sample of eligible accounts receiving standard operating procedures (no targeted contact or promotion).
3. **Primary Effect Metric**: Difference-in-differences in primary KPI between target and holdout groups across the evaluation window:
   $$\Delta_{\text{treatment}} = (\text{KPI}_{\text{target, post}} - \text{KPI}_{\text{target, pre}}) - (\text{KPI}_{\text{control, post}} - \text{KPI}_{\text{control, pre}})$$
4. **Guardrail Decision Rule**: If the guardrail metric exceeds baseline thresholds by $\ge 10\%$, immediately halt the test.
