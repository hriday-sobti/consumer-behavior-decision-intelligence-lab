"""Tests for customer behavioral features, recency, momentum, and eligibility logic."""

import pandas as pd
import pytest

from src.features.build_features import build_customer_features, compute_reference_date


@pytest.fixture
def mock_transaction_pair():
    valid = pd.DataFrame([
        # Customer A: 3 orders, 100 days tenure -> Eligible
        {"invoice_no": "A1", "stock_code": "P1", "quantity": 10, "unit_price": 10.0, "line_value": 100.0, "customer_id": "CUST_A", "invoice_date": pd.Timestamp("2011-01-01 10:00:00"), "country": "UK"},
        {"invoice_no": "A2", "stock_code": "P2", "quantity": 5, "unit_price": 20.0, "line_value": 100.0, "customer_id": "CUST_A", "invoice_date": pd.Timestamp("2011-03-01 10:00:00"), "country": "UK"},
        {"invoice_no": "A3", "stock_code": "P3", "quantity": 2, "unit_price": 50.0, "line_value": 100.0, "customer_id": "CUST_A", "invoice_date": pd.Timestamp("2011-04-10 10:00:00"), "country": "UK"},
        # Customer B: 1 order, 10 days tenure -> Ineligible (insufficient_history = True)
        {"invoice_no": "B1", "stock_code": "P1", "quantity": 1, "unit_price": 50.0, "line_value": 50.0, "customer_id": "CUST_B", "invoice_date": pd.Timestamp("2011-04-05 10:00:00"), "country": "France"},
    ])
    valid["event_class"] = "VALID_PURCHASE"

    all_tx = valid.copy()
    return all_tx, valid

def test_reference_date_rule(mock_transaction_pair):
    _, valid = mock_transaction_pair
    ref_date = compute_reference_date(valid)
    # Max date is 2011-04-10 -> ref date should be 2011-04-11 normalized
    assert ref_date == pd.Timestamp("2011-04-11 00:00:00")

def test_customer_eligibility_and_metrics(mock_transaction_pair):
    all_tx, valid = mock_transaction_pair
    features = build_customer_features(all_tx, valid)

    cust_a = features[features["customer_id"] == "CUST_A"].iloc[0]
    cust_b = features[features["customer_id"] == "CUST_B"].iloc[0]

    assert cust_a["insufficient_history"] == False
    assert cust_b["insufficient_history"] == True

    # Order count
    assert cust_a["transaction_count"] == 3
    assert cust_b["transaction_count"] == 1

    # Total spend
    assert cust_a["total_value"] == 300.0
    assert cust_b["total_value"] == 50.0

    # Recency: 2011-04-11 - 2011-04-10 = 0 full days (or 0-1 day depending on hour)
    assert cust_a["recency_days"] == 0
