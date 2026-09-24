# Final Pipeline Execution Run Report

- **Run Timestamp**: 2026-09-24 18:33:22 UTC
- **Pipeline Runtime**: 166.67 seconds
- **Dataset Source**: UCI Machine Learning Repository (Online Retail II, DOI: 10.24432/C5CG6D)
- **Source Observation Span**: 2009-12-01 07:45:00 to 2011-12-09 12:50:00 (approx. 24 continuous months)
- **Analytical Reference Date**: 2011-12-10 00:00:00

---

## 1. Data Ingestion & Event Classification Counts

| Analytical Event Class | Record Count | Share of Raw | Notes |
| :--- | :--- | :--- | :--- |
| **Total Raw Records** | 1,067,371 | 100.00% | Across sheets Year 2009-2010 and Year 2010-2011 |
| **Class 3: VALID_PURCHASE** | 779,423 | 75.45% | Positive price, positive quantity, valid customer ID |
| **Class 1: CANCELLATION** | 19,494 | 1.83% | Explicit 'C' invoice prefix |
| **Class 2: REVERSAL_OR_RETURN** | 3,462 | 0.32% | Non-cancellation negative adjustments |
| **Class 4: INVALID_OR_UNUSABLE**| 238,866 | 22.38% | Unattributed walk-ins and administrative lines |
| **Cleaned Staging Records** | 1,033,034 | - | Following exact composite key deduplication |

---

## 2. Customer Population & Eligibility

- **Total Distinct Identified Customer Accounts**: 5,878
- **Eligible Behavioral Segmentation Accounts**: 4,023 (68.4%)
- **Insufficient History Accounts**: 1,855 (31.6%)

---

## 3. Behavioral Segmentation Structure ($K=3$)

- **Selected Cluster Count ($K$)**: 3
- **Model Selection Criteria**: Smallest $K$ with Silhouette >= 90% of peak and all cluster shares >= 5%.
- **Silhouette Score**: 0.2749
- **Inertia**: 16,148.04

### Segment Distribution & Monetary Share:
- **High-Value Stable**: 1,164 accounts (28.9%) | Spend: £12,409,131 (75.0%) | Median Recency: 23d | Median Orders: 13
- **Emerging Engagement**: 1,084 accounts (27.0%) | Spend: £2,086,316 (12.6%) | Median Recency: 29d | Median Orders: 4
- **Low-Activity / Long-Recency**: 1,775 accounts (44.1%) | Spend: £2,054,244 (12.4%) | Median Recency: 266d | Median Orders: 3

---

## 4. Deterministic Decision Signals Trigger Inventory

Total Signals Triggered: **3,608** across 5,878 accounts.

- **POSITIVE_MOMENTUM**: 2,044 accounts
- **EMERGING_BROADENING**: 440 accounts
- **BROAD_ENGAGEMENT_SOFTENING**: 345 accounts
- **HIGH_FREQUENCY_LOW_VALUE**: 325 accounts
- **HIGH_VALUE_SOFTENING**: 261 accounts
- **HISTORICAL_VALUE_DORMANT**: 193 accounts

---

## 5. Audit & Validation Sign-Off

- **Automated SQL Validation Suite**: PASSED (0 violations detected)
- **PostgreSQL Schemas Active**: `staging`, `analytics`, `reporting`
- **Audit Control Status**: PASS (Zero critical failure conditions active)
