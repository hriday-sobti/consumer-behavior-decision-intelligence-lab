"""Execute event classification, transaction cleaning, and staging exports."""

import pandas as pd

from src.cleaning.clean import classify_transaction_events, clean_transactions
from src.config import path_config
from src.ingestion.load_raw import load_raw_data
from src.logging_config import logger


def run_cleaning():
    logger.info("Executing transaction cleaning pipeline...")
    interim_raw = path_config.interim_data_dir / "raw_unified.parquet"
    if interim_raw.exists():
        logger.info(f"Loading raw unified data from interim cache: {interim_raw}")
        raw_df = pd.read_parquet(interim_raw)
    else:
        raw_df = load_raw_data()

    # Step 1: Event Classification
    classified_df = classify_transaction_events(raw_df)

    # Step 2: Cleaning & Deduplication
    clean_all_df, valid_purchases_df = clean_transactions(classified_df)

    # Step 3: Export processed datasets
    path_config.processed_data_dir.mkdir(parents=True, exist_ok=True)
    all_dest = path_config.processed_data_dir / "transactions_all_classified.parquet"
    valid_dest = path_config.processed_data_dir / "transactions_valid_purchases.parquet"

    clean_all_df.to_parquet(all_dest, index=False)
    valid_purchases_df.to_parquet(valid_dest, index=False)

    logger.info(f"Exported all classified transactions: {all_dest} ({len(clean_all_df):,} rows)")
    logger.info(f"Exported valid purchases transactions: {valid_dest} ({len(valid_purchases_df):,} rows)")

if __name__ == "__main__":
    run_cleaning()
