"""Unit tests for event classification, deduplication, and line value calculation."""

import pandas as pd
import pytest

from src.cleaning.clean import EventClass, classify_transaction_events, clean_transactions


@pytest.fixture
def sample_test_df():
    return pd.DataFrame([
        # Class 1: Cancellation (Invoice starts with C)
        {"invoice_no": "C1001", "stock_code": "SKU1", "description": "Item 1", "quantity": -5, "invoice_date": "2010-01-01 10:00:00", "unit_price": 10.0, "customer_id": 12345, "country": "UK"},
        # Class 2: Reversal (quantity < 0 but regular invoice)
        {"invoice_no": "1002", "stock_code": "SKU2", "description": "Item 2", "quantity": -2, "invoice_date": "2010-01-02 11:00:00", "unit_price": 5.0, "customer_id": 12345, "country": "UK"},
        # Class 3: Valid Purchase
        {"invoice_no": "1003", "stock_code": "SKU3", "description": "Item 3", "quantity": 10, "invoice_date": "2010-01-03 12:00:00", "unit_price": 2.5, "customer_id": 12345, "country": "UK"},
        # Class 4: Missing Customer ID
        {"invoice_no": "1004", "stock_code": "SKU4", "description": "Item 4", "quantity": 10, "invoice_date": "2010-01-04 13:00:00", "unit_price": 2.5, "customer_id": None, "country": "UK"},
        # Class 4: Zero Price
        {"invoice_no": "1005", "stock_code": "SKU5", "description": "Item 5", "quantity": 10, "invoice_date": "2010-01-05 14:00:00", "unit_price": 0.0, "customer_id": 12345, "country": "UK"},
        # Class 4: Negative Price (bad debt)
        {"invoice_no": "1006", "stock_code": "SKU6", "description": "Item 6", "quantity": 1, "invoice_date": "2010-01-06 15:00:00", "unit_price": -100.0, "customer_id": 12345, "country": "UK"},
        # Duplicate line of valid purchase
        {"invoice_no": "1003", "stock_code": "SKU3", "description": "Item 3", "quantity": 10, "invoice_date": "2010-01-03 12:00:00", "unit_price": 2.5, "customer_id": 12345, "country": "UK"}
    ])

def test_event_classification_precedence(sample_test_df):
    classified = classify_transaction_events(sample_test_df)
    
    # Verify line value calculation: Quantity * UnitPrice
    assert classified.loc[0, "line_value"] == -50.0
    assert classified.loc[2, "line_value"] == 25.0

    # Verify event classification assignment
    assert classified.loc[0, "event_class"] == EventClass.CANCELLATION.value
    assert classified.loc[1, "event_class"] == EventClass.REVERSAL_OR_RETURN.value
    assert classified.loc[2, "event_class"] == EventClass.VALID_PURCHASE.value
    assert classified.loc[3, "event_class"] == EventClass.INVALID_OR_UNUSABLE.value
    assert classified.loc[4, "event_class"] == EventClass.INVALID_OR_UNUSABLE.value
    assert classified.loc[5, "event_class"] == EventClass.INVALID_OR_UNUSABLE.value

def test_deduplication_removes_exact_duplicates(sample_test_df):
    classified = classify_transaction_events(sample_test_df)
    clean_all, valid_purchases = clean_transactions(classified)

    # Initial had 7 rows, 1 duplicate pair -> should result in 6 clean rows
    assert len(clean_all) == 6
    # Valid purchases had 2 rows with 1 duplicate -> 1 distinct valid row
    assert len(valid_purchases) == 1
    assert valid_purchases.iloc[0]["invoice_no"] == "1003"
