# Analytical Methodology & Mathematical Foundations

## 1. Reference Date & Analytical Windows

To prevent lookahead bias and ensure absolute reproducibility, the reference date is fixed programmatically as:
$$\text{REFERENCE\_DATE} = \max(\text{valid purchase date}) + 1\text{ day} = \text{2011-12-10 00:00:00}$$

### Standardized Time Horizons:
- **Full History**: All valid purchase transactions between `2009-12-01` and `2011-12-09`.
- **Primary Behavior Window**: 365 calendar days ending one day before reference date (`2010-12-10` to `2011-12-09`).
- **Recent Window**: 90 calendar days ending one day before reference date (`2011-09-11` to `2011-12-09`).
- **Prior Window**: 90 calendar days immediately preceding the recent window (`2011-06-13` to `2011-09-10`).

---

## 2. Customer Longitudinal Eligibility Rule

To avoid distorting interval metrics and momentum calculations with one-off or brand-new accounts:
$$\text{Eligible Customer} \iff (\text{Orders} \ge 2) \land (\text{Tenure} \ge 90\text{ days})$$

Accounts that fail this criterion are flagged as `insufficient_history = TRUE`. They are **never deleted**, remaining fully auditable across overview population summaries while being excluded from unsupervised clustering.

---

## 3. The Five Behavioral Dimensions

Rather than reducing customer behavior to a simplistic composite score, the architecture quantifies accounts across five distinct dimensions:
1. **Value**: Cumulative gross spend, Average Order Value (AOV), median basket value.
2. **Activity**: Recency intervals (days since last purchase), transaction count, active monthly presence.
3. **Breadth**: Unique stock codes (SKUs) purchased, average items per basket.
4. **Stability**: Coefficient of variation (CV) of interpurchase day intervals ($\sigma_{\text{gap}} / \mu_{\text{gap}}$).
5. **Momentum**: Recent 90-day vs prior 90-day percentage change across value, frequency, and product breadth.

$$\text{Momentum}_{\text{Value}} = \frac{\text{Value}_{\text{recent}} - \text{Value}_{\text{prior}}}{\text{Value}_{\text{prior}}} \quad (\text{when } \text{Value}_{\text{prior}} > 0)$$

---

## 4. Behavioral Clustering Methodology

### Feature Transformation & Scaling
- Positive right-skewed variables (`total_value`, `transaction_count`, `product_count`) receive $\log(1 + x)$ transformations.
- Momentum variables are clipped to $[-1.0, 5.0]$ to guard against hyper-inflated small-baseline percentage spikes.
- Primary feature vector:
  $$\mathbf{x} = \begin{bmatrix} \log(1 + \text{spend}), & \log(1 + \text{orders}), & \text{recency}, & \log(1 + \text{skus}), & \mu_{\text{gap}}, & \text{mom}_{\text{val}}, & \text{mom}_{\text{freq}} \end{bmatrix}^T$$
- Standardized via Z-score normalization ($\mu=0, \sigma=1$).

### Deterministic Model Selection Rule
Evaluate $K \in \{3, 4, 5, 6\}$ under fixed seed `42`:
$$\text{Choose smallest } K \text{ such that } \text{Silhouette}(K) \ge 0.90 \times \max_{k}(\text{Silhouette}(k)) \text{ and } \min_{j}(\text{Share}(C_j)) \ge 5\%$$

*Empirical Result*: $K=3$ achieved highest silhouette score (0.2749) with well-balanced cluster sizes (28.9%, 26.9%, 44.1%), strictly satisfying the rule.

---

## 5. Behavioral Lifecycle State Machine

States are evaluated as of month-end or reference date with strict priority precedence:
1. **`REACTIVATED`**: Transacted in recent period AND zero purchases during preceding 120 days AND has transaction history prior to gap.
2. **`EMERGING`**: First transaction occurred $\le 90$ days prior to evaluation date.
3. **`DORMANT`**: Elapsed recency $> 120$ days.
4. **`SOFTENING`**: Remains within 120 days recency BUT recent order frequency $\le 0.75 \times \text{prior frequency}$.
5. **`ENGAGED`**: All remaining active eligible accounts.
