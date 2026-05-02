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

import os
import duckdb
import boto3
import pandas as pd
from io import BytesIO
from loguru import logger
from botocore.client import Config
from src.config import settings


# table names
FINAL_TABLE = settings.inpatient_final_table
STAGE_TABLE = settings.inpatient_stage_table

# sql file path
SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "ingest_inpatients.sql")


def get_rustfs_client():
    # connect to RustFS using credentials from .env
    client = boto3.client(
        "s3",
        endpoint_url=settings.rustfs_endpoint,
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
    df = pd.read_parquet(buffer)
    logger.info(f"Rows read from RustFS: {len(df)}")
    return df


def read_sql(file_path, **kwargs):
    # read sql file and fill in the table name placeholders
    with open(file_path, "r") as f:
        sql = f.read()
    return sql.format(**kwargs)


def main():
    logger.info("Starting inpatient ingestion → DuckDB")

    # step 1 - connect to DuckDB
    con = duckdb.connect(settings.duckdb_path)
    logger.info(f"Connected to DuckDB: {settings.duckdb_path}")

    # step 2 - read latest parquet from RustFS
    client = get_rustfs_client()
    s3_key = get_latest_parquet_key(client, "inpatient/")

    if s3_key is None:
        logger.error("No Parquet file found. Stopping.")
        return

    df = read_parquet_from_rustfs(client, s3_key)

    if df.empty:
        logger.warning("DataFrame is empty. Stopping.")
        return

    # step 3 - truncate staging table
    con.execute(f"TRUNCATE TABLE {STAGE_TABLE};")
    logger.info(f"Truncated: {STAGE_TABLE}")

    # step 4 - load dataframe into staging table
    # DuckDB can read pandas dataframes directly
    con.execute(f"INSERT INTO {STAGE_TABLE} SELECT * FROM df;")
    stage_count = con.execute(f"SELECT COUNT(*) FROM {STAGE_TABLE}").fetchone()[0]
    logger.info(f"Rows loaded into staging: {stage_count:,}")

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
    logger.success("Inpatient ingestion into DuckDB complete!")


if __name__ == "__main__":
    main()