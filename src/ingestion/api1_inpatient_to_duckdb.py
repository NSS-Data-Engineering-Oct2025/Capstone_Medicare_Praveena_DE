"""
api1_inpatient_to_duckdb.py

Reads inpatient Parquet from RustFS and loads into DuckDB raw schema.

Steps:
    1. Connect to DuckDB
    2. Read latest Parquet from RustFS into a DataFrame
    3. Truncate staging table
    4. Load DataFrame into staging table
    5. Run MERGE into final table
    6. Log row counts

Usage:
    uv run python -m src.ingestion.api1_inpatient_to_duckdb
"""

from datetime import date
import os
import duckdb
import boto3
import pandas as pd
from io import BytesIO
from loguru import logger
from botocore.client import Config
from src.config import settings
from src.utils import get_rustfs_endpoint, get_duckdb_path


# table names
FINAL_TABLE = settings.inpatient_final_table
STAGE_TABLE = settings.inpatient_stage_table

# sql file path
SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "ingest_inpatients.sql")


def get_rustfs_client():
    client = boto3.client(
        "s3",
        endpoint_url=get_rustfs_endpoint(),
        aws_access_key_id=settings.rustfs_access_key,
        aws_secret_access_key=settings.rustfs_secret_key,
        config=Config(signature_version="s3v4")
    )
    return client


def get_latest_prefix(client, base_prefix):
    """Get the most recently modified date folder from RustFS."""
    response = client.list_objects_v2(
        Bucket=settings.rustfs_bucket,
        Prefix=base_prefix
    )

    if "Contents" not in response:
        logger.error(f"No files found under: {base_prefix}")
        return None

    # filter only parquet files
    parquet_files = [
        obj for obj in response["Contents"]
        if obj["Key"].endswith(".parquet")
    ]

    if not parquet_files:
        logger.error("No parquet files found.")
        return None

    # get most recently modified file's folder
    latest = max(parquet_files, key=lambda x: x["LastModified"])

    # extract date folder
    # e.g. "inpatient/2026-05-09/part_0.parquet" → "inpatient/2026-05-09/"
    prefix = "/".join(latest["Key"].split("/")[:2]) + "/"
    logger.info(f"Latest date folder: {prefix}")
    return prefix

def get_parquet_files(client, prefix):
    """List all parquet part files under a prefix, sorted by name."""
    response = client.list_objects_v2(
        Bucket=settings.rustfs_bucket,
        Prefix=prefix
    )

    if "Contents" not in response:
        logger.error(f"No files found under: {prefix}")
        return []

    parquet_files = sorted([
        obj["Key"] for obj in response["Contents"]
        if obj["Key"].endswith(".parquet")
    ])

    logger.info(f"Found {len(parquet_files)} parquet files to load.")
    return parquet_files


def read_sql(file_path, **kwargs):
    with open(file_path, "r") as f:
        sql = f.read()
    return sql.format(**kwargs)

def main():
    logger.info("Starting inpatient ingestion → DuckDB")
    # step 1 - connect to DuckDB
    duckdb_path = get_duckdb_path()
    con = duckdb.connect(duckdb_path)
    logger.info(f"Connected to DuckDB: {duckdb_path}")

    # step 2 - get latest date folder from RustFS
    client = get_rustfs_client()
    prefix = get_latest_prefix(client, "inpatient/")

    if prefix is None:
        logger.error("No prefix found. Stopping.")
        return

    # get all part files under that prefix
    parquet_files = get_parquet_files(client, prefix)

    if not parquet_files:
        logger.error("No parquet files found. Stopping.")
        return
    # step 3 - truncate staging ONCE before loading
    con.execute(f"TRUNCATE TABLE {STAGE_TABLE};")
    logger.info(f"Truncated: {STAGE_TABLE}")

    # step 4 - insert each part file into staging one at a time

    total_loaded = 0
    for key in parquet_files:
        response = client.get_object(
            Bucket=settings.rustfs_bucket,
            Key=key
        )
        buffer = BytesIO(response["Body"].read())
        chunk = pd.read_parquet(buffer)
        con.execute(f"INSERT INTO {STAGE_TABLE} SELECT * FROM chunk;")
        total_loaded += len(chunk)
        logger.info(f"Loaded {key} → {len(chunk):,} rows | Total: {total_loaded:,}")

    logger.info(f"All parts loaded into staging. Total rows: {total_loaded:,}")

    # step 5 - run MERGE staging → final table
    merge_sql = read_sql(
        SQL_PATH,
        FINAL_TABLE=FINAL_TABLE,
        STAGE_TABLE=STAGE_TABLE
    )
    con.execute(merge_sql)
    logger.info("MERGE completed")

    # step 6 - log final row count
    final_count = con.execute(f"SELECT COUNT(*) FROM {FINAL_TABLE}").fetchone()[0]
    logger.info(f"Total rows in {FINAL_TABLE}: {final_count:,}")

    con.close()
    logger.success("Inpatient ingestion into DuckDB complete!")


if __name__ == "__main__":
    main()