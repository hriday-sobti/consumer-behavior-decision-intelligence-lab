"""Feature engineering and RFM pipeline runner."""

import pandas as pd

from src.config import path_config
from src.features.build_features import build_customer_features
from src.features.rfm import build_rfm_scores
from src.logging_config import logger


def run_feature_engineering():
    logger.info("Executing customer feature engineering and RFM scoring pipeline...")
    all_tx_path = path_config.processed_data_dir / "transactions_all_classified.parquet"
    valid_tx_path = path_config.processed_data_dir / "transactions_valid_purchases.parquet"

    all_tx_df = pd.read_parquet(all_tx_path)
    valid_tx_df = pd.read_parquet(valid_tx_path)

    features_df = build_customer_features(all_tx_df, valid_tx_df)
    rfm_df = build_rfm_scores(features_df)

    feat_dest = path_config.processed_data_dir / "customer_behavior_features.parquet"
    rfm_dest = path_config.processed_data_dir / "customer_rfm.parquet"

    features_df.to_parquet(feat_dest, index=False)
    rfm_df.to_parquet(rfm_dest, index=False)

    logger.info(f"Customer behavior features exported to: {feat_dest}")
    logger.info(f"Customer RFM scores exported to: {rfm_dest}")

if __name__ == "__main__":
    run_feature_engineering()
