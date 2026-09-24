"""Unit and integration tests for data ingestion, loading, and schema verification."""

import pandas as pd

from src.config import path_config


def test_raw_provenance_file_exists():
    """Verify that provenance metadata is stored and non-empty."""
    prov_file = path_config.raw_data_dir / "provenance.json"
    assert prov_file.exists(), "Provenance file data/raw/provenance.json must exist."
    content = prov_file.read_text(encoding="utf-8")
    assert "UCI Machine Learning Repository" in content
    assert "10.24432/C5CG6D" in content

def test_raw_dataset_is_present():
    """Verify raw excel file presence without corruption."""
    xlsx_files = list(path_config.raw_data_dir.glob("*.xlsx"))
    assert len(xlsx_files) >= 1, "Raw Excel workbook must exist in data/raw."
    assert xlsx_files[0].stat().st_size > 40 * 1024 * 1024, "Raw Excel workbook must be > 40MB."

def test_interim_cache_validity():
    """Verify that interim cache contains expected raw columns."""
    interim_raw = path_config.interim_data_dir / "raw_unified.parquet"
    assert interim_raw.exists(), "Interim parquet cache must exist."
    df = pd.read_parquet(interim_raw)
    assert len(df) > 1_000_000, "Raw records count should exceed 1,000,000."
    required_cols = {"invoice_no", "stock_code", "quantity", "invoice_date", "unit_price", "customer_id", "country"}
    assert required_cols.issubset(set(df.columns)), f"Columns missing from interim: {required_cols - set(df.columns)}"
