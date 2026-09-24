"""RFM Quintile Scoring module.

Computes standard recency, frequency, and monetary quintile scores (1-5):
- Recency: lower days = higher score (5 = most recent)
- Frequency: higher count = higher score (5 = most frequent)
- Monetary: higher value = higher score (5 = highest spending)
Handles ties with rank(method='first' or 'average') to ensure robust binning.
"""

import pandas as pd

from src.logging_config import logger


def build_rfm_scores(features_df: pd.DataFrame) -> pd.DataFrame:
    """Computes transparent RFM quintiles and composite scores for all customers."""
    logger.info("Computing supporting RFM quintile scores...")
    df = features_df[["customer_id", "recency_days", "transaction_count", "total_value"]].copy()

    # Recency: Lower recency_days is better -> inverted quintiles (5 = lowest days)
    # Using pd.qcut with rank to avoid identical boundary errors on ties
    r_ranks = df["recency_days"].rank(method="first", ascending=True)
    df["rfm_recency_score"] = pd.qcut(r_ranks, q=5, labels=[5, 4, 3, 2, 1]).astype(int)

    # Frequency: Higher transaction_count is better (5 = highest)
    f_ranks = df["transaction_count"].rank(method="first", ascending=True)
    df["rfm_frequency_score"] = pd.qcut(f_ranks, q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Monetary: Higher total_value is better (5 = highest)
    m_ranks = df["total_value"].rank(method="first", ascending=True)
    df["rfm_monetary_score"] = pd.qcut(m_ranks, q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    df["rfm_total_score"] = df["rfm_recency_score"] + df["rfm_frequency_score"] + df["rfm_monetary_score"]
    df["rfm_composite_code"] = (
        df["rfm_recency_score"].astype(str) + 
        df["rfm_frequency_score"].astype(str) + 
        df["rfm_monetary_score"].astype(str)
    )

    logger.info(f"RFM scores calculated for {len(df):,} customers. Mean total score: {df['rfm_total_score'].mean():.2f}")
    return df
