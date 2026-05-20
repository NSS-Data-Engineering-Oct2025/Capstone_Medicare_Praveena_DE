"""
database.py — DuckDB connection management for FastAPI.

"""

import duckdb
from loguru import logger
from src.config import settings


def get_connection() -> duckdb.DuckDBPyConnection:

    logger.debug(f"Opening DuckDB connection: {settings.duckdb_path}")
    con = duckdb.connect(settings.duckdb_path, read_only=True)
    try:
        yield con        # FastAPI manages lifecycle
    finally:
        con.close()      # always closes after request finishes
        logger.debug("DuckDB connection closed.")