"""Temporal state transitions and migration matrix computation."""

import pandas as pd

from src.logging_config import logger


def build_state_transitions(snapshot_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Computes month-over-month customer state history and aggregated transition probability matrix.
    
    Generates:
      1. history_df: individual customer month-to-month state movement
      2. matrix_df: aggregated transition count and customer share
    """
    logger.info("Computing month-over-month customer behavioral state transitions...")
    # Sort by customer_id and year_month
    df = snapshot_df.sort_values(["customer_id", "year_month"]).copy()

    # Shift states within customer
    df["previous_month"] = df.groupby("customer_id")["year_month"].shift(1)
    df["previous_state"] = df.groupby("customer_id")["behavioral_state"].shift(1)

    # Filter to valid transition pairs
    transitions = df.dropna(subset=["previous_month", "previous_state"]).copy()
    transitions["current_month"] = transitions["year_month"]
    transitions["current_state"] = transitions["behavioral_state"]
    transitions["is_state_changed"] = transitions["previous_state"] != transitions["current_state"]

    history_df = transitions[[
        "customer_id",
        "previous_month",
        "current_month",
        "previous_state",
        "current_state",
        "is_state_changed"
    ]].reset_index(drop=True)

    # Aggregated Transition Matrix per month pair
    matrix_rows = []
    month_groups = history_df.groupby(["previous_month", "current_month"])

    for (p_m, c_m), grp in month_groups:
        len(grp)
        state_counts = grp.groupby(["previous_state", "current_state"]).size().reset_index(name="customer_count")
        
        # Calculate share from previous_state origin
        state_totals = grp.groupby("previous_state").size().to_dict()
        
        state_counts["previous_month"] = p_m
        state_counts["current_month"] = c_m
        totals_lookup = dict(state_totals)
        state_counts["customer_share"] = state_counts.apply(
            lambda r, st_map=totals_lookup: round(r["customer_count"] / st_map[r["previous_state"]], 4) if st_map.get(r["previous_state"], 0) > 0 else 0.0,
            axis=1
        )
        matrix_rows.append(state_counts)

    if matrix_rows:
        matrix_df = pd.concat(matrix_rows, ignore_index=True)
    else:
        matrix_df = pd.DataFrame(columns=["previous_month", "current_month", "previous_state", "current_state", "customer_count", "customer_share"])

    logger.info(f"Computed {len(history_df):,} individual transitions and {len(matrix_df):,} transition matrix aggregates.")
    return history_df, matrix_df
