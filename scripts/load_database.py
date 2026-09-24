"""Load processed tables into PostgreSQL database."""

from src.ingestion.load_database import load_database_tables
from src.logging_config import logger

if __name__ == "__main__":
    logger.info("Executing load_database.py script...")
    load_database_tables()
