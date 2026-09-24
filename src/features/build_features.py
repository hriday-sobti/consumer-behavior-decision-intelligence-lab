"""Customer behavioral feature engineering and analytical metrics.

Implements all required customer-level features, time windows, and eligibility logic:
- Reference Date = max(valid purchase date) + 1 day
- Primary window = 365 days
- Recent window = 90 days
- Prior window = 90 days immediately preceding recent window
- Eligibility = orders >= 2 AND tenure >= 90 days
"""


import numpy as np
import pandas as pd

from src.config import analytical_config
from src.logging_config import logger


def compute_reference_date(valid_df: pd.DataFrame) -> pd.Timestamp:
    """Computes REFERENCE_DATE = maximum valid purchase date + 1 day, normalized to midnight."""
    max_date = valid_df["invoice_date"].max()
    ref_date = (max_date + pd.Timedelta(days=1)).normalize()
    return ref_date


def build_customer_features(
    all_transactions_df: pd.DataFrame,
    valid_purchases_df: pd.DataFrame,
    reference_date: pd.Timestamp | None = None
) -> pd.DataFrame:
    """Calculates all customer behavior features across the 5 analytical dimensions.
    
    Required fields:
      customer_id, first_purchase_date, last_purchase_date, customer_lifetime_days,
      recency_days, transaction_count, active_month_count, frequency_per_active_month,
      total_value, average_order_value, median_order_value, average_items_per_order,
      median_items_per_order, product_count, purchase_day_count, mean_interpurchase_days,
      median_interpurchase_days, interpurchase_gap_std, interpurchase_gap_cv,
      recent_90d_value, prior_90d_value, recent_90d_transactions, prior_90d_transactions,
      recent_90d_items, prior_90d_items, value_change_pct, frequency_change_pct,
      product_breadth_change_pct, reversal_line_count, reversal_value, reversal_rate,
      country, insufficient_history
    """
    logger.info("Building customer behavioral features...")
    if reference_date is None:
        reference_date = compute_reference_date(valid_purchases_df)
    
    logger.info(f"Analytical Reference Date: {reference_date.strftime('%Y-%m-%d %H:%M:%S')}")

    # Window definitions
    recent_start = reference_date - pd.Timedelta(days=analytical_config.recent_window_days)
    prior_start = recent_start - pd.Timedelta(days=analytical_config.prior_window_days)

    # 1. Order-level aggregation on valid purchases
    # Group by customer_id and invoice_no
    order_agg = valid_purchases_df.groupby(["customer_id", "invoice_no"]).agg(
        order_date=("invoice_date", "min"),
        order_value=("line_value", "sum"),
        order_items=("quantity", "sum"),
        order_skus=("stock_code", "nunique"),
        country=("country", "first")
    ).reset_index()

    order_agg["order_day"] = order_agg["order_date"].dt.normalize()
    order_agg["order_month"] = order_agg["order_date"].dt.to_period("M").astype(str)

    # 2. Reversal and cancellation aggregations per customer
    reversals_df = all_transactions_df[
        all_transactions_df["customer_id"].notna() & 
        all_transactions_df["event_class"].isin(["CANCELLATION", "REVERSAL_OR_RETURN"])
    ]
    reversal_summary = reversals_df.groupby("customer_id").agg(
        reversal_line_count=("invoice_no", "count"),
        reversal_value=("line_value", lambda x: abs(float(x.sum())))
    ).reset_index()

    # 3. Customer level feature engineering
    customer_rows = []
    grouped_customers = order_agg.groupby("customer_id")

    # Map reversals
    rev_dict = reversal_summary.set_index("customer_id").to_dict(orient="index")

    for cid, orders in grouped_customers:
        # Sort orders by date
        orders_sorted = orders.sort_values("order_date").reset_index(drop=True)
        first_date = orders_sorted["order_date"].min()
        last_date = orders_sorted["order_date"].max()
        
        tenure_days = int((reference_date - first_date).days)
        recency_days = int((reference_date - last_date).days)
        tx_count = len(orders_sorted)
        
        active_months = orders_sorted["order_month"].nunique()
        freq_per_active_month = round(float(tx_count / active_months), 4) if active_months > 0 else 1.0

        tot_val = float(orders_sorted["order_value"].sum())
        aov = round(float(orders_sorted["order_value"].mean()), 4)
        med_ov = round(float(orders_sorted["order_value"].median()), 4)

        avg_items = round(float(orders_sorted["order_items"].mean()), 4)
        med_items = round(float(orders_sorted["order_items"].median()), 4)
        
        purchase_days = orders_sorted["order_day"].nunique()

        # Interpurchase days
        if tx_count >= 2:
            unique_days = orders_sorted["order_day"].drop_duplicates().sort_values()
            if len(unique_days) >= 2:
                gaps = unique_days.diff().dt.days.dropna().values
                mean_gap = round(float(np.mean(gaps)), 2)
                median_gap = round(float(np.median(gaps)), 2)
                std_gap = round(float(np.std(gaps, ddof=1)), 2) if len(gaps) > 1 else 0.0
                cv_gap = round(float(std_gap / mean_gap), 4) if mean_gap > 0 else 0.0
            else:
                mean_gap, median_gap, std_gap, cv_gap = 0.0, 0.0, 0.0, 0.0
        else:
            mean_gap, median_gap, std_gap, cv_gap = None, None, None, None

        # Recent vs Prior 90d slices
        recent_orders = orders_sorted[orders_sorted["order_date"] >= recent_start]
        prior_orders = orders_sorted[(orders_sorted["order_date"] >= prior_start) & (orders_sorted["order_date"] < recent_start)]

        recent_val = float(recent_orders["order_value"].sum())
        prior_val = float(prior_orders["order_value"].sum())

        recent_tx = len(recent_orders)
        prior_tx = len(prior_orders)

        recent_items = int(recent_orders["order_items"].sum())
        prior_items = int(prior_orders["order_items"].sum())

        # Percentage momentum changes (safe explicit division)
        if prior_val > 0:
            val_change = round(float((recent_val - prior_val) / prior_val), 4)
        elif recent_val > 0:
            val_change = 1.0  # Positive growth from zero baseline
        else:
            val_change = 0.0

        if prior_tx > 0:
            freq_change = round(float((recent_tx - prior_tx) / prior_tx), 4)
        elif recent_tx > 0:
            freq_change = 1.0
        else:
            freq_change = 0.0

        # Product breadth across valid lines for this customer
        # We fetch customer valid purchases
        primary_country = orders_sorted["country"].mode().iloc[0] if not orders_sorted["country"].empty else "United Kingdom"

        # Reversal stats
        c_rev = rev_dict.get(cid, {"reversal_line_count": 0, "reversal_value": 0.0})
        rev_count = int(c_rev["reversal_line_count"])
        rev_val = float(c_rev["reversal_value"])
        rev_rate = round(float(rev_val / (tot_val + rev_val)), 4) if (tot_val + rev_val) > 0 else 0.0

        # Eligibility rule: at least 2 valid purchase orders AND at least 90 days between first and reference date
        is_ineligible = (tx_count < analytical_config.min_orders_for_eligibility) or (tenure_days < analytical_config.min_tenure_days_for_eligibility)

        customer_rows.append({
            "customer_id": cid,
            "first_purchase_date": first_date,
            "last_purchase_date": last_date,
            "customer_lifetime_days": tenure_days,
            "recency_days": recency_days,
            "transaction_count": tx_count,
            "active_month_count": active_months,
            "frequency_per_active_month": freq_per_active_month,
            "total_value": round(tot_val, 4),
            "average_order_value": aov,
            "median_order_value": med_ov,
            "average_items_per_order": avg_items,
            "median_items_per_order": med_items,
            "purchase_day_count": purchase_days,
            "mean_interpurchase_days": mean_gap,
            "median_interpurchase_days": median_gap,
            "interpurchase_gap_std": std_gap,
            "interpurchase_gap_cv": cv_gap,
            "recent_90d_value": round(recent_val, 4),
            "prior_90d_value": round(prior_val, 4),
            "recent_90d_transactions": recent_tx,
            "prior_90d_transactions": prior_tx,
            "recent_90d_items": recent_items,
            "prior_90d_items": prior_items,
            "value_change_pct": val_change,
            "frequency_change_pct": freq_change,
            "reversal_line_count": rev_count,
            "reversal_value": round(rev_val, 4),
            "reversal_rate": rev_rate,
            "country": primary_country,
            "insufficient_history": is_ineligible
        })

    feat_df = pd.DataFrame(customer_rows)

    # Calculate overall and windowed distinct product breadth from valid lines
    logger.info("Computing product counts and breadth momentum per customer...")
    valid_lines_cust = valid_purchases_df.groupby("customer_id")["stock_code"].nunique().rename("product_count")
    
    # Recent vs prior products
    recent_lines = valid_purchases_df[valid_purchases_df["invoice_date"] >= recent_start]
    prior_lines = valid_purchases_df[(valid_purchases_df["invoice_date"] >= prior_start) & (valid_purchases_df["invoice_date"] < recent_start)]
    
    recent_prod = recent_lines.groupby("customer_id")["stock_code"].nunique().rename("recent_products")
    prior_prod = prior_lines.groupby("customer_id")["stock_code"].nunique().rename("prior_products")

    feat_df = feat_df.merge(valid_lines_cust, on="customer_id", how="left")
    feat_df = feat_df.merge(recent_prod, on="customer_id", how="left")
    feat_df = feat_df.merge(prior_prod, on="customer_id", how="left")

    feat_df["recent_products"] = feat_df["recent_products"].fillna(0).astype(int)
    feat_df["prior_products"] = feat_df["prior_products"].fillna(0).astype(int)
    feat_df["product_count"] = feat_df["product_count"].fillna(0).astype(int)

    def calc_breadth_change(row):
        p = row["prior_products"]
        r = row["recent_products"]
        if p > 0:
            return round((r - p) / p, 4)
        elif r > 0:
            return 1.0
        return 0.0

    feat_df["product_breadth_change_pct"] = feat_df.apply(calc_breadth_change, axis=1)
    feat_df = feat_df.drop(columns=["recent_products", "prior_products"])

    logger.info(f"Customer features built for {len(feat_df):,} customers.")
    logger.info(f"Eligible customers: {(~feat_df['insufficient_history']).sum():,}; Insufficient history: {feat_df['insufficient_history'].sum():,}")
    return feat_df
