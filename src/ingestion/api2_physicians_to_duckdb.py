"""
api2_physicians_to_duckdb.py

Reads physician Parquet from RustFS and loads into DuckDB raw schema.
Physician dataset is large (~9.6M rows) so we load it in chunks.

Steps:
    1. Connect to DuckDB
    2. Read latest Parquet from RustFS into a DataFrame
    3. Truncate staging table
    4. Load DataFrame into staging table in chunks
    5. Run MERGE into final table
    6. Log row counts

Usage:
    uv run python -m src.ingestion.api2_physicians_to_duckdb
"""

import os
import duckdb
import boto3
import pandas as pd
from io import BytesIO
from loguru import logger
from botocore.client import Config
from src.config import settings
from  src.utils import get_duckdb_path, get_rustfs_endpoint

# table names
FINAL_TABLE = settings.physician_final_table
STAGE_TABLE = settings.physician_stage_table

# chunk size for loading large dataset — 500k rows at a time
CHUNK_SIZE = 500_000

# sql file path
SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "ingest_physicians.sql")


def get_rustfs_client():
    # connect to RustFS using credentials from .env
    client = boto3.client(
        "s3",
        endpoint_url=get_rustfs_endpoint(),
        aws_access_key_id=settings.rustfs_access_key,
        aws_secret_access_key=settings.rustfs_secret_key,
        config=Config(signature_version="s3v4")
    )
    return client


def get_latest_parquet_key(client, prefix):
    # list all files under this prefix and return the most recent one
    response = client.list_objects_v2(
        Bucket=settings.rustfs_bucket,
        Prefix=prefix
    )

    if "Contents" not in response:
        logger.error(f"No files found in RustFS under prefix: {prefix}")
        return None

    # sort by last modified and pick the latest
    files = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)
    latest_key = files[0]["Key"]
    logger.info(f"Latest Parquet found: {latest_key}")
    return latest_key


def read_parquet_from_rustfs(client, s3_key):
    # download parquet file into memory and load as dataframe
    response = client.get_object(
        Bucket=settings.rustfs_bucket,
        Key=s3_key
    )
    buffer = BytesIO(response["Body"].read())
    dataset = pd.read_parquet(buffer)
    logger.info(f"Rows read from RustFS: {len(dataset):,}")
    return dataset


def read_sql(file_path, **kwargs):
    # read sql file and fill in the table name placeholders
    with open(file_path, "r") as f:
        sql = f.read()
    return sql.format(**kwargs)


def load_in_chunks(con, dataset, stage_table, chunk_size):
    # physician dataset is ~9.6M rows — load in chunks to avoid memory issues
    total_rows = len(dataset)
    loaded = 0

    for start in range(0, total_rows, chunk_size):
        # slice the dataframe into a chunk
        chunk = dataset.iloc[start: start + chunk_size]

        # insert chunk into staging table
        con.execute(f"INSERT INTO {stage_table} SELECT * FROM chunk;")
        loaded += len(chunk)
        logger.info(f"Loaded {loaded:,} / {total_rows:,} rows into staging...")

    logger.info(f"All chunks loaded. Total rows in staging: {loaded:,}")


def main():
    logger.info("Starting physician ingestion → DuckDB")

    # step 1 - connect to DuckDB
    duckdb_path = get_duckdb_path()
    con = duckdb.connect(duckdb_path)
    logger.info(f"Connected to DuckDB: {duckdb_path}")

    # step 2 - read latest parquet from RustFS
    client = get_rustfs_client()
    s3_key = get_latest_parquet_key(client, "physician/")

    if s3_key is None:
        logger.error("No Parquet file found. Stopping.")
        return

    dataset = read_parquet_from_rustfs(client, s3_key)

    if dataset.empty:
        logger.warning("DataFrame is empty. Stopping.")
        return

    # step 3 - truncate staging table
    con.execute(f"TRUNCATE TABLE {STAGE_TABLE};")
    logger.info(f"Truncated: {STAGE_TABLE}")

    # step 4 - load dataframe into staging in chunks
    # physician dataset is large so we chunk it
    load_in_chunks(con, dataset, STAGE_TABLE, CHUNK_SIZE)

    # step 5 - run merge into final table
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
    logger.success("Physician ingestion into DuckDB complete!")


if __name__ == "__main__":
    main()