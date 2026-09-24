"""Tests for RFM scoring quintiles and score properties."""

import pandas as pd

from src.features.rfm import build_rfm_scores


def test_rfm_scoring_distribution():
    # 10 synthetic customers with varying recency, frequency, and value
    test_data = pd.DataFrame({
        "customer_id": [f"C_{i}" for i in range(10)],
        "recency_days": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "transaction_count": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        "total_value": [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]
    })
    
    rfm_df = build_rfm_scores(test_data)
    
    assert set(rfm_df.columns).issuperset({
        "customer_id", "rfm_recency_score", "rfm_frequency_score", "rfm_monetary_score", "rfm_total_score", "rfm_composite_code"
    })
    
    # Check score bounds (1-5)
    for col in ["rfm_recency_score", "rfm_frequency_score", "rfm_monetary_score"]:
        assert rfm_df[col].min() >= 1
        assert rfm_df[col].max() <= 5

    # Customer C_0 has lowest recency (best), highest frequency, highest spend -> should have 5, 5, 5
    top_c = rfm_df[rfm_df["customer_id"] == "C_0"].iloc[0]
    assert top_c["rfm_recency_score"] == 5
    assert top_c["rfm_frequency_score"] == 5
    assert top_c["rfm_monetary_score"] == 5
    assert top_c["rfm_total_score"] == 15
    assert top_c["rfm_composite_code"] == "555"
