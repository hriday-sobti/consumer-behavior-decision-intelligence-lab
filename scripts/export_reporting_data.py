"""Reporting data export script."""

from src.logging_config import logger
from src.reporting.export_reporting import export_reporting_data

if __name__ == "__main__":
    logger.info("Executing export_reporting_data.py script...")
    export_reporting_data()
