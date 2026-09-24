"""Unit tests for event classification rules, deduplication, and line values."""

import numpy as np
import pandas as pd
import pytest

from src.cleaning.clean import EventClass, classify_transaction_events, clean_transactions


# 1. Parameterized Event Classification Scenarios (20 cases)
@pytest.mark.parametrize("inv,stock,desc,q,price,cid,date,expected_class", [
    # Explicit cancellations
    ("C10001", "85048", "Standard Item", -10, 5.0, "12345", "2010-01-01 10:00:00", EventClass.CANCELLATION.value),
    ("c10002", "85048", "Standard Item", -1, 2.5, "12345", "2010-01-01 10:00:00", EventClass.CANCELLATION.value),
    (" C10003 ", "85048", "Whitespace Invoice", -5, 10.0, "12345", "2010-01-01 10:00:00", EventClass.CANCELLATION.value),
    ("C489434", "POST", "Postage Cancellation", -1, 18.0, "13085", "2009-12-01 07:45:00", EventClass.CANCELLATION.value),
    ("c99999", "D", "Discount Cancellation", -1, 50.0, "15000", "2011-05-01 12:00:00", EventClass.CANCELLATION.value),
    # Reversals / returns (negative quantity, positive price, no 'C' prefix)
    ("10001", "85048", "Return Line", -5, 10.0, "12345", "2010-01-01 10:00:00", EventClass.REVERSAL_OR_RETURN.value),
    ("20002", "79323P", "Damaged goods", -100, 1.25, "16000", "2010-02-01 11:00:00", EventClass.REVERSAL_OR_RETURN.value),
    ("30003", "M", "Manual Return", -2, 25.0, "17000", "2010-03-01 12:00:00", EventClass.REVERSAL_OR_RETURN.value),
    ("40004", "22492", "Return Box", -12, 0.65, "18000", "2011-04-01 14:00:00", EventClass.REVERSAL_OR_RETURN.value),
    # Valid Purchases
    ("50001", "85048", "Valid Item 1", 1, 10.0, "12345", "2010-01-01 10:00:00", EventClass.VALID_PURCHASE.value),
    ("50002", "79323W", "Valid Item 2", 48, 6.75, "13078", "2009-12-01 07:46:00", EventClass.VALID_PURCHASE.value),
    ("50003", "POST", "Valid Postage", 1, 18.0, "15362", "2009-12-01 09:06:00", EventClass.VALID_PURCHASE.value),
    ("50004", "22041", "Large Order", 1200, 2.10, "14000", "2011-06-01 15:00:00", EventClass.VALID_PURCHASE.value),
    ("50005", "21232", "Penny Item", 10, 0.01, "12500", "2011-07-01 16:00:00", EventClass.VALID_PURCHASE.value),
    # Invalid / Unusable: Missing Customer ID
    ("60001", "85048", "Guest Checkout", 5, 10.0, None, "2010-01-01 10:00:00", EventClass.INVALID_OR_UNUSABLE.value),
    ("60002", "85048", "NaN Customer", 5, 10.0, np.nan, "2010-01-01 10:00:00", EventClass.INVALID_OR_UNUSABLE.value),
    ("60003", "85048", "Blank Customer", 5, 10.0, "", "2010-01-01 10:00:00", EventClass.INVALID_OR_UNUSABLE.value),
    ("60004", "85048", "Zero Customer", 5, 10.0, 0, "2010-01-01 10:00:00", EventClass.INVALID_OR_UNUSABLE.value),
    # Invalid / Unusable: Corrupt Price
    ("70001", "85048", "Free Sample", 10, 0.0, "12345", "2010-01-01 10:00:00", EventClass.INVALID_OR_UNUSABLE.value),
    ("70002", "ADJUST", "Bad Debt Adj", 1, -53594.36, "12345", "2010-01-01 10:00:00", EventClass.INVALID_OR_UNUSABLE.value),
])
def test_parameterized_event_classification(inv, stock, desc, q, price, cid, date, expected_class):
    df = pd.DataFrame([{
        "invoice_no": inv, "stock_code": stock, "description": desc,
        "quantity": q, "unit_price": price, "customer_id": cid,
        "invoice_date": date, "country": "United Kingdom"
    }])
    classified = classify_transaction_events(df)
    assert classified.iloc[0]["event_class"] == expected_class


# 2. Line Value Precision Tests (8 cases)
@pytest.mark.parametrize("quantity,unit_price,expected_line_value", [
    (1, 1.0, 1.0),
    (10, 2.55, 25.50),
    (100, 0.01, 1.00),
    (3, 4.15, 12.45),
    (120, 15.0, 1800.0),
    (-5, 10.0, -50.0),
    (-100, 2.5, -250.0),
    (80995, 2.08, 168469.60),
])
def test_parameterized_line_value_calculation(quantity, unit_price, expected_line_value):
    df = pd.DataFrame([{
        "invoice_no": "1001", "stock_code": "SKU1", "description": "Test",
        "quantity": quantity, "unit_price": unit_price, "customer_id": "12345",
        "invoice_date": "2010-01-01 10:00:00", "country": "UK"
    }])
    classified = classify_transaction_events(df)
    assert np.isclose(classified.iloc[0]["line_value"], expected_line_value, atol=1e-2)


# 3. Deduplication Granular Cases (7 cases)
@pytest.mark.parametrize("dup_count,is_valid", [
    (1, True),   # Single record
    (2, True),   # 1 duplicate pair
    (3, True),   # Triplicate
    (5, True),   # 5 duplicates
    (1, False),  # Single invalid
    (2, False),  # 2 duplicate invalid records
    (4, False),  # 4 duplicate invalid records
])
def test_parameterized_deduplication(dup_count, is_valid):
    row = {
        "invoice_no": "INV123", "stock_code": "SKU_A", "description": "Desc A",
        "quantity": 10 if is_valid else 0,
        "unit_price": 2.50,
        "customer_id": "12345" if is_valid else None,
        "invoice_date": "2010-05-01 10:00:00",
        "country": "UK"
    }
    df = pd.DataFrame([row] * dup_count)
    classified = classify_transaction_events(df)
    clean_all, valid_purchases = clean_transactions(classified)

    # After dedup, exactly 1 row should remain in clean_all
    assert len(clean_all) == 1
    if is_valid:
        assert len(valid_purchases) == 1
    else:
        assert len(valid_purchases) == 0
