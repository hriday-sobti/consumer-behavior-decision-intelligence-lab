"""Event classification and data cleaning module.

Assigns analytical event classes with strict precedence:
  CLASS 1: CANCELLATION (Invoice starts with 'C' or 'c')
  CLASS 2: REVERSAL_OR_RETURN (quantity < 0 or negative transaction, not meeting Class 1)
  CLASS 3: VALID_PURCHASE (Quantity > 0 AND UnitPrice > 0 AND CustomerID present AND InvoiceDate valid)
  CLASS 4: INVALID_OR_UNUSABLE (All other records, including missing customer_id, non-positive price, corrupt data)
"""

from enum import Enum

import numpy as np
import pandas as pd

from src.logging_config import logger


class EventClass(str, Enum):
    CANCELLATION = "CANCELLATION"
    REVERSAL_OR_RETURN = "REVERSAL_OR_RETURN"
    VALID_PURCHASE = "VALID_PURCHASE"
    INVALID_OR_UNUSABLE = "INVALID_OR_UNUSABLE"


def classify_transaction_events(df: pd.DataFrame) -> pd.DataFrame:
    """Assigns an explicit event class to every record following strict analytical precedence.
    
    Precedence:
      1. CANCELLATION: invoice_no starts with 'C' or 'c'
      2. REVERSAL_OR_RETURN: quantity < 0 or monetary < 0 (not meeting 1)
      3. VALID_PURCHASE: quantity > 0 AND unit_price > 0 AND customer_id not null AND invoice_date valid
      4. INVALID_OR_UNUSABLE: remaining records
    """
    logger.info("Classifying transaction events according to precedence rules...")
    classified_df = df.copy()

    # Standardize column types
    classified_df["invoice_no_str"] = classified_df["invoice_no"].astype(str).str.strip()
    
    # Parse quantity and price
    q = pd.to_numeric(classified_df["quantity"], errors="coerce")
    p = pd.to_numeric(classified_df["unit_price"], errors="coerce")
    classified_df["quantity_num"] = q
    classified_df["unit_price_num"] = p
    
    # Explicit line value
    classified_df["line_value"] = q * p
    
    # Check customer id presence
    has_customer = classified_df["customer_id"].notna() & (classified_df["customer_id"].astype(str).str.strip() != "") & (classified_df["customer_id"] != 0)
    # Check date validity
    has_valid_date = pd.to_datetime(classified_df["invoice_date"], errors="coerce").notna()
    
    # Class 1: Cancellation
    is_cancellation = classified_df["invoice_no_str"].str.startswith(("C", "c"))
    
    # Class 2: Reversal or return (negative quantity with positive price, not cancellation)
    is_reversal = (~is_cancellation) & (q < 0) & (p > 0)
    
    # Class 3: Valid Purchase
    is_valid_purchase = (
        (~is_cancellation) & 
        (~is_reversal) & 
        (q > 0) & 
        (p > 0) & 
        has_customer & 
        has_valid_date
    )

    # Assign event_class
    event_classes = np.full(len(classified_df), EventClass.INVALID_OR_UNUSABLE.value, dtype=object)
    event_classes[is_reversal] = EventClass.REVERSAL_OR_RETURN.value
    event_classes[is_cancellation] = EventClass.CANCELLATION.value
    event_classes[is_valid_purchase] = EventClass.VALID_PURCHASE.value

    classified_df["event_class"] = event_classes
    
    # Cleanup temporary helper columns
    classified_df = classified_df.drop(columns=["invoice_no_str", "quantity_num", "unit_price_num"])
    
    counts = classified_df["event_class"].value_counts()
    for ev, cnt in counts.items():
        logger.info(f"Event classification - {ev}: {cnt:,} rows ({cnt / len(classified_df) * 100:.2f}%)")

    return classified_df


def clean_transactions(classified_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Applies deduplication and clean formatting to transactions.
    
    Returns:
      clean_all_df: all transactions with normalized fields, valid types, and deduplicated lines
      valid_purchases_df: subset of Class 3 VALID_PURCHASE records for customer behavioral analytics
    """
    logger.info("Cleaning transactions and applying line-level deduplication...")
    df = classified_df.copy()

    # Format dates
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    
    # Clean string fields
    df["invoice_no"] = df["invoice_no"].astype(str).str.strip()
    df["stock_code"] = df["stock_code"].astype(str).str.strip().str.upper()
    df["description"] = df["description"].fillna("").astype(str).str.strip()
    df["country"] = df["country"].fillna("Unspecified").astype(str).str.strip()
    
    # Standardize customer_id as integer string or NA
    df["customer_id"] = df["customer_id"].apply(
        lambda x: str(int(float(x))) if pd.notna(x) and str(x).strip() not in ("", "nan", "None", "0") else None
    )

    # Line deduplication (same invoice, stock code, customer, date, quantity, unit price)
    initial_len = len(df)
    df = df.drop_duplicates(
        subset=["invoice_no", "stock_code", "customer_id", "invoice_date", "quantity", "unit_price"],
        keep="first"
    ).reset_index(drop=True)
    dedup_removed = initial_len - len(df)
    logger.info(f"Deduplication removed {dedup_removed:,} duplicate rows. Remaining: {len(df):,} rows.")

    valid_purchases_df = df[df["event_class"] == EventClass.VALID_PURCHASE.value].copy().reset_index(drop=True)
    logger.info(f"Total VALID_PURCHASE rows for core behavioral analytics: {len(valid_purchases_df):,}")

    return df, valid_purchases_df
