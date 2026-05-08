"""
database.py — DuckDB connection management for FastAPI.

"""

import duckdb
from loguru import logger
from src.config import settings


def get_connection() -> duckdb.DuckDBPyConnection:

    logger.debug(f"Opening DuckDB connection: {settings.duckdb_path}")
    con = duckdb.connect(settings.duckdb_path, read_only=True)
    return con