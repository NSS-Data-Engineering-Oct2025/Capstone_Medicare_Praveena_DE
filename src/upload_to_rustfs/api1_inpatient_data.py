import time
import random
import requests
import polars as pl
from datetime import date
from loguru import logger
from src.config import settings
from src.utils import ensure_bucket_exists, upload_parquet_to_rustfs


def fetch_inpatient_data(max_retries=5, base_delay=1):
    """
    Fetch inpatient data with:
    - pagination (5000 rows/batch)
    - exponential backoff retry
    - chunked uploads every 100k rows using Polars
    """
    url = f"{settings.cms_api_base_url}/{settings.cms_inpatient_dataset_id}/data"
    today = date.today()

    chunk = []
    chunk_number = 0
    total_rows = 0
    offset = 0
    limit = 5000

    logger.info("Starting to fetch inpatient hospital data...")

    while True:
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params={"size": limit, "offset": offset},
                    timeout=60
                )
                response.raise_for_status()
                batch = response.json()
                break

            except requests.exceptions.RequestException as e:
                wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {wait_time:.2f}s..."
                )
                time.sleep(wait_time)
        else:
            logger.error(f"Max retries exceeded at offset {offset}. Stopping.")
            if chunk:
                s3_key = f"inpatient/{today}/part_{chunk_number}.parquet"
                upload_parquet_to_rustfs(pl.DataFrame(chunk), s3_key)
                logger.info(f"Saved partial chunk {chunk_number} before stopping.")
            return total_rows

        if not batch:
            logger.info("No more data to fetch.")
            break

        chunk.extend(batch)
        total_rows += len(batch)
        offset += limit

        logger.info(f"Fetched {total_rows:,} rows so far...")

        # upload every 100k rows using Polars — memory efficient
        if len(chunk) >= 100_000:
            s3_key = f"inpatient/{today}/part_{chunk_number}.parquet"
            upload_parquet_to_rustfs(pl.DataFrame(chunk), s3_key)
            logger.success(
                f"Uploaded chunk {chunk_number} ({len(chunk):,} rows) → {s3_key}"
            )
            chunk = []        # release memory immediately
            chunk_number += 1

        if len(batch) < limit:
            logger.info("Reached last page.")
            break

        time.sleep(1)

    # upload remaining rows
    if chunk:
        s3_key = f"inpatient/{today}/part_{chunk_number}.parquet"
        upload_parquet_to_rustfs(pl.DataFrame(chunk), s3_key)
        logger.success(
            f"Uploaded final chunk {chunk_number} ({len(chunk):,} rows) → {s3_key}"
        )

    logger.info(f"Finished fetching. Total rows: {total_rows:,}")
    return total_rows


def run():
    ensure_bucket_exists()

    total_rows = fetch_inpatient_data()

    if total_rows == 0:
        logger.warning("No data fetched. Stopping.")
        return

    logger.success(f"Inpatient data ingestion done! Total rows: {total_rows:,}")


if __name__ == "__main__":
    run()