import boto3
import pandas as pd
from io import BytesIO
from botocore.client import Config
from loguru import logger
from src.config import settings
 
 
def get_rustfs_client():
    # same connection as utils.py
    client = boto3.client(
        "s3",
        endpoint_url=settings.rustfs_endpoint,
        aws_access_key_id=settings.rustfs_access_key,
        aws_secret_access_key=settings.rustfs_secret_key,
        config=Config(signature_version="s3v4")
    )
    return client
 
 
def get_latest_parquet(client, prefix):
    # list all files under this prefix and get the most recent one
    response = client.list_objects_v2(
        Bucket=settings.rustfs_bucket,
        Prefix=prefix
    )
 
    if "Contents" not in response:
        logger.warning(f"No files found under prefix: {prefix}")
        return None
 
    # sort by last modified and pick the latest file
    files = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)
    latest_key = files[0]["Key"]
    logger.info(f"Latest file found: {latest_key}")
    return latest_key
 
 
def read_parquet_from_rustfs(client, s3_key):
    # download the parquet file into memory and read it
    response = client.get_object(
        Bucket=settings.rustfs_bucket,
        Key=s3_key
    )
    buffer = BytesIO(response["Body"].read())
    data = pd.read_parquet(buffer)
    return data
 
 
def inspect(client, dataset_name, prefix):
    logger.info("=" * 60)
    logger.info(f"  Dataset: {dataset_name}")
    logger.info("=" * 60)
 
    s3_key = get_latest_parquet(client, prefix)
    if s3_key is None:
        return
 
    # only read first 5 rows — we just need column names
    dataset = read_parquet_from_rustfs(client, s3_key)
    sample = dataset.head(5)
 
    logger.info(f"Total columns : {len(dataset.columns)}")
    logger.info(f"Total rows    : {len(dataset)}")
    logger.info("")
    logger.info("Column names:")
    for i, col in enumerate(dataset.columns, 1):
        logger.info(f"  {i:>3}. {col}")
 
    logger.info("")
    logger.info("Sample (first 2 rows):")
    print(sample.head(2).to_string())
    logger.info("")
 
 
def main():
    client = get_rustfs_client()
 
    # inspect all 3 datasets
    inspect(client, "Inpatient",  "inpatient/")
    inspect(client, "Physician",  "physician/")
    inspect(client, "NPI",        "npi/")
 
 
if __name__ == "__main__":
    main()