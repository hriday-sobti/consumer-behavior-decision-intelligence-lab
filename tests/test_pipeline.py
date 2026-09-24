"""End-to-end integration test verifying that all stages and artifacts exist and are non-empty."""

import pandas as pd

from src.config import path_config


def test_pipeline_reporting_exports_exist():
    required_exports = [
        "customer_summary.csv",
        "segment_summary.csv",
        "monthly_summary.csv",
        "state_transitions.csv",
        "decision_signals.csv",
        "data_controls.csv",
        "cohort_summary.csv",
        "country_summary.csv",
        "product_summary.csv"
    ]
    for exp in required_exports:
        p = path_config.exports_dir / exp
        assert p.exists(), f"Reporting export {exp} missing from {path_config.exports_dir}"
        df = pd.read_csv(p)
        assert len(df) > 0, f"Reporting export {exp} must be non-empty."

def test_automated_insights_generated():
    insights_csv = path_config.tables_dir / "automated_insights.csv"
    assert insights_csv.exists()
    df = pd.read_csv(insights_csv)
    assert len(df) >= 3, "Automated insight catalog must contain at least 3 verified observations."
