"""Data profiling and quality investigation module."""

import pandas as pd

from src.logging_config import logger


def profile_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Computes comprehensive field-level statistics and systematic quality issue counts.
    
    Generates:
      1. profile_df: data type, nulls, distincts, quantiles, min, max, examples
      2. issues_df: count and percentage of specific data quality anomalies
    """
    logger.info("Computing field-level statistical profile...")
    profile_rows = []
    n_rows = len(df)

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_pct = float((missing_count / n_rows) * 100) if n_rows > 0 else 0.0
        distinct_count = int(series.nunique(dropna=False))
        
        # Calculate numeric statistics if applicable
        is_numeric = pd.api.types.is_numeric_dtype(series)
        is_datetime = pd.api.types.is_datetime64_any_dtype(series)
        
        min_val = None
        max_val = None
        mean_val = None
        median_val = None
        q25_val = None
        q75_val = None

        if is_numeric and not series.dropna().empty:
            clean_s = series.dropna()
            min_val = float(clean_s.min())
            max_val = float(clean_s.max())
            mean_val = float(clean_s.mean())
            median_val = float(clean_s.median())
            q25_val = float(clean_s.quantile(0.25))
            q75_val = float(clean_s.quantile(0.75))
        elif is_datetime and not series.dropna().empty:
            clean_s = series.dropna()
            min_val = str(clean_s.min())
            max_val = str(clean_s.max())

        # Sample non-null examples
        examples = series.dropna().unique()[:3]
        example_str = "; ".join(str(x) for x in examples)

        profile_rows.append({
            "field_name": col,
            "data_type": str(series.dtype),
            "total_rows": n_rows,
            "missing_count": missing_count,
            "missing_pct": round(missing_pct, 2),
            "distinct_count": distinct_count,
            "min_value": min_val,
            "q25_value": q25_val,
            "median_value": median_val,
            "mean_value": round(mean_val, 4) if mean_val is not None else None,
            "q75_value": q75_val,
            "max_value": max_val,
            "sample_examples": example_str
        })

    profile_df = pd.DataFrame(profile_rows)

    logger.info("Investigating data quality anomalies...")
    # Specific investigations
    dup_rows = int(df.duplicated(subset=["invoice_no", "stock_code", "customer_id", "invoice_date", "quantity", "unit_price"]).sum())
    
    # Cancellations (Invoice starting with 'C' or 'c')
    str_invoices = df["invoice_no"].astype(str)
    cancellations = int(str_invoices.str.startswith(("C", "c")).sum())
    
    # Negative / zero quantities
    num_quantity = pd.to_numeric(df["quantity"], errors="coerce")
    neg_quantity = int((num_quantity < 0).sum())
    zero_quantity = int((num_quantity == 0).sum())
    
    # Negative / zero prices
    num_price = pd.to_numeric(df["unit_price"], errors="coerce")
    neg_price = int((num_price < 0).sum())
    zero_price = int((num_price == 0).sum())
    
    # Missing customer ID
    missing_customer = int(df["customer_id"].isna().sum())
    
    # Missing description or whitespace
    str_desc = df["description"].fillna("").astype(str)
    empty_or_ws_desc = int((str_desc.str.strip() == "").sum())
    
    # StockCode irregularities (e.g. non-product codes like POST, D, M, BANK CHARGES)
    str_stock = df["stock_code"].astype(str).str.strip().str.upper()
    unusual_stock_codes = int(str_stock.isin(["POST", "D", "M", "BANK CHARGES", "PADS", "DOT", "CRUK", "AMAZONFEE"]).sum())

    issues = [
        {"issue_type": "duplicate_transaction_lines", "affected_count": dup_rows, "affected_pct": round(dup_rows / n_rows * 100, 2), "severity": "WARNING", "impact": "Overcounts activity if not deduplicated or audited."},
        {"issue_type": "cancellation_invoices", "affected_count": cancellations, "affected_pct": round(cancellations / n_rows * 100, 2), "severity": "INFO", "impact": "Must be classified as cancellations; separate from valid sales."},
        {"issue_type": "negative_quantities", "affected_count": neg_quantity, "affected_pct": round(neg_quantity / n_rows * 100, 2), "severity": "WARNING", "impact": "Reversals or damaged goods; distorts raw sum totals."},
        {"issue_type": "zero_quantities", "affected_count": zero_quantity, "affected_pct": round(zero_quantity / n_rows * 100, 2), "severity": "WARNING", "impact": "Null transactions; non-purchases."},
        {"issue_type": "negative_unit_prices", "affected_count": neg_price, "affected_pct": round(neg_price / n_rows * 100, 2), "severity": "FAIL", "impact": "Corrupted accounting adjustment records (e.g. debt adjustments)."},
        {"issue_type": "zero_unit_prices", "affected_count": zero_price, "affected_pct": round(zero_price / n_rows * 100, 2), "severity": "WARNING", "impact": "Free samples, giveaways, or inventory audits."},
        {"issue_type": "missing_customer_ids", "affected_count": missing_customer, "affected_pct": round(missing_customer / n_rows * 100, 2), "severity": "WARNING", "impact": "Cannot be attributed to customer grain; excluded from customer segmentation."},
        {"issue_type": "empty_or_whitespace_descriptions", "affected_count": empty_or_ws_desc, "affected_pct": round(empty_or_ws_desc / n_rows * 100, 2), "severity": "WARNING", "impact": "Missing descriptive metadata."},
        {"issue_type": "non_product_stock_codes", "affected_count": unusual_stock_codes, "affected_pct": round(unusual_stock_codes / n_rows * 100, 2), "severity": "INFO", "impact": "Postage, bank charges, manual adjustments."}
    ]
    issues_df = pd.DataFrame(issues)
    return profile_df, issues_df
