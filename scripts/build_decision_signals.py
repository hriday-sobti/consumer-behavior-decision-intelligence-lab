"""Decision signals pipeline execution script."""

import pandas as pd

from src.config import path_config
from src.decisions.signals import build_decision_signals
from src.logging_config import logger


def run_decision_signals():
    logger.info("Executing decision signals and strategy catalog pipeline...")
    feat_path = path_config.processed_data_dir / "customer_behavior_features.parquet"
    seg_path = path_config.processed_data_dir / "customer_segment.parquet"
    snap_path = path_config.processed_data_dir / "customer_monthly_snapshot.parquet"

    features_df = pd.read_parquet(feat_path)
    clustered_df = pd.read_parquet(seg_path)
    snapshots_df = pd.read_parquet(snap_path)

    # Reference date from last snapshot month end
    ref_date = snapshots_df["month_end_date"].max()

    signals_df, strategies_df = build_decision_signals(
        features_df, clustered_df, snapshots_df, ref_date
    )

    # Export
    signals_dest = path_config.processed_data_dir / "customer_decision_signal.parquet"
    strat_dest = path_config.processed_data_dir / "decision_strategy.parquet"
    signals_csv = path_config.tables_dir / "customer_decision_signals.csv"
    strat_csv = path_config.tables_dir / "decision_strategies.csv"

    signals_df.to_parquet(signals_dest, index=False)
    strategies_df.to_parquet(strat_dest, index=False)
    signals_df.to_csv(signals_csv, index=False)
    strategies_df.to_csv(strat_csv, index=False)

    logger.info(f"Decision signals exported to: {signals_dest} and {signals_csv}")
    logger.info(f"Decision strategies catalog exported to: {strat_dest} and {strat_csv}")

if __name__ == "__main__":
    run_decision_signals()
