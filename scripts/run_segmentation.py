"""Behavioral segmentation execution script."""

import pandas as pd

from src.config import analytical_config, path_config
from src.logging_config import logger
from src.segmentation.cluster import (
    evaluate_clusters,
    fit_behavioral_segments,
    prepare_clustering_features,
)


def run_segmentation():
    logger.info("Executing behavioral clustering pipeline...")
    feat_path = path_config.processed_data_dir / "customer_behavior_features.parquet"
    features_df = pd.read_parquet(feat_path)

    # Prepare features
    eligible_df, trans_df, scaled_df, _scaler = prepare_clustering_features(features_df)

    # Evaluate K candidates
    selected_k, eval_df = evaluate_clusters(scaled_df, analytical_config.clustering_k_candidates, seed=analytical_config.random_seed)

    # Save evaluation table
    eval_csv = path_config.tables_dir / "cluster_evaluation.csv"
    eval_df.to_csv(eval_csv, index=False)
    logger.info(f"Saved cluster evaluation results to: {eval_csv}")

    # Fit final model and profile
    clustered_df, profile_df = fit_behavioral_segments(
        eligible_df, trans_df, scaled_df, selected_k, seed=analytical_config.random_seed
    )

    # Export segment tables
    clustered_dest = path_config.processed_data_dir / "customer_segment.parquet"
    profile_dest = path_config.processed_data_dir / "segment_profile.parquet"
    profile_csv = path_config.tables_dir / "segment_profiles.csv"

    clustered_df.to_parquet(clustered_dest, index=False)
    profile_df.to_parquet(profile_dest, index=False)
    profile_df.to_csv(profile_csv, index=False)

    logger.info(f"Clustered customer assignments saved to: {clustered_dest}")
    logger.info(f"Segment behavioral profiles saved to: {profile_dest} and {profile_csv}")

if __name__ == "__main__":
    run_segmentation()
