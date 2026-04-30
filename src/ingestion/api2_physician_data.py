import requests
import pandas as pd
from datetime import date
from loguru import logger
from src.ingestion.config import settings
from src.ingestion.utils import ensure_bucket_exists, upload_parquet_to_rustfs


def fetch_physician_data():
    # build the API url using physician dataset id from .env
    url = f"{settings.cms_api_base_url}/{settings.cms_physician_dataset_id}/data"

    all_data = []   # we will collect all rows here
    offset = 0      # starting point
    limit = 5000    # how many rows to fetch per request

    logger.info("Starting to fetch physician data...")

    while True:
        # add pagination params to the request
        params = {
            "size": limit,
            "offset": offset
        }

        # hit the API
        response = requests.get(url, params=params, timeout=60)

        # if request failed, stop and show error
        response.raise_for_status()

        # convert response to list of rows
        batch = response.json()

        # if no rows came back, we are done
        if not batch:
            logger.info("No more data to fetch.")
            break

        # add this batch to our full list
        all_data.extend(batch)
        logger.info(f"Fetched {len(all_data)} rows so far...")

        # if batch is less than 5000, this was the last page
        if len(batch) < limit:
            logger.info("Reached last page.")
            break

        # move to next page
        offset = offset + limit

    # convert full list to dataframe
    physician_data = pd.DataFrame(all_data)
    logger.info(f"Finished fetching. Total rows: {len(physician_data)}")
    logger.info(f"Columns in data: {list(physician_data.columns)}")

    return physician_data


def run():
    # step 1 - make sure bucket exists in RustFS
    ensure_bucket_exists()

    # step 2 - fetch the data from API
    physician_data = fetch_physician_data()

    # step 3 - check if we got any data
    if physician_data.empty:
        logger.warning("No data fetched. Stopping.")
        return

    # step 4 - build the file path inside RustFS
    # using today's date so each run saves separately
    today = date.today()
    s3_key = f"physician/{today}/physician_data.parquet"

    # step 5 - upload to RustFS
    upload_parquet_to_rustfs(physician_data, s3_key)
    logger.success("Physician data ingestion done!")


if __name__ == "__main__":
    run()