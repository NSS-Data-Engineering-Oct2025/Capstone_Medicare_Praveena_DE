from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # RustFS settings
    rustfs_endpoint: str
    airflow_rustfs_endpoint: str
    rustfs_access_key: str
    rustfs_secret_key: str
    rustfs_bucket: str

    # CMS API settings
    cms_api_base_url: str
    cms_inpatient_dataset_id: str
    cms_physician_dataset_id: str
    

    # NPI CSV
    npi_csv_path: str
    airflow_npi_csv_path: str
    
    # DuckDB
    duckdb_path: str
    airflow_duckdb_path: str

    # DuckDB table names — inpatient
    inpatient_final_table: str
    inpatient_stage_table: str

    # DuckDB table names — physician
    physician_final_table: str
    physician_stage_table: str

    # DuckDB table names — NPI
    npi_final_table: str
    npi_stage_table: str
    
    # Ducklake local paths
    ducklake_catalog_path: str
    ducklake_data_path: str
    

    # Physician API row limit
    physician_max_rows: int = 500000
    class Config:
        env_file = ".env"


# create one settings object, import this everywhere
settings = Settings()