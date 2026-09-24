"""Database loader module: Loads staging, dimensional, fact, analytical, and reporting tables into PostgreSQL."""

import pandas as pd

from src.config import path_config
from src.ingestion.db import get_engine, init_database
from src.logging_config import logger


def load_database_tables():
    """Populates PostgreSQL database from processed parquet datasets."""
    logger.info("Connecting to PostgreSQL and verifying table schemas...")
    engine = get_engine()
    
    # Ensure fresh clean schema
    init_database(engine)

    # 1. Load Staging Raw Transactions
    logger.info("Loading staging.raw_retail_transactions...")
    tx_all_path = path_config.processed_data_dir / "transactions_all_classified.parquet"
    tx_all_df = pd.read_parquet(tx_all_path)
    
    # Align columns
    staging_df = tx_all_df[[
        "invoice_no", "stock_code", "description", "quantity",
        "invoice_date", "unit_price", "line_value", "customer_id",
        "country", "source_sheet", "event_class"
    ]].copy()
    
    # Chunked insertion for staging
    staging_df.to_sql(
        "raw_retail_transactions",
        engine,
        schema="staging",
        if_exists="append",
        index=False,
        chunksize=10000
    )
    logger.info(f"Loaded {len(staging_df):,} rows into staging.raw_retail_transactions.")

    # 2. Dimensions
    logger.info("Populating analytics dimensions (dim_customer, dim_product, dim_country, dim_date)...")
    valid_tx_path = path_config.processed_data_dir / "transactions_valid_purchases.parquet"
    valid_tx = pd.read_parquet(valid_tx_path)

    # Dim Country
    unique_countries = sorted(tx_all_df["country"].dropna().unique())
    country_df = pd.DataFrame({
        "country_key": range(1, len(unique_countries) + 1),
        "country_name": unique_countries,
        "region": ["Domestic" if c == "United Kingdom" else "International" for c in unique_countries]
    })
    country_df.to_sql("dim_country", engine, schema="analytics", if_exists="append", index=False)
    country_map = country_df.set_index("country_name")["country_key"].to_dict()

    # Dim Product
    prod_agg = tx_all_df.groupby("stock_code").agg(
        primary_description=("description", "first")
    ).reset_index()
    prod_agg["product_key"] = range(1, len(prod_agg) + 1)
    prod_agg["is_manual_or_fee"] = prod_agg["stock_code"].isin(["POST", "D", "M", "BANK CHARGES", "PADS", "DOT", "CRUK", "AMAZONFEE"])
    
    prod_df = prod_agg[["product_key", "stock_code", "primary_description", "is_manual_or_fee"]]
    prod_df.to_sql("dim_product", engine, schema="analytics", if_exists="append", index=False)
    prod_map = prod_df.set_index("stock_code")["product_key"].to_dict()

    # Dim Date
    min_date = tx_all_df["invoice_date"].min().date()
    max_date = tx_all_df["invoice_date"].max().date()
    date_range = pd.date_range(min_date, max_date, freq="D")
    
    date_rows = []
    for d in date_range:
        date_rows.append({
            "date_key": int(d.strftime("%Y%m%d")),
            "full_date": d.date(),
            "year_num": d.year,
            "quarter_num": d.quarter,
            "month_num": d.month,
            "month_name": d.strftime("%B"),
            "year_month": d.strftime("%Y-%m"),
            "day_num": d.day,
            "day_of_week": d.dayofweek + 1,
            "day_name": d.strftime("%A"),
            "is_weekend": d.dayofweek in (5, 6)
        })
    dim_date_df = pd.DataFrame(date_rows)
    dim_date_df.to_sql("dim_date", engine, schema="analytics", if_exists="append", index=False)

    # Dim Customer
    feat_path = path_config.processed_data_dir / "customer_behavior_features.parquet"
    feat_df = pd.read_parquet(feat_path)
    
    dim_cust_df = pd.DataFrame({
        "customer_key": range(1, len(feat_df) + 1),
        "customer_id": feat_df["customer_id"],
        "first_purchase_date": feat_df["first_purchase_date"],
        "last_purchase_date": feat_df["last_purchase_date"],
        "primary_country": feat_df["country"]
    })
    dim_cust_df.to_sql("dim_customer", engine, schema="analytics", if_exists="append", index=False)
    cust_map = dim_cust_df.set_index("customer_id")["customer_key"].to_dict()

    # 3. Fact Order & Fact Transaction
    logger.info("Populating analytics fact tables (fact_order, fact_transaction)...")
    valid_tx["date_key"] = pd.to_datetime(valid_tx["invoice_date"]).dt.strftime("%Y%m%d").astype(int)
    valid_tx["customer_key"] = valid_tx["customer_id"].map(cust_map)
    valid_tx["product_key"] = valid_tx["stock_code"].map(prod_map)
    valid_tx["country_key"] = valid_tx["country"].map(country_map)

    # Aggregate Fact Order
    order_agg = valid_tx.groupby("invoice_no").agg(
        customer_key=("customer_key", "first"),
        customer_id=("customer_id", "first"),
        date_key=("date_key", "first"),
        order_timestamp=("invoice_date", "min"),
        country_key=("country_key", "first"),
        line_item_count=("stock_code", "count"),
        total_quantity=("quantity", "sum"),
        order_value=("line_value", "sum")
    ).reset_index()
    order_agg["is_cancellation"] = False
    order_agg["is_reversal"] = False

    order_agg.to_sql("fact_order", engine, schema="analytics", if_exists="append", index=False, chunksize=5000)
    logger.info(f"Loaded {len(order_agg):,} orders into analytics.fact_order.")

    # 4. Load Analytics Tables
    logger.info("Loading customer behavioral features, RFM, segments, and snapshots into PostgreSQL...")
    feat_df["customer_key"] = feat_df["customer_id"].map(cust_map)
    feat_df.to_sql("customer_behavior_features", engine, schema="analytics", if_exists="append", index=False, chunksize=2000)

    rfm_path = path_config.processed_data_dir / "customer_rfm.parquet"
    rfm_df = pd.read_parquet(rfm_path)
    rfm_df.to_sql("customer_rfm", engine, schema="analytics", if_exists="append", index=False, chunksize=2000)

    seg_prof_path = path_config.processed_data_dir / "segment_profile.parquet"
    seg_prof_df = pd.read_parquet(seg_prof_path)
    seg_prof_df.to_sql("segment_profile", engine, schema="analytics", if_exists="append", index=False)

    seg_cust_path = path_config.processed_data_dir / "customer_segment.parquet"
    seg_cust_df = pd.read_parquet(seg_cust_path)[[
        "customer_id", "segment_id", "segment_name", "log_total_value",
        "log_transaction_count", "recency_days", "log_product_count",
        "mean_interpurchase_days", "value_momentum_pct", "frequency_momentum_pct",
        "distance_to_center"
    ]]
    seg_cust_df.to_sql("customer_segment", engine, schema="analytics", if_exists="append", index=False, chunksize=2000)

    snap_path = path_config.processed_data_dir / "customer_monthly_snapshot.parquet"
    snap_df = pd.read_parquet(snap_path)
    snap_df.to_sql("customer_monthly_snapshot", engine, schema="analytics", if_exists="append", index=False, chunksize=5000)

    hist_path = path_config.processed_data_dir / "customer_state_history.parquet"
    hist_df = pd.read_parquet(hist_path)
    hist_df.to_sql("customer_state_history", engine, schema="analytics", if_exists="append", index=False, chunksize=5000)

    mat_path = path_config.processed_data_dir / "state_transition_matrix.parquet"
    mat_df = pd.read_parquet(mat_path)
    mat_df.to_sql("state_transition_matrix", engine, schema="analytics", if_exists="append", index=False)

    sig_path = path_config.processed_data_dir / "customer_decision_signal.parquet"
    sig_df = pd.read_parquet(sig_path)
    sig_df.to_sql("customer_decision_signal", engine, schema="analytics", if_exists="append", index=False, chunksize=2000)

    strat_path = path_config.processed_data_dir / "decision_strategy.parquet"
    strat_df = pd.read_parquet(strat_path)
    strat_df.to_sql("decision_strategy", engine, schema="analytics", if_exists="append", index=False)

    logger.info("PostgreSQL database fully populated with analytical tables.")

if __name__ == "__main__":
    load_database_tables()
