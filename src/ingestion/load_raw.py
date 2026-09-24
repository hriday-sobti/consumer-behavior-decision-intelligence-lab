"""Data ingestion module for UCI Online Retail II dataset.

Preserves raw inputs verbatim and parses both longitudinal sheets ('Year 2009-2010' and 'Year 2010-2011').
"""

from pathlib import Path

import pandas as pd

from src.config import path_config
from src.logging_config import logger

RAW_SCHEMA_MAP = {
    "Invoice": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "Customer ID": "customer_id",
    "Country": "country"
}

def load_raw_data(file_path: Path | None = None) -> pd.DataFrame:
    """Reads both sheets of the raw Excel workbook without modifying raw files.
    
    Returns a unified raw DataFrame with tracked source sheets.
    """
    if file_path is None:
        xlsx_files = list(path_config.raw_data_dir.glob("*.xlsx"))
        if not xlsx_files:
            raise FileNotFoundError(f"No Excel dataset found in {path_config.raw_data_dir}")
        file_path = xlsx_files[0]

    logger.info(f"Loading raw data workbook: {file_path}")
    excel_file = pd.ExcelFile(file_path, engine="openpyxl")
    sheet_dfs = []

    for sheet in excel_file.sheet_names:
        logger.info(f"Reading sheet: '{sheet}'...")
        df_sheet = pd.read_excel(excel_file, sheet_name=sheet)
        df_sheet["source_sheet"] = str(sheet)
        # Rename standard columns
        df_sheet = df_sheet.rename(columns=RAW_SCHEMA_MAP)
        sheet_dfs.append(df_sheet)
        logger.info(f"Sheet '{sheet}' loaded: {len(df_sheet):,} rows, {len(df_sheet.columns)} columns.")

    raw_df = pd.concat(sheet_dfs, ignore_index=True)
    logger.info(f"Unified raw dataset loaded: {len(raw_df):,} total rows, {len(raw_df.columns)} columns.")
    return raw_df
