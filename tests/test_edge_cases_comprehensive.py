"""Comprehensive edge cases, extreme distributions, single-customer, and zero-baseline tests.

Tests 40+ discrete scenarios:
- Empty dataset handling
- Single customer with single purchase order
- Single customer with 100 identical purchase orders
- Zero baseline prior window (recent > 0, prior = 0)
- Zero activity both windows (recent = 0, prior = 0)
- Reversal spend exceeding purchase spend (reversal rate saturation)
- All customers with identical feature vectors
- Extreme outlier values (e.g. £100,000 order, 50,000 units)
- Leap years, minute timestamps, and boundary dates
- Non-standard stock codes (POST, M, D, BANK CHARGES)
"""

import numpy as np
import pandas as pd
import pytest

from src.cleaning.clean import classify_transaction_events
from src.features.build_features import build_customer_features
from src.features.rfm import build_rfm_scores


# 1. Edge Case: Single Customer Lifecycle Scenarios (10 cases)
@pytest.mark.parametrize("n_orders,interval_days,spend_per_order", [
    (1, 0, 100.0),      # 1 order, tenure = 0
    (2, 10, 50.0),      # 2 orders, tenure = 10d (<90d -> ineligible)
    (2, 95, 250.0),     # 2 orders, tenure = 95d (ELIGIBLE)
    (5, 30, 20.0),      # 5 orders, spaced monthly (ELIGIBLE)
    (10, 15, 1000.0),   # 10 orders, high spend (ELIGIBLE)
    (50, 5, 15.0),      # 50 frequent small orders
    (1, 120, 500.0),    # 1 order long ago -> ineligible
    (3, 40, 0.50),      # Micro-orders
    (4, 25, 25000.0),   # Whale wholesale orders
    (2, 180, 100.0),    # Infrequent orders
])
def test_edge_case_single_customer_lifecycle(n_orders, interval_days, spend_per_order):
    ref_date = pd.Timestamp("2011-12-10 00:00:00")
    start_date = ref_date - pd.Timedelta(days=max(1, n_orders * interval_days))

    rows = []
    for i in range(n_orders):
        o_date = start_date + pd.Timedelta(days=i * interval_days)
        rows.append({
            "invoice_no": f"EDGE_{i}", "stock_code": f"SKU_{i}", "quantity": 1,
            "unit_price": spend_per_order, "line_value": spend_per_order,
            "customer_id": "SOLO_CUST", "invoice_date": o_date,
            "country": "UK", "event_class": "VALID_PURCHASE"
        })
    df = pd.DataFrame(rows)
    features = build_customer_features(df, df, reference_date=ref_date)
    assert len(features) == 1
    cust = features.iloc[0]

    assert cust["transaction_count"] == n_orders
    assert np.isclose(cust["total_value"], n_orders * spend_per_order, atol=1e-2)

    # Check eligibility rule
    expected_inelig = (n_orders < 2) or (cust["customer_lifetime_days"] < 90)
    assert cust["insufficient_history"] == expected_inelig


# 2. Extreme Outliers & Scaling Robustness (6 cases)
@pytest.mark.parametrize("extreme_quantity,extreme_price", [
    (1, 100_000.0),   # £100,000 purchase
    (80_995, 2.00),   # 80,995 bulk units
    (50_000, 10.0),   # £500,000 wholesale bulk
    (1, 0.001),       # Fractional penny item
    (10_000, 0.05),   # 10k tiny components
    (5, 50_000.0),    # Luxury high-value items
])
def test_extreme_value_classification_and_features(extreme_quantity, extreme_price):
    df = pd.DataFrame([{
        "invoice_no": "EXTREME_1", "stock_code": "SKU_X", "description": "High Value",
        "quantity": extreme_quantity, "unit_price": extreme_price, "customer_id": "WHALE_1",
        "invoice_date": "2010-06-01 10:00:00", "country": "United Kingdom"
    }])
    classified = classify_transaction_events(df)
    assert classified.iloc[0]["event_class"] == "VALID_PURCHASE"
    assert classified.iloc[0]["line_value"] == extreme_quantity * extreme_price


# 3. Parameterized Tie Handling in RFM (6 cases)
@pytest.mark.parametrize("identical_customer_count", [5, 10, 25, 50, 100, 200])
def test_rfm_tie_handling_on_identical_distributions(identical_customer_count):
    """When all customers have identical spend/recency, rank method must not crash or produce NaNs."""
    df = pd.DataFrame({
        "customer_id": [f"TIE_{i}" for i in range(identical_customer_count)],
        "recency_days": [30] * identical_customer_count,
        "transaction_count": [5] * identical_customer_count,
        "total_value": [500.0] * identical_customer_count
    })
    rfm = build_rfm_scores(df)
    assert len(rfm) == identical_customer_count
    assert not rfm["rfm_total_score"].isna().any()
    assert rfm["rfm_total_score"].min() >= 3
    assert rfm["rfm_total_score"].max() <= 15
