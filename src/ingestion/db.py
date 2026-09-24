"""Database connection and initialization utilities."""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import db_config, path_config
from src.logging_config import logger


def get_engine() -> Engine:
    """Returns a SQLAlchemy engine connected to the PostgreSQL analytical database."""
    # Using psycopg binary driver with trust / explicit credentials
    url = f"postgresql+psycopg://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
    return create_engine(url, pool_pre_ping=True)


def init_database(engine: Engine | None = None) -> None:
    """Executes all DDL scripts in sequence to prepare schemas, tables, and views."""
    if engine is None:
        engine = get_engine()
        
    sql_files = sorted(path_config.sql_dir.glob("*.sql"))
    logger.info(f"Applying {len(sql_files)} SQL schema scripts to PostgreSQL...")

    with engine.begin() as conn:
        for sql_file in sql_files:
            # Skip validation queries during schema creation
            if sql_file.name.startswith("11_"):
                continue
            logger.info(f"Applying schema script: {sql_file.name}")
            with open(sql_file, "r", encoding="utf-8") as f:
                statements = f.read()
            # Split and execute individual statements
            conn.execute(text(statements))

    logger.info("All PostgreSQL database schemas and tables successfully initialized.")
