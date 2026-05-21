"""
medicare_pipeline.py — Full Medicare data pipeline DAG.

Pipeline flow:
    1. Upload to RustFS (3 tasks in parallel)
       - upload_inpatient
       - upload_physician
       - upload_npi
    2. Ingest to DuckDB (3 tasks in parallel, after all uploads complete)
       - ingest_inpatient
       - ingest_physician
       - ingest_npi
    3. dbt run (after all ingestions complete)

Schedule: Weekly on Sunday at midnight UTC
"""

import pendulum
from airflow.sdk import dag, task
from  datetime import timedelta


#  Upload to RustFS tasks 

@task(execution_timeout=timedelta(hours=6))
def upload_inpatient():
    from src.upload_to_rustfs.api1_inpatient_data import run
    run()


@task(execution_timeout=timedelta(hours=6))
def upload_physician():
    from src.upload_to_rustfs.api2_physician_data import run
    run()


@task
def upload_npi():
    from src.upload_to_rustfs.csv_loader import run
    run()


#  Ingest to DuckDB tasks 

@task
def ingest_inpatient():
    from src.ingestion.api1_inpatient_to_duckdb import main
    main()


@task
def ingest_physician():
    from src.ingestion.api2_physicians_to_duckdb import main
    main()


@task
def ingest_npi():
    from src.ingestion.csv_npi_to_duckdb import main
    main()


#  dbt run task 

@task.bash
def dbt_run():
    return (
        "dbt clean "
        "--project-dir /opt/airflow/workspace/medicare_dbt "
        "--profiles-dir /opt/airflow/workspace/medicare_dbt "
        "&& dbt run "
        "--project-dir /opt/airflow/workspace/medicare_dbt "
        "--profiles-dir /opt/airflow/workspace/medicare_dbt"
    )
#  Ducklake loader task 

@task
def load_ducklake():
    from lakehouse.ducklake_loader import main
    main()

#  DAG definition 

@dag(
    dag_id="medicare_pipeline",
    schedule="@weekly",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["medicare", "pipeline"],
    # retry failed tasks automatically
    default_args={
        "retries": 2,                                    # retry 2 times
        "retry_delay": pendulum.duration(minutes=5),
        "execution_timeout": pendulum.duration(hours=2),     # wait 5 mins between retries
    },
    doc_md="""
    ## Medicare Data Pipeline

    Full end-to-end pipeline that:
    1. Fetches fresh data from CMS APIs and NPI CSV → uploads to RustFS as Parquet
    2. Reads Parquet from RustFS → loads into DuckDB raw schema
    3. Runs dbt transformations → creates staging views and mart tables
    4. Loads Ducklake gold tables → serves Metabase and FastAPI
    **Schedule:** Weekly on Sunday at midnight UTC
    **Data Sources:** CMS Inpatient, CMS Physician, NPI Weekly CSV
    """
)
def medicare_pipeline():

    # step 1 — upload to RustFS (parallel)
    inpatient_upload = upload_inpatient()
    physician_upload = upload_physician()
    npi_upload = upload_npi()

    # step 2 — ingest to DuckDB (sequential — DuckDB one writer at a time)
    inpatient_ingest = ingest_inpatient()
    physician_ingest = ingest_physician()
    npi_ingest = ingest_npi()

    # step 3 — dbt run
    dbt = dbt_run()

    # step 4 — load Ducklake
    ducklake = load_ducklake()

    # uploads run in sequencially
    inpatient_upload >> physician_upload >> npi_upload

    # ingestion starts after all uploads complete, runs sequentially
    npi_upload >> inpatient_ingest
    inpatient_ingest >> physician_ingest
    physician_ingest >> npi_ingest

    # dbt runs after all ingestion complete
    npi_ingest >> dbt
    # ducklake loads after dbt completes
    dbt >> ducklake

medicare_pipeline()