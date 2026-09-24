"""Acquire UCI Online Retail II dataset from official UCI Machine Learning Repository."""

import json
import shutil
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from src.config import path_config
from src.logging_config import logger

UCI_DATASET_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
DOI = "10.24432/C5CG6D"
SOURCE_NAME = "UCI Machine Learning Repository: Online Retail II"
SOURCE_LICENSE = "Creative Commons Attribution 4.0 International (CC BY 4.0)"

def acquire_data(force: bool = False) -> Path:
    """Downloads and unpacks the raw UCI Online Retail II dataset without altering source bytes."""
    raw_dir = path_config.raw_data_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    zip_dest = raw_dir / "online_retail_ii.zip"
    meta_dest = raw_dir / "provenance.json"
    
    # Target extracted files may be online_retail_II.xlsx
    xlsx_files = list(raw_dir.glob("*.xlsx"))
    if xlsx_files and not force:
        logger.info(f"Raw dataset already present at: {xlsx_files[0]}")
        return xlsx_files[0]

    logger.info(f"Downloading dataset from {UCI_DATASET_URL}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(UCI_DATASET_URL, headers=headers)
    
    with urllib.request.urlopen(req, timeout=60) as resp, open(zip_dest, "wb") as f:
        shutil.copyfileobj(resp, f)

    file_size = zip_dest.stat().st_size
    logger.info(f"Downloaded zip archive ({file_size / (1024*1024):.2f} MB). Extracting...")

    with zipfile.ZipFile(zip_dest, "r") as zf:
        zf.extractall(raw_dir)
        extracted_names = zf.namelist()

    target_xlsx = None
    for name in extracted_names:
        p = raw_dir / name
        if p.suffix.lower() == ".xlsx":
            target_xlsx = p
            break
            
    if not target_xlsx:
        # Check if another zip or file was inside
        for p in raw_dir.glob("*.xlsx"):
            target_xlsx = p
            break

    if not target_xlsx:
        raise FileNotFoundError(f"Could not locate extracted .xlsx file in {raw_dir}")

    metadata = {
        "source_name": SOURCE_NAME,
        "source_url": UCI_DATASET_URL,
        "source_doi": DOI,
        "retrieval_date": datetime.now(UTC).isoformat(),
        "file_name": target_xlsx.name,
        "file_size_bytes": target_xlsx.stat().st_size,
        "source_license": SOURCE_LICENSE
    }
    
    with open(meta_dest, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Dataset successfully acquired and verified at: {target_xlsx} ({target_xlsx.stat().st_size / (1024*1024):.2f} MB)")
    return target_xlsx

if __name__ == "__main__":
    acquire_data()
