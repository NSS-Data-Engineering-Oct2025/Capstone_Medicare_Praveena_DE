import boto3
import pandas as pd
from io import BytesIO
from loguru import logger
from botocore.client import Config
from src.ingestion.config import settings


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


def ensure_bucket_exists():
    # create the bucket in RustFS if it doesn't exist yet
    client = get_rustfs_client()

    # get list of existing buckets
    response = client.list_buckets()
    bucket_names = [b["Name"] for b in response["Buckets"]]

    if settings.rustfs_bucket not in bucket_names:
        client.create_bucket(Bucket=settings.rustfs_bucket)
        logger.info(f"Bucket created: {settings.rustfs_bucket}")
    else:
        logger.info(f"Bucket already exists: {settings.rustfs_bucket}")


def upload_parquet_to_rustfs(data, s3_key):
    # convert dataframe to parquet and upload to RustFS
    client = get_rustfs_client()

    # write dataframe to a memory buffer as parquet
    buffer = BytesIO()
    data.to_parquet(buffer, index=False)
    buffer.seek(0)

    # upload the buffer to RustFS
    client.put_object(
        Bucket=settings.rustfs_bucket,
        Key=s3_key,
        Body=buffer.getvalue()
    )

    logger.info(f"Uploaded to RustFS: {s3_key}")
    logger.info(f"Total rows uploaded: {len(data)}")