"""Tests for behavioral lifecycle state transitions and temporal consistency."""

import pandas as pd

from src.lifecycle.snapshots import build_monthly_snapshots
from src.lifecycle.transitions import build_state_transitions


def test_monthly_snapshot_state_precedence():
    # Synthetic transaction series
    data = pd.DataFrame([
        # Cust 1 transacts in Dec 2009, then nothing until Oct 2011 (>120d gap, reactivated)
        {"invoice_no": "INV1", "stock_code": "SKU1", "quantity": 10, "unit_price": 5.0, "line_value": 50.0, "customer_id": "CUST_1", "invoice_date": pd.Timestamp("2009-12-15"), "country": "UK"},
        {"invoice_no": "INV2", "stock_code": "SKU1", "quantity": 10, "unit_price": 5.0, "line_value": 50.0, "customer_id": "CUST_1", "invoice_date": pd.Timestamp("2011-10-15"), "country": "UK"},
    ])
    data["event_class"] = "VALID_PURCHASE"

    snapshots = build_monthly_snapshots(data)
    assert len(snapshots) > 0
    assert "behavioral_state" in snapshots.columns
    
    # State transition builder
    history, _matrix = build_state_transitions(snapshots)
    assert len(history) > 0
    assert "is_state_changed" in history.columns
