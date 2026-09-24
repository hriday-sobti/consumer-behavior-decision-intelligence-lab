"""Export reporting-ready summary CSV and parquet files for dashboards and stakeholders."""

import pandas as pd

from src.config import path_config
from src.decisions.insights import build_data_controls, generate_automated_insights
from src.logging_config import logger


def export_reporting_data():
    """Generates all 9 standardized reporting exports into outputs/exports/ and dashboard/powerbi/data_exports/."""
    logger.info("Generating standardized reporting exports...")
    # Ingest analytical parquet models produced by upstream feature and lifecycle stages
    feat_df = pd.read_parquet(path_config.processed_data_dir / "customer_behavior_features.parquet")
    valid_tx = pd.read_parquet(path_config.processed_data_dir / "transactions_valid_purchases.parquet")
    seg_cust_df = pd.read_parquet(path_config.processed_data_dir / "customer_segment.parquet")
    seg_prof_df = pd.read_parquet(path_config.processed_data_dir / "segment_profile.parquet")
    snap_df = pd.read_parquet(path_config.processed_data_dir / "customer_monthly_snapshot.parquet")
    signals_df = pd.read_parquet(path_config.processed_data_dir / "customer_decision_signal.parquet")
    pd.read_parquet(path_config.processed_data_dir / "decision_strategy.parquet")
    mat_df = pd.read_parquet(path_config.processed_data_dir / "state_transition_matrix.parquet")

    # Latest state per customer
    latest_state = snap_df.sort_values("year_month").groupby("customer_id")["behavioral_state"].last().to_dict()

    # Segments map
    seg_map = seg_cust_df.set_index("customer_id")["segment_name"].to_dict()

    # Primary active signal per customer
    top_sig = signals_df.sort_values("signal_strength").groupby("customer_id")["signal_name"].first().to_dict()

    # 1. customer_summary.csv
    logger.info("Exporting customer_summary.csv...")
    cust_sum = pd.DataFrame({
        "customer_id": feat_df["customer_id"],
        "segment_name": feat_df["customer_id"].map(seg_map).fillna("Unsegmented (Insufficient History)"),
        "behavioral_state": feat_df["customer_id"].map(latest_state).fillna("UNKNOWN"),
        "primary_country": feat_df["country"],
        "lifetime_orders": feat_df["transaction_count"],
        "total_value": feat_df["total_value"],
        "recency_days": feat_df["recency_days"],
        "average_order_value": feat_df["average_order_value"],
        "recent_90d_value": feat_df["recent_90d_value"],
        "prior_90d_value": feat_df["prior_90d_value"],
        "value_momentum_pct": feat_df["value_change_pct"],
        "frequency_momentum_pct": feat_df["frequency_change_pct"],
        "product_count": feat_df["product_count"],
        "primary_active_signal": feat_df["customer_id"].map(top_sig).fillna("None"),
        "insufficient_history": feat_df["insufficient_history"]
    })

    # 2. segment_summary.csv
    logger.info("Exporting segment_summary.csv...")
    seg_sum = seg_prof_df.copy()

    # 3. monthly_summary.csv
    logger.info("Exporting monthly_summary.csv...")
    m_agg = snap_df.groupby("year_month").agg(
        active_customers=("active_flag", lambda s: int(s.sum())),
        total_orders=("transaction_count", "sum"),
        total_items=("items", "sum"),
        total_value=("value", "sum"),
        emerging_customers=("behavioral_state", lambda s: int((s == "EMERGING").sum())),
        reactivated_customers=("behavioral_state", lambda s: int((s == "REACTIVATED").sum())),
        dormant_customers=("behavioral_state", lambda s: int((s == "DORMANT").sum())),
        engaged_customers=("behavioral_state", lambda s: int((s == "ENGAGED").sum())),
        softening_customers=("behavioral_state", lambda s: int((s == "SOFTENING").sum()))
    ).reset_index()
    m_agg["average_order_value"] = (m_agg["total_value"] / m_agg["total_orders"]).round(2).fillna(0.0)

    # 4. state_transitions.csv
    logger.info("Exporting state_transitions.csv...")
    state_trans = mat_df.copy()

    # 5. decision_signals.csv
    logger.info("Exporting decision_signals.csv...")
    dec_signals = signals_df.copy()

    # 6. data_controls.csv
    logger.info("Exporting data_controls.csv...")
    raw_profile = pd.read_csv(path_config.tables_dir / "data_profile.csv")
    raw_issues = pd.read_csv(path_config.tables_dir / "data_quality_issues.csv")
    data_ctrl = build_data_controls(raw_profile, raw_issues, feat_df, seg_cust_df)

    # 7. cohort_summary.csv (acquisition cohort retention grid)
    logger.info("Exporting cohort_summary.csv...")
    valid_tx["order_date"] = pd.to_datetime(valid_tx["invoice_date"])
    first_month_map = valid_tx.groupby("customer_id")["order_date"].min().dt.to_period("M").astype(str).to_dict()
    valid_tx["cohort_month"] = valid_tx["customer_id"].map(first_month_map)
    valid_tx["order_month"] = valid_tx["order_date"].dt.to_period("M").astype(str)

    cohort_counts = valid_tx.groupby("cohort_month")["customer_id"].nunique().reset_index(name="customers_acquired")
    cohort_activity = valid_tx.groupby(["cohort_month", "order_month"])["customer_id"].nunique().reset_index(name="active_customers")
    
    # Calculate month index: (order_year - cohort_year)*12 + (order_month - cohort_month)
    def calc_cohort_index(row):
        c = pd.Period(row["cohort_month"], freq="M")
        o = pd.Period(row["order_month"], freq="M")
        return (o.year - c.year) * 12 + (o.month - c.month)

    cohort_activity["cohort_index"] = cohort_activity.apply(calc_cohort_index, axis=1)
    cohort_summary = cohort_activity.merge(cohort_counts, on="cohort_month", how="left")
    cohort_summary["retention_rate"] = (cohort_summary["active_customers"] / cohort_summary["customers_acquired"]).round(4)

    # 8. country_summary.csv
    logger.info("Exporting country_summary.csv...")
    country_sum = feat_df.groupby("country").agg(
        customer_count=("customer_id", "count"),
        total_orders=("transaction_count", "sum"),
        total_value=("total_value", "sum"),
        average_order_value=("average_order_value", "mean"),
        median_recency=("recency_days", "median")
    ).reset_index().sort_values("total_value", ascending=False)
    country_sum["value_share"] = (country_sum["total_value"] / country_sum["total_value"].sum()).round(4)

    # 9. product_summary.csv
    logger.info("Exporting product_summary.csv...")
    prod_sum = valid_tx.groupby(["stock_code", "description"]).agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("line_value", "sum"),
        customer_count=("customer_id", "nunique"),
        order_count=("invoice_no", "nunique")
    ).reset_index().sort_values("total_revenue", ascending=False).head(500)
    prod_sum["revenue_share"] = (prod_sum["total_revenue"] / valid_tx["line_value"].sum()).round(4)

    # Save to outputs/exports and dashboard/powerbi/data_exports
    export_targets = [path_config.exports_dir, path_config.powerbi_exports_dir]
    files = {
        "customer_summary.csv": cust_sum,
        "segment_summary.csv": seg_sum,
        "monthly_summary.csv": m_agg,
        "state_transitions.csv": state_trans,
        "decision_signals.csv": dec_signals,
        "data_controls.csv": data_ctrl,
        "cohort_summary.csv": cohort_summary,
        "country_summary.csv": country_sum,
        "product_summary.csv": prod_sum
    }

    for target_dir in export_targets:
        target_dir.mkdir(parents=True, exist_ok=True)
        for fname, df_item in files.items():
            dest = target_dir / fname
            df_item.to_csv(dest, index=False)
            logger.info(f"Wrote reporting export: {dest}")

    # Generate insights table
    insights_df = generate_automated_insights(feat_df, seg_prof_df, dec_signals, snap_df)
    insights_csv = path_config.tables_dir / "automated_insights.csv"
    insights_df.to_csv(insights_csv, index=False)
    logger.info(f"Automated insights exported to: {insights_csv}")

if __name__ == "__main__":
    export_reporting_data()
