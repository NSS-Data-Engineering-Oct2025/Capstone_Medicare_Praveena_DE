import requests
import pandas as pd
from datetime import date
from loguru import logger
from src.config import settings
from src.utils import ensure_bucket_exists, upload_parquet_to_rustfs


def fetch_inpatient_data():
    # build the API url using dataset id from .env
    url = f"{settings.cms_api_base_url}/{settings.cms_inpatient_dataset_id}/data"

    all_data = []   # we will collect all rows here
    offset = 0      # starting point
    limit = 5000    # how many rows to fetch per request

    logger.info("Starting to fetch inpatient hospital data...")

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