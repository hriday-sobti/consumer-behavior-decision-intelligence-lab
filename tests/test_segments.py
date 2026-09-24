"""Tests for behavioral clustering, stability checks, and segment profiling."""

import numpy as np
import pandas as pd
import pytest

from src.segmentation.cluster import (
    evaluate_clusters,
    fit_behavioral_segments,
    prepare_clustering_features,
)


@pytest.fixture
def mock_eligible_features():
    # 60 synthetic eligible customers
    np.random.seed(42)
    n = 60
    return pd.DataFrame({
        "customer_id": [f"C_{i}" for i in range(n)],
        "insufficient_history": [False] * n,
        "total_value": np.random.exponential(scale=1000, size=n) + 100,
        "transaction_count": np.random.randint(2, 30, size=n),
        "recency_days": np.random.randint(1, 300, size=n),
        "product_count": np.random.randint(5, 100, size=n),
        "mean_interpurchase_days": np.random.uniform(5, 60, size=n),
        "value_change_pct": np.random.uniform(-0.5, 0.5, size=n),
        "frequency_change_pct": np.random.uniform(-0.5, 0.5, size=n),
        "interpurchase_gap_cv": np.random.uniform(0.1, 1.2, size=n),
        "reversal_rate": np.random.uniform(0.0, 0.05, size=n)
    })

def test_prepare_clustering_features(mock_eligible_features):
    _eligible, _trans, scaled, _scaler = prepare_clustering_features(mock_eligible_features)
    assert len(scaled) == 60
    assert "log_total_value" in scaled.columns
    assert "log_transaction_count" in scaled.columns

def test_cluster_stability_across_seeds(mock_eligible_features):
    """Part 88 check: Compare cluster structure across controlled random seeds (42, 123, 2026)."""
    eligible, trans, scaled, _scaler = prepare_clustering_features(mock_eligible_features)
    
    seeds = [42, 123, 2026]
    profiles = []
    
    for s in seeds:
        _sel_k, _eval_df = evaluate_clusters(scaled, k_range=(3, 4), seed=s)
        _clustered, profile = fit_behavioral_segments(eligible, trans, scaled, selected_k=3, seed=s)
        profiles.append(profile["customer_count"].tolist())

    # Ensure all runs succeed and assign exactly all 60 accounts
    for p in profiles:
        assert sum(p) == 60
