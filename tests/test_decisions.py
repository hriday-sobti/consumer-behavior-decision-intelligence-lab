"""Tests for decision signals, severity thresholds, and strategy registry."""

from datetime import date

import pandas as pd

from src.decisions.signals import build_decision_signals


def test_decision_signals_trigger_correctly():
    # Synthetic customers
    features = pd.DataFrame([
        # High value softening: spend=10000 (>= P80), val_change = -0.50 (<= -25%)
        {
            "customer_id": "C_HIGH_SOFT", "total_value": 10000.0, "transaction_count": 10,
            "average_order_value": 1000.0, "product_count": 50, "customer_lifetime_days": 300,
            "recency_days": 10, "value_change_pct": -0.50, "frequency_change_pct": -0.40,
            "product_breadth_change_pct": -0.20, "insufficient_history": False,
            "reversal_rate": 0.0, "prior_90d_value": 5000.0
        },
        # High frequency low value: frequency=50 (>= P80), aov = 20.0 (<= P40)
        {
            "customer_id": "C_FREQ_LOW_VAL", "total_value": 1000.0, "transaction_count": 50,
            "average_order_value": 20.0, "product_count": 30, "customer_lifetime_days": 200,
            "recency_days": 5, "value_change_pct": 0.05, "frequency_change_pct": 0.05,
            "product_breadth_change_pct": 0.0, "insufficient_history": False,
            "reversal_rate": 0.0, "prior_90d_value": 500.0
        },
        # Control customer with normal values
        {
            "customer_id": "C_NORMAL", "total_value": 500.0, "transaction_count": 3,
            "average_order_value": 166.0, "product_count": 10, "customer_lifetime_days": 150,
            "recency_days": 20, "value_change_pct": 0.0, "frequency_change_pct": 0.0,
            "product_breadth_change_pct": 0.0, "insufficient_history": False,
            "reversal_rate": 0.0, "prior_90d_value": 250.0
        }
    ])

    clustered = pd.DataFrame([
        {"customer_id": "C_HIGH_SOFT", "segment_name": "High-Value Stable"},
        {"customer_id": "C_FREQ_LOW_VAL", "segment_name": "Frequent Narrow-Basket"},
        {"customer_id": "C_NORMAL", "segment_name": "Moderate-Value Regular"}
    ])

    snapshots = pd.DataFrame([
        {"customer_id": "C_HIGH_SOFT", "year_month": "2011-12", "behavioral_state": "ENGAGED", "month_end_date": date(2011, 12, 10)},
        {"customer_id": "C_FREQ_LOW_VAL", "year_month": "2011-12", "behavioral_state": "ENGAGED", "month_end_date": date(2011, 12, 10)},
        {"customer_id": "C_NORMAL", "year_month": "2011-12", "behavioral_state": "ENGAGED", "month_end_date": date(2011, 12, 10)}
    ])

    signals, strategies = build_decision_signals(features, clustered, snapshots, date(2011, 12, 10))

    # C_HIGH_SOFT should trigger HIGH_VALUE_SOFTENING
    c_soft_sigs = signals[signals["customer_id"] == "C_HIGH_SOFT"]["signal_name"].tolist()
    assert "HIGH_VALUE_SOFTENING" in c_soft_sigs
    
    # C_FREQ_LOW_VAL should trigger HIGH_FREQUENCY_LOW_VALUE
    c_freq_sigs = signals[signals["customer_id"] == "C_FREQ_LOW_VAL"]["signal_name"].tolist()
    assert "HIGH_FREQUENCY_LOW_VALUE" in c_freq_sigs

    # Strategies must cover all 6 locked strategies
    assert len(strategies) == 6
    assert "STRAT-01" in strategies["strategy_id"].values
