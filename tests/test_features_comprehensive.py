"""Unit tests for customer eligibility criteria, RFM quintiles, and momentum calculations."""

import numpy as np
import pandas as pd
import pytest

from src.features.build_features import build_customer_features
from src.features.rfm import build_rfm_scores


# 1. Eligibility Rule Boundary Scenarios (8 cases)
@pytest.mark.parametrize("order_count,tenure_days,expected_insufficient", [
    (1, 10, True),    # <2 orders, <90d
    (1, 90, True),    # 1 order, exactly 90d -> still insufficient (<2 orders)
    (1, 150, True),   # 1 order, >90d -> insufficient
    (2, 89, True),    # 2 orders, 89 days -> insufficient (<90d)
    (2, 90, False),   # exactly 2 orders, exactly 90 days -> ELIGIBLE
    (2, 100, False),  # 2 orders, >90 days -> ELIGIBLE
    (5, 45, True),    # 5 orders, <90 days -> insufficient
    (10, 365, False), # 10 orders, 365 days -> ELIGIBLE
])
def test_parameterized_customer_eligibility(order_count, tenure_days, expected_insufficient):
    ref_date = pd.Timestamp("2011-12-10 00:00:00")
    first_date = ref_date - pd.Timedelta(days=tenure_days)
    
    rows = []
    for i in range(order_count):
        # space orders between first_date and ref_date
        o_date = first_date + pd.Timedelta(days=i * max(1, int(tenure_days / max(1, order_count))))
        rows.append({
            "invoice_no": f"INV_{i}", "stock_code": f"SKU_{i}", "quantity": 1,
            "unit_price": 50.0, "line_value": 50.0, "customer_id": "TEST_CUST",
            "invoice_date": o_date, "country": "United Kingdom", "event_class": "VALID_PURCHASE"
        })
    valid_df = pd.DataFrame(rows)
    all_df = valid_df.copy()

    features = build_customer_features(all_df, valid_df, reference_date=ref_date)
    assert features.iloc[0]["insufficient_history"] == expected_insufficient


# 2. Spend & Momentum Percentage Scenarios (10 cases)
@pytest.mark.parametrize("prior_val,recent_val,expected_change", [
    (100.0, 150.0, 0.50),    # +50%
    (100.0, 100.0, 0.00),    # 0%
    (100.0, 50.0, -0.50),    # -50%
    (100.0, 75.0, -0.25),    # -25%
    (100.0, 0.0, -1.00),     # -100% complete drop
    (200.0, 400.0, 1.00),    # +100%
    (0.0, 100.0, 1.00),      # Zero baseline with recent spend -> +1.0
    (0.0, 0.0, 0.00),        # Zero baseline with zero spend -> 0.0
    (50.0, 25.0, -0.50),     # -50%
    (1000.0, 1250.0, 0.25),  # +25%
])
def test_parameterized_momentum_calculation(prior_val, recent_val, expected_change):
    ref_date = pd.Timestamp("2011-12-10 00:00:00")
    # recent window: last 90 days (e.g. 2011-11-01)
    # prior window: days -180 to -91 (e.g. 2011-08-01)
    rows = []
    # Base order to ensure 2 orders & tenure
    rows.append({
        "invoice_no": "BASE", "stock_code": "SKU0", "quantity": 1,
        "unit_price": 10.0, "line_value": 10.0, "customer_id": "MOM_CUST",
        "invoice_date": ref_date - pd.Timedelta(days=200), "country": "UK", "event_class": "VALID_PURCHASE"
    })
    if prior_val > 0:
        rows.append({
            "invoice_no": "PRIOR", "stock_code": "SKU1", "quantity": 1,
            "unit_price": prior_val, "line_value": prior_val, "customer_id": "MOM_CUST",
            "invoice_date": ref_date - pd.Timedelta(days=120), "country": "UK", "event_class": "VALID_PURCHASE"
        })
    if recent_val > 0:
        rows.append({
            "invoice_no": "RECENT", "stock_code": "SKU2", "quantity": 1,
            "unit_price": recent_val, "line_value": recent_val, "customer_id": "MOM_CUST",
            "invoice_date": ref_date - pd.Timedelta(days=30), "country": "UK", "event_class": "VALID_PURCHASE"
        })

    valid_df = pd.DataFrame(rows)
    all_df = valid_df.copy()
    features = build_customer_features(all_df, valid_df, reference_date=ref_date)
    assert np.isclose(features.iloc[0]["value_change_pct"], expected_change, atol=1e-2)


# 3. RFM Scoring Quantile Range Tests (12 cases)
@pytest.mark.parametrize("n_customers,expected_min_score,expected_max_score", [
    (5, 3, 15),
    (10, 3, 15),
    (20, 3, 15),
    (50, 3, 15),
    (100, 3, 15),
    (500, 3, 15),
])
def test_parameterized_rfm_quintiles(n_customers, expected_min_score, expected_max_score):
    np.random.seed(42)
    df = pd.DataFrame({
        "customer_id": [f"CUST_{i}" for i in range(n_customers)],
        "recency_days": np.random.randint(1, 365, size=n_customers),
        "transaction_count": np.random.randint(1, 50, size=n_customers),
        "total_value": np.random.exponential(1000, size=n_customers) + 10
    })
    rfm = build_rfm_scores(df)

    assert rfm["rfm_recency_score"].min() >= 1
    assert rfm["rfm_recency_score"].max() <= 5
    assert rfm["rfm_frequency_score"].min() >= 1
    assert rfm["rfm_frequency_score"].max() <= 5
    assert rfm["rfm_monetary_score"].min() >= 1
    assert rfm["rfm_monetary_score"].max() <= 5
    assert rfm["rfm_total_score"].min() >= expected_min_score
    assert rfm["rfm_total_score"].max() <= expected_max_score
