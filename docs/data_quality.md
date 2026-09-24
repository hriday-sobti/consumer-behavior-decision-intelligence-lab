# Data Quality Investigation & Profile

## 1. Executive Summary

This document reports the baseline data quality investigation performed on the raw **UCI Online Retail II** dataset (`data/raw/online_retail_II.xlsx`).

- **Total Source Records**: 1,067,371 rows across two longitudinal sheets (`Year 2009-2010` and `Year 2010-2011`).
- **Observation Span**: December 1, 2009 07:45:00 through December 9, 2011 12:50:00 (approx. 24 continuous months).
- **Distinct Customers**: 5,942 identified customer IDs (plus 243,007 unassigned transaction rows).
- **Distinct Invoices**: 53,628 unique invoice numbers.
- **Distinct Stock Codes**: 5,305 catalog codes.
- **Geographic Scope**: 43 distinct countries (heavily concentrated in the United Kingdom).

---

## 2. Field-Level Statistical Profile

Summary of distributions extracted directly from the raw records:

| Field Name | Type | Missing Count | Missing % | Distinct | Min | Median | Max | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `invoice_no` | string | 0 | 0.00% | 53,628 | - | - | - | Prefix 'C' indicates cancellations. |
| `stock_code` | string | 0 | 0.00% | 5,305 | - | - | - | Includes non-inventory items (POST, D, M, etc.). |
| `description` | string | 4,382 | 0.41% | 5,699 | - | - | - | Occasional nulls/whitespace on administrative entries. |
| `quantity` | integer | 0 | 0.00% | 1,057 | -80,995 | 3 | 80,995 | Negative values indicate reversals/cancellations. Extreme symmetric values observed. |
| `invoice_date` | timestamp | 0 | 0.00% | 47,635 | 2009-12-01 | - | 2011-12-09 | Discrete transaction timestamp down to the minute. |
| `unit_price` | float | 0 | 0.00% | 2,807 | -53,594.36 | 2.10 | 38,970.00 | Negative prices indicate debt/bad debt write-offs. Zero prices indicate samples or manual audits. |
| `customer_id` | float/int | 243,007 | 22.77% | 5,942 | 12346 | 15255 | 18287 | 22.77% of rows lack a customer ID (guest checkouts / POS walk-ins). |
| `country` | string | 0 | 0.00% | 43 | - | - | - | Sovereign origin of transaction billing. |
| `source_sheet` | string | 0 | 0.00% | 2 | - | - | - | Tracking provenance across the 2-year workbook. |

---

## 3. Systematic Anomalies & Quality Risks

### 3.1 Missing Customer Identifiers (243,007 rows / 22.77%)
- **Description**: Approximately 22.8% of line items do not record a `customer_id`.
- **Analytical Impact**: While valid at the transaction level for aggregate product revenue, these records cannot be linked to a behavioral customer history.
- **Handling**: These records are classified as `INVALID_OR_UNUSABLE` for customer-grain feature engineering and behavioral segmentation, but retained in staging/order-level accounting for control verification.

### 3.2 Cancellations (`C` prefix, 19,494 rows / 1.83%)
- **Description**: Invoices beginning with `C` or `c` denote formalized order cancellations (e.g. `C489449`).
- **Analytical Impact**: Including cancellations as positive purchase events would inflate order frequencies and bias recency.
- **Handling**: Classified as `CLASS 1: CANCELLATION` with highest precedence. Kept isolated from gross purchase value and used to calculate customer reversal rates.

### 3.3 Reversals and Negative Quantities (22,950 rows / 2.15%)
- **Description**: 22,950 rows feature `quantity < 0`. Of these, 19,494 are explicit cancellations; the remaining 3,456 represent damaged stock adjustments, inventory corrections, or return lines without standard `C` prefixes.
- **Handling**: Classified as `CLASS 2: REVERSAL_OR_RETURN`.

### 3.4 Corrupted Negative Unit Prices (5 rows)
- **Description**: Exactly 5 rows feature negative unit prices (e.g., `-53594.36`, `-38970.00`) accompanied by descriptions such as `Adjust bad debt`.
- **Handling**: Classified as `CLASS 4: INVALID_OR_UNUSABLE` (severe accounting adjustment, not a retail trade event).

### 3.5 Zero Unit Prices (6,202 rows / 0.58%)
- **Description**: 6,202 line items have `unit_price == 0`.
- **Handling**: Classified as `CLASS 4: INVALID_OR_UNUSABLE` for value modeling, as they represent administrative entries, samples, or lost inventory audits.

### 3.6 Line-Item Duplicates (34,337 rows / 3.22%)
- **Description**: Repeated line items with identical `invoice_no`, `stock_code`, `customer_id`, `invoice_date`, `quantity`, and `unit_price`.
- **Handling**: Deduplicated in the cleaned transaction fact table to ensure true unit velocity and basket line counts.

---

## 4. Control Checks & Gate Sign-Off

- **Raw Immutability**: Raw files in `data/raw/` are strictly read-only.
- **Auditability**: Every classified event is assigned an explicit, deterministic event class tag.
- **Line Value Rule**: Explicitly computed as `Quantity * UnitPrice` with float/numeric verification.
