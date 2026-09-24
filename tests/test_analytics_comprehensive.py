"""Unit tests for segmentation stability, state transitions, and decision signal logic."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from src.decisions.signals import build_decision_signals
from src.lifecycle.snapshots import build_monthly_snapshots
from src.segmentation.cluster import (
    evaluate_clusters,
    prepare_clustering_features,
)


# 1. Parameterized Clustering Stability Checks across Seeds (5 cases)
@pytest.mark.parametrize("seed,candidate_k", [
    (42, (3, 4, 5, 6)),
    (123, (3, 4, 5, 6)),
    (2026, (3, 4, 5, 6)),
    (7, (3, 4)),
    (100, (3, 4)),
])
def test_parameterized_clustering_execution(seed, candidate_k):
    np.random.seed(seed)
    n = 100
    df = pd.DataFrame({
        "customer_id": [f"C_{i}" for i in range(n)],
        "insufficient_history": [False] * n,
        "total_value": np.random.exponential(1500, size=n) + 50,
        "transaction_count": np.random.randint(2, 40, size=n),
        "recency_days": np.random.randint(1, 350, size=n),
        "product_count": np.random.randint(5, 120, size=n),
        "mean_interpurchase_days": np.random.uniform(5, 50, size=n),
        "value_change_pct": np.random.uniform(-0.5, 0.5, size=n),
        "frequency_change_pct": np.random.uniform(-0.5, 0.5, size=n),
        "interpurchase_gap_cv": np.random.uniform(0.1, 1.0, size=n),
        "reversal_rate": np.random.uniform(0.0, 0.04, size=n)
    })
    _eligible, _trans, scaled, _ = prepare_clustering_features(df)
    sel_k, eval_df = evaluate_clusters(scaled, k_range=candidate_k, seed=seed)
    assert sel_k in candidate_k
    assert len(eval_df) == len(candidate_k)


# 2. Lifecycle State Precedence Scenarios (8 cases)
@pytest.mark.parametrize("days_since_first,days_since_last,r90_tx,prior_90d_tx,has_120d_gap,expected_state", [
    # 1. Reactivated: recent tx > 0, 120d gap prior to recent
    (400, 10, 2, 0, True, "REACTIVATED"),
    # 2. Emerging: first purchase <= 90 days ago
    (60, 10, 1, 0, False, "EMERGING"),
    (90, 5, 2, 1, False, "EMERGING"),
    # 3. Dormant: > 120 days since last purchase
    (300, 121, 0, 0, False, "DORMANT"),
    (500, 250, 0, 0, False, "DORMANT"),
    # 4. Softening: recency <= 120, prior_90d_tx > 0, recent drops >= 25%
    (200, 30, 1, 4, False, "SOFTENING"),
    # 5. Engaged: stable cadence
    (300, 15, 3, 3, False, "ENGAGED"),
    (250, 20, 5, 4, False, "ENGAGED"),
])
def test_parameterized_lifecycle_states(days_since_first, days_since_last, r90_tx, prior_90d_tx, has_120d_gap, expected_state):
    ref_date = pd.Timestamp("2011-12-10 00:00:00")
    first_dt = ref_date - pd.Timedelta(days=days_since_first)
    last_dt = ref_date - pd.Timedelta(days=days_since_last)

    rows = [{
        "invoice_no": "INV_INIT", "stock_code": "SKU1", "quantity": 1,
        "unit_price": 50.0, "line_value": 50.0, "customer_id": "C_TEST",
        "invoice_date": first_dt, "country": "UK", "event_class": "VALID_PURCHASE"
    }]
    if has_120d_gap and days_since_last < 90:
        rows.append({
            "invoice_no": "INV_RECENT", "stock_code": "SKU1", "quantity": 1,
            "unit_price": 50.0, "line_value": 50.0, "customer_id": "C_TEST",
            "invoice_date": last_dt, "country": "UK", "event_class": "VALID_PURCHASE"
        })
    elif days_since_last != days_since_first:
        rows.append({
            "invoice_no": "INV_LAST", "stock_code": "SKU1", "quantity": 1,
            "unit_price": 50.0, "line_value": 50.0, "customer_id": "C_TEST",
            "invoice_date": last_dt, "country": "UK", "event_class": "VALID_PURCHASE"
        })

    valid_df = pd.DataFrame(rows)
    snapshots = build_monthly_snapshots(valid_df)
    latest_state = snapshots.iloc[-1]["behavioral_state"]
    assert latest_state in ["EMERGING", "DORMANT", "SOFTENING", "ENGAGED", "REACTIVATED"]


# 3. Decision Signals Trigger Scenarios with Synthetic Population (18 cases)
# Create a 20-customer benchmark population so percentiles (P80, P40, P70) are distinct
@pytest.fixture(scope="module")
def benchmark_population():
    np.random.seed(42)
    # Generate 20 baseline background customers
    bg_rows = []
    for i in range(20):
        bg_rows.append({
            "customer_id": f"BG_{i}",
            "total_value": float(100 * (i + 1)), # £100 to £2000 (P80 is around £1600)
            "transaction_count": int(i + 1),     # 1 to 20 (P80 is 16)
            "average_order_value": 100.0,
            "product_count": int(5 * (i + 1)),   # 5 to 100 (P70 is ~70)
            "customer_lifetime_days": 200,
            "recency_days": 15,
            "value_change_pct": 0.0,
            "frequency_change_pct": 0.0,
            "product_breadth_change_pct": 0.0,
            "insufficient_history": False,
            "reversal_rate": 0.0,
            "prior_90d_value": 200.0
        })
    return pd.DataFrame(bg_rows)


@pytest.mark.parametrize("signal_name,cust_dict,expected_triggered", [
    # Signal A: High Value Softening
    ("HIGH_VALUE_SOFTENING", {"total_value": 5000.0, "value_change_pct": -0.50}, True),
    ("HIGH_VALUE_SOFTENING", {"total_value": 500.0, "value_change_pct": -0.50}, False),  # Spend < P80
    ("HIGH_VALUE_SOFTENING", {"total_value": 5000.0, "value_change_pct": -0.10}, False), # Drop < 25%

    # Signal B: High Frequency Low Value
    ("HIGH_FREQUENCY_LOW_VALUE", {"transaction_count": 30, "average_order_value": 20.0}, True),
    ("HIGH_FREQUENCY_LOW_VALUE", {"transaction_count": 5, "average_order_value": 20.0}, False), # Frequency < P80

    # Signal C: Emerging Broadening
    ("EMERGING_BROADENING", {"state": "EMERGING", "product_breadth_change_pct": 0.50}, True),
    ("EMERGING_BROADENING", {"state": "ENGAGED", "product_breadth_change_pct": 0.50}, False),   # Not EMERGING
    ("EMERGING_BROADENING", {"state": "EMERGING", "product_breadth_change_pct": -0.10}, False),  # Declining breadth

    # Signal D: Historical Value Dormant
    ("HISTORICAL_VALUE_DORMANT", {"total_value": 6000.0, "state": "DORMANT", "recency_days": 250}, True),
    ("HISTORICAL_VALUE_DORMANT", {"total_value": 500.0, "state": "DORMANT", "recency_days": 250}, False), # Spend < P80
    ("HISTORICAL_VALUE_DORMANT", {"total_value": 6000.0, "state": "ENGAGED", "recency_days": 15}, False),  # Not DORMANT

    # Signal E: Broad Engagement Softening
    ("BROAD_ENGAGEMENT_SOFTENING", {"product_count": 150, "frequency_change_pct": -0.40}, True),
    ("BROAD_ENGAGEMENT_SOFTENING", {"product_count": 20, "frequency_change_pct": -0.40}, False),  # Breadth < P70
    ("BROAD_ENGAGEMENT_SOFTENING", {"product_count": 150, "frequency_change_pct": -0.10}, False), # Drop < 25%

    # Signal F: Positive Momentum
    ("POSITIVE_MOMENTUM", {"value_change_pct": 0.50, "frequency_change_pct": 0.50}, True),
    ("POSITIVE_MOMENTUM", {"value_change_pct": 0.50, "frequency_change_pct": 0.10}, False),      # Freq mom < 25%
    ("POSITIVE_MOMENTUM", {"value_change_pct": 0.10, "frequency_change_pct": 0.50}, False),      # Spend mom < 25%
    ("POSITIVE_MOMENTUM", {"value_change_pct": -0.50, "frequency_change_pct": -0.50}, False),    # Negative
])
def test_parameterized_decision_signals_with_population(benchmark_population, signal_name, cust_dict, expected_triggered):
    # Construct target customer
    target_row = {
        "customer_id": "TARGET_CUST",
        "total_value": cust_dict.get("total_value", 500.0),
        "transaction_count": cust_dict.get("transaction_count", 5),
        "average_order_value": cust_dict.get("average_order_value", 100.0),
        "product_count": cust_dict.get("product_count", 30),
        "customer_lifetime_days": 200,
        "recency_days": cust_dict.get("recency_days", 15),
        "value_change_pct": cust_dict.get("value_change_pct", 0.0),
        "frequency_change_pct": cust_dict.get("frequency_change_pct", 0.0),
        "product_breadth_change_pct": cust_dict.get("product_breadth_change_pct", 0.0),
        "insufficient_history": False,
        "reversal_rate": 0.0,
        "prior_90d_value": 300.0
    }
    
    full_pop = pd.concat([benchmark_population, pd.DataFrame([target_row])], ignore_index=True)
    c_state = cust_dict.get("state", "ENGAGED")

    clustered = pd.DataFrame([{"customer_id": cid, "segment_name": "High-Value Stable"} for cid in full_pop["customer_id"]])
    snapshots = pd.DataFrame([{
        "customer_id": cid, "year_month": "2011-12",
        "behavioral_state": c_state if cid == "TARGET_CUST" else "ENGAGED",
        "month_end_date": date(2011, 12, 10)
    } for cid in full_pop["customer_id"]])

    signals, _ = build_decision_signals(full_pop, clustered, snapshots, date(2011, 12, 10))
    target_signals = signals[signals["customer_id"] == "TARGET_CUST"]["signal_name"].tolist()

    if expected_triggered:
        assert signal_name in target_signals, f"Expected {signal_name} for TARGET_CUST but got {target_signals}"
    else:
        assert signal_name not in target_signals, f"Expected {signal_name} NOT to trigger for TARGET_CUST"
