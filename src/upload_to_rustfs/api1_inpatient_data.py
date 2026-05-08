import time
import random
import requests
import pandas as pd
from datetime import date
from loguru import logger
from src.config import settings
from src.utils import ensure_bucket_exists, upload_parquet_to_rustfs


def fetch_inpatient_data(max_retries=5, base_delay=1):
    """Fetch inpatient data with pagination, exponential backoff, and max retries."""
    url = f"{settings.cms_api_base_url}/{settings.cms_inpatient_dataset_id}/data"
 
    all_data = []
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
                break  # success — exit retry loop
 
            except requests.exceptions.RequestException as e:
                wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f}s..."
                )
                time.sleep(wait_time)
        else:
            # all retries failed
            logger.error(f"Max retries exceeded for offset {offset}. Stopping.")
            return pd.DataFrame()
 
        if not batch:
            logger.info("No more data to fetch.")
            break
 
        all_data.extend(batch)
        logger.info(f"Fetched {len(all_data)} rows so far...")
 
        if len(batch) < limit:
            logger.info("Reached last page.")
            break
 
        offset = offset + limit
        time.sleep(1)  # avoid hitting API rate limits
 
    final_data = pd.DataFrame(all_data)
    logger.info(f"Finished fetching. Total rows: {len(final_data)}")
    logger.info(f"Columns in data: {list(final_data.columns)}")
    return final_data


def run():
    # step 1 - make sure bucket exists in RustFS
    ensure_bucket_exists()

    # step 2 - fetch the data from API
    final_data = fetch_inpatient_data()

    # step 3 - check if we got any data
    if final_data.empty:
        logger.warning("No data fetched. Stopping.")
        return

    # step 4 - build the file path inside RustFS
    # using today's date so each run saves separately
    today = date.today()
    s3_key = f"inpatient/{today}/inpatient_hospitals.parquet"

    # step 5 - upload to RustFS
    upload_parquet_to_rustfs(final_data, s3_key)
    logger.success("Inpatient data ingestion done!")


# this runs when you do: python -m src.ingestion.api1
if __name__ == "__main__":
    run()