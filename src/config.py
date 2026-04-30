from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # RustFS settings
    rustfs_endpoint: str
    rustfs_access_key: str
    rustfs_secret_key: str
    rustfs_bucket: str

    # CMS API settings
    cms_api_base_url: str
    cms_inpatient_dataset_id: str
    cms_physician_dataset_id: str

    # NPI CSV
    npi_csv_path: str
    
    # DuckDB
    duckdb_path: str

    class Config:
        env_file = ".env"


# create one settings object, import this everywhere
settings = Settings()