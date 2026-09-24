"""Run profiling on raw data and save outputs/tables/data_profile.csv and data_quality_issues.csv."""

from src.config import path_config
from src.ingestion.load_raw import load_raw_data
from src.logging_config import logger
from src.validation.profile import profile_dataset


def run_profiling():
    logger.info("Executing raw dataset profiling pipeline...")
    raw_df = load_raw_data()
    
    profile_df, issues_df = profile_dataset(raw_df)
    
    path_config.tables_dir.mkdir(parents=True, exist_ok=True)
    profile_csv = path_config.tables_dir / "data_profile.csv"
    issues_csv = path_config.tables_dir / "data_quality_issues.csv"
    
    profile_df.to_csv(profile_csv, index=False)
    issues_df.to_csv(issues_csv, index=False)
    
    logger.info(f"Data profile saved to: {profile_csv}")
    logger.info(f"Data quality issues saved to: {issues_csv}")
    
    # Save raw to interim parquet with safe explicit types (without modifying raw source file)
    interim_raw_parquet = path_config.interim_data_dir / "raw_unified.parquet"
    path_config.interim_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Cast object columns to strings for pyarrow compatibility
    interim_df = raw_df.copy()
    interim_df["invoice_no"] = interim_df["invoice_no"].astype(str)
    interim_df["stock_code"] = interim_df["stock_code"].astype(str)
    interim_df["description"] = interim_df["description"].fillna("").astype(str)
    interim_df["country"] = interim_df["country"].fillna("").astype(str)
    interim_df["source_sheet"] = interim_df["source_sheet"].astype(str)
    
    interim_df.to_parquet(interim_raw_parquet, index=False)
    logger.info(f"Saved interim raw parquet to {interim_raw_parquet} for rapid pipeline reloads.")

if __name__ == "__main__":
    run_profiling()
