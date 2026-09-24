"""Additional scenarios for RFM quintile cutoffs."""

import pandas as pd
import pytest

from src.config import path_config


# 20 Parameterized Scenarios for RFM Quintile Cutoffs & Bounds
@pytest.mark.parametrize("quintile_target,threshold_factor", [
    (1, 0.1), (1, 0.15), (1, 0.20),
    (2, 0.25), (2, 0.30), (2, 0.35),
    (3, 0.40), (3, 0.45), (3, 0.50),
    (4, 0.55), (4, 0.60), (4, 0.65),
    (5, 0.70), (5, 0.75), (5, 0.80),
    (5, 0.85), (5, 0.90), (5, 0.95),
    (5, 0.98), (5, 0.99),
])
def test_rfm_quantile_boundary_cutoffs(quintile_target, threshold_factor):
    df = pd.read_csv(path_config.exports_dir / "customer_summary.csv")
    q_val = df["total_value"].quantile(threshold_factor)
    assert q_val > 0, f"Quantile {threshold_factor} should be positive."
