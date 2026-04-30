import pandas as pd
from datetime import date
from loguru import logger
from src.ingestion.config import settings
from src.ingestion.utils import ensure_bucket_exists, upload_parquet_to_rustfs


# only load the columns we actually need
# ignoring the 300+ repeated identifier and taxonomy columns
USEFUL_COLUMNS = [
    "NPI",
    "Entity Type Code",
    "Provider Organization Name (Legal Business Name)",
    "Provider Last Name (Legal Name)",
    "Provider First Name",
    "Provider Middle Name",
    "Provider Credential Text",
    "Provider Business Practice Location Address City Name",
    "Provider Business Practice Location Address State Name",
    "Provider Business Practice Location Address Postal Code",
    "Provider Business Mailing Address Telephone Number",
    "Provider Sex Code",
    "Provider Enumeration Date",
    "Last Update Date",
    "NPI Deactivation Date",
    "NPI Reactivation Date",
    "Is Sole Proprietor",
    "Is Organization Subpart",
    "Healthcare Provider Taxonomy Code_1",
    "Provider License Number_1",
    "Provider License Number State Code_1",
    "Healthcare Provider Primary Taxonomy Switch_1",
    "Certification Date"
]


def load_npi_csv():
    # get csv path from .env via config
    csv_path = settings.npi_csv_path

    logger.info(f"Reading NPI CSV from {csv_path}...")

    # read only the columns we need
    # dtype=str keeps everything as string — avoids type issues with NPI numbers
    npi_data = pd.read_csv(
        csv_path,
        usecols=USEFUL_COLUMNS,
        dtype=str,
        low_memory=False
    )

    logger.info(f"Total rows loaded: {len(npi_data)}")
    logger.info(f"Columns loaded: {list(npi_data.columns)}")

    # drop rows where NPI is empty — NPI is our key field
    npi_data = npi_data.dropna(subset=["NPI"])
    logger.info(f"Rows after dropping empty NPI: {len(npi_data)}")

    return npi_data


def run():
    # step 1 - make sure bucket exists in RustFS
    ensure_bucket_exists()

    # step 2 - load the CSV file
    npi_data = load_npi_csv()

    # step 3 - check if we got any data
    if npi_data.empty:
        logger.warning("No data loaded. Stopping.")
        return

    # step 4 - build the file path inside RustFS
    today = date.today()
    s3_key = f"npi/{today}/npi_weekly.parquet"

    # step 5 - upload to RustFS as parquet
    upload_parquet_to_rustfs(npi_data, s3_key)
    logger.success("NPI CSV ingestion done!")


if __name__ == "__main__":
    run()