"""Configuration settings for CBDIL pipeline, database, and analytical rules."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "127.0.0.1")
    port: int = int(os.getenv("DB_PORT", "54329"))
    database: str = os.getenv("DB_NAME", "cbdil_analytics")
    user: str = os.getenv("DB_USER", "cbdil_user")
    password: str = os.getenv("DB_PASSWORD", "cbdil_password")

    @property
    def connection_url(self) -> str:
        # Standard SQLAlchemy URL using psycopg3 driver
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def fallback_connection_url(self) -> str:
        # Fallback to psycopg2 driver if needed
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass(frozen=True)
class PathConfig:
    root_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    raw_data_dir: Path = BASE_DIR / "data" / "raw"
    interim_data_dir: Path = BASE_DIR / "data" / "interim"
    processed_data_dir: Path = BASE_DIR / "data" / "processed"
    outputs_dir: Path = BASE_DIR / "outputs"
    tables_dir: Path = BASE_DIR / "outputs" / "tables"
    figures_dir: Path = BASE_DIR / "outputs" / "figures"
    validation_dir: Path = BASE_DIR / "outputs" / "validation"
    exports_dir: Path = BASE_DIR / "outputs" / "exports"
    reports_dir: Path = BASE_DIR / "outputs" / "reports"
    sql_dir: Path = BASE_DIR / "sql"
    docs_dir: Path = BASE_DIR / "docs"
    powerbi_exports_dir: Path = BASE_DIR / "dashboard" / "powerbi" / "data_exports"


@dataclass(frozen=True)
class AnalyticalConfig:
    random_seed: int = int(os.getenv("RANDOM_SEED", "42"))
    
    # Time Windows (days relative to reference_date)
    # primary_behavior_window: 365 days ending one day before reference_date
    primary_behavior_window_days: int = 365
    
    # recent_window: 90 days ending one day before reference_date
    recent_window_days: int = 90
    
    # prior_window: 90 days immediately preceding the recent window (days -180 to -91)
    prior_window_days: int = 90
    
    # Customer Eligibility Rule
    # at least 2 valid purchase orders AND at least 90 days between first and reference date
    min_orders_for_eligibility: int = 2
    min_tenure_days_for_eligibility: int = 90
    
    # Lifecycle State Thresholds
    emerging_window_days: int = 90
    dormant_threshold_days: int = 120
    reactivated_gap_days: int = 120
    softening_frequency_drop_pct: float = -0.25  # at least 25% drop
    
    # Decision Signal Thresholds
    high_value_percentile: float = 0.80
    high_frequency_percentile: float = 0.80
    low_aov_percentile: float = 0.40
    broad_breadth_percentile: float = 0.70
    momentum_decline_threshold: float = -0.25
    momentum_growth_threshold: float = 0.25
    
    # Clustering search grid
    clustering_k_candidates: tuple = (3, 4, 5, 6)
    silhouette_relative_threshold: float = 0.90
    min_cluster_share: float = 0.05


# Global instances
db_config = DatabaseConfig()
path_config = PathConfig()
analytical_config = AnalyticalConfig()
