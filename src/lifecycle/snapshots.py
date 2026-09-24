"""Monthly customer snapshots and behavioral lifecycle state assignments - Vectorized implementation."""


import numpy as np
import pandas as pd

from src.logging_config import logger


def build_monthly_snapshots(valid_purchases_df: pd.DataFrame) -> pd.DataFrame:
    """Builds complete monthly customer snapshots across the 24-month longitudinal observation period using vectorized aggregations."""
    logger.info("Generating longitudinal monthly customer snapshots (vectorized)...")
    df = valid_purchases_df.copy()
    df["order_date"] = pd.to_datetime(df["invoice_date"])
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)

    # 1. Order-level aggregation
    orders_df = df.groupby(["customer_id", "invoice_no"]).agg(
        order_date=("order_date", "min"),
        order_value=("line_value", "sum"),
        order_items=("quantity", "sum"),
        order_skus=("stock_code", "nunique"),
        year_month=("year_month", "first")
    ).reset_index()

    # Distinct calendar months
    all_months = sorted(orders_df["year_month"].unique())
    logger.info(f"Aggregating monthly activity across {len(all_months)} distinct months ({all_months[0]} to {all_months[-1]})...")

    # In-month aggregations
    cust_month_orders = orders_df.groupby(["customer_id", "year_month"]).agg(
        transaction_count=("invoice_no", "count"),
        value=("order_value", "sum"),
        items=("order_items", "sum")
    ).reset_index()

    cust_month_skus = df.groupby(["customer_id", "year_month"])["stock_code"].nunique().reset_index(name="product_count")
    cust_month_activity = cust_month_orders.merge(cust_month_skus, on=["customer_id", "year_month"], how="left")

    # Customer acquisition month and first/last dates
    cust_first_date = orders_df.groupby("customer_id")["order_date"].min().to_dict()
    cust_first_month = {cid: str(dt.to_period("M")) for cid, dt in cust_first_date.items()}

    # Create dense grid only from customer acquisition month through last month
    grid_rows = []
    month_periods = {ym: pd.Period(ym, freq="M") for ym in all_months}
    month_ends = {ym: p.end_time for ym, p in month_periods.items()}
    month_starts = {ym: p.start_time for ym, p in month_periods.items()}

    logger.info("Building dense customer-month observation grid...")
    for cid, f_ym in cust_first_month.items():
        # Slices of months where customer exists in universe
        c_months = [m for m in all_months if m >= f_ym]
        for m in c_months:
            grid_rows.append({"customer_id": cid, "year_month": m})

    grid_df = pd.DataFrame(grid_rows)
    logger.info(f"Dense grid created with {len(grid_df):,} customer-months. Merging actual activity...")

    # Merge activity onto grid
    merged = grid_df.merge(cust_month_activity, on=["customer_id", "year_month"], how="left")
    merged["transaction_count"] = merged["transaction_count"].fillna(0).astype(int)
    merged["value"] = merged["value"].fillna(0.0).round(4)
    merged["items"] = merged["items"].fillna(0).astype(int)
    merged["product_count"] = merged["product_count"].fillna(0).astype(int)
    merged["active_flag"] = merged["transaction_count"] > 0

    # Add date boundaries
    merged["month_start_date"] = merged["year_month"].map(lambda ym: month_starts[ym].date())
    merged["month_end_date"] = merged["year_month"].map(lambda ym: month_ends[ym].date())
    merged["month_end_dt"] = merged["year_month"].map(lambda ym: month_ends[ym])

    # Sort deterministically
    merged = merged.sort_values(["customer_id", "year_month"]).reset_index(drop=True)

    # Calculate rolling 3-month (approx 90d) metrics using grouped rolling
    logger.info("Computing rolling 90-day window aggregations...")
    # Grouped rolling over 3 monthly periods (current month + prior 2 months)
    # Set customer_id as index for grouped operations
    merged["rolling_90d_transactions"] = (
        merged.groupby("customer_id")["transaction_count"]
        .rolling(window=3, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
        .astype(int)
    )

    merged["rolling_90d_value"] = (
        merged.groupby("customer_id")["value"]
        .rolling(window=3, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
        .round(4)
    )

    merged["rolling_90d_products"] = (
        merged.groupby("customer_id")["product_count"]
        .rolling(window=3, min_periods=1)
        .max()
        .reset_index(level=0, drop=True)
        .astype(int)
    )

    # Prior 90-day rolling transactions (lag 3 months of rolling 3-month sum)
    # Or shift(3) of rolling sum
    merged["prior_90d_transactions"] = (
        merged.groupby("customer_id")["rolling_90d_transactions"]
        .shift(3)
        .fillna(0)
        .astype(int)
    )

    # Calculate recency at month end
    logger.info("Calculating elapsed recency at each month end...")
    # Track the latest active month for each customer
    merged["active_month_dt"] = merged["month_end_dt"].where(merged["active_flag"])
    merged["last_active_dt"] = merged.groupby("customer_id")["active_month_dt"].ffill()
    
    # Days between month_end_dt and last_active_dt
    merged["recency_at_month_end"] = (merged["month_end_dt"] - merged["last_active_dt"]).dt.days.fillna(0).astype(int)

    # Days since customer first purchase
    cust_first_dt_series = merged["customer_id"].map(cust_first_date)
    merged["days_since_first"] = (merged["month_end_dt"] - cust_first_dt_series).dt.days

    # 4-month rolling activity check for reactivation (120 days = 4 months)
    # Check if customer transacted in months t-4 to t-1
    merged["lag_1_tx"] = merged.groupby("customer_id")["transaction_count"].shift(1).fillna(0)
    merged["lag_2_tx"] = merged.groupby("customer_id")["transaction_count"].shift(2).fillna(0)
    merged["lag_3_tx"] = merged.groupby("customer_id")["transaction_count"].shift(3).fillna(0)
    merged["lag_4_tx"] = merged.groupby("customer_id")["transaction_count"].shift(4).fillna(0)
    merged["prior_120d_tx"] = merged["lag_1_tx"] + merged["lag_2_tx"] + merged["lag_3_tx"] + merged["lag_4_tx"]
    
    # Any transaction prior to the 120-day gap
    merged["cum_tx"] = merged.groupby("customer_id")["transaction_count"].cumsum()
    merged["tx_before_120d"] = (merged["cum_tx"] - merged["prior_120d_tx"] - merged["transaction_count"]) > 0

    logger.info("Assigning deterministic behavioral states by strict precedence...")
    # Conditions:
    # 1. REACTIVATED: valid purchase in recent period AND zero purchases in preceding 120 days AND has purchase before gap
    c_reactivated = (merged["rolling_90d_transactions"] > 0) & (merged["prior_120d_tx"] == 0) & (merged["tx_before_120d"])

    # 2. EMERGING: first valid purchase occurred within previous 90 days
    c_emerging = (merged["days_since_first"] <= 90)

    # 3. DORMANT: > 120 days since most recent valid purchase
    c_dormant = (merged["recency_at_month_end"] > 120)

    # 4. SOFTENING: <= 120 days since last purchase, prior_90d_transactions > 0, and drop >= 25%
    softening_drop = (merged["rolling_90d_transactions"] - merged["prior_90d_transactions"]) / merged["prior_90d_transactions"]
    c_softening = (~c_dormant) & (merged["prior_90d_transactions"] > 0) & (softening_drop <= -0.25)

    # Precedence: REACTIVATED -> EMERGING -> DORMANT -> SOFTENING -> ENGAGED
    state_arr = np.full(len(merged), "ENGAGED", dtype=object)
    state_arr[c_softening] = "SOFTENING"
    state_arr[c_dormant] = "DORMANT"
    state_arr[c_emerging] = "EMERGING"
    state_arr[c_reactivated] = "REACTIVATED"

    merged["behavioral_state"] = state_arr

    # Select final snapshot columns
    final_cols = [
        "customer_id",
        "year_month",
        "month_start_date",
        "month_end_date",
        "transaction_count",
        "value",
        "items",
        "product_count",
        "recency_at_month_end",
        "active_flag",
        "rolling_90d_transactions",
        "rolling_90d_value",
        "rolling_90d_products",
        "behavioral_state"
    ]
    snapshot_df = merged[final_cols].copy()
    logger.info(f"Vectorized monthly snapshot generation complete: {len(snapshot_df):,} rows.")
    return snapshot_df
