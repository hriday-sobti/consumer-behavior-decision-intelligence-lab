"""Monthly snapshots and state transitions pipeline runner."""

import pandas as pd

from src.config import path_config
from src.lifecycle.snapshots import build_monthly_snapshots
from src.lifecycle.transitions import build_state_transitions
from src.logging_config import logger


def run_snapshots_pipeline():
    logger.info("Executing monthly snapshots and lifecycle state pipeline...")
    valid_tx_path = path_config.processed_data_dir / "transactions_valid_purchases.parquet"
    valid_tx_df = pd.read_parquet(valid_tx_path)

    # 1. Build snapshots
    snapshot_df = build_monthly_snapshots(valid_tx_df)

    # 2. Build transitions
    history_df, matrix_df = build_state_transitions(snapshot_df)

    # 3. Export datasets
    snap_dest = path_config.processed_data_dir / "customer_monthly_snapshot.parquet"
    hist_dest = path_config.processed_data_dir / "customer_state_history.parquet"
    mat_dest = path_config.processed_data_dir / "state_transition_matrix.parquet"
    mat_csv = path_config.tables_dir / "state_transition_matrix.csv"

    snapshot_df.to_parquet(snap_dest, index=False)
    history_df.to_parquet(hist_dest, index=False)
    matrix_df.to_parquet(mat_dest, index=False)
    matrix_df.to_csv(mat_csv, index=False)

    logger.info(f"Monthly snapshots exported to: {snap_dest}")
    logger.info(f"State transition history exported to: {hist_dest}")
    logger.info(f"State transition matrix exported to: {mat_dest} and {mat_csv}")

if __name__ == "__main__":
    run_snapshots_pipeline()
