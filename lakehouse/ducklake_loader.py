"""
ducklake_loader.py — Loads dbt mart tables into Ducklake gold layer.

Follows trainer's pattern:
    1. Connect to DuckDB (read marts)
    2. Connect to Ducklake
    3. Create gold tables
    4. Insert data from dbt marts
    5. Verify snapshots

Usage:
    uv run python -m lakehouse.ducklake_loader
"""

import duckdb
from loguru import logger
from src.config import settings
from src.utils import get_duckdb_path, get_ducklake_catalog_path, get_ducklake_data_path


def main():
    logger.info("Starting Ducklake loader...")

    #  step 1: read mart data from DuckDB 
    duckdb_path = get_duckdb_path()
    logger.info(f"Reading from DuckDB: {duckdb_path}")
    duckdb_con = duckdb.connect(duckdb_path, read_only=True)

    inpatient_df = duckdb_con.execute("""
        SELECT
            provider_ccn,
            provider_name,
            provider_city,
            provider_state,
            provider_zip,
            provider_ruca,
            provider_ruca_desc,
            drg_code,
            drg_desc,
            total_discharges,
            avg_submitted_charge,
            avg_total_payment,
            avg_medicare_payment,
            payment_gap,
            medicare_coverage_pct
        FROM marts.mart_inpatient
    """).df()
    logger.info(f"Read {len(inpatient_df):,} rows from mart_inpatient")

    physician_df = duckdb_con.execute("""
        SELECT
            npi,
            provider_last_name,
            provider_first_name,
            provider_credentials,
            provider_type,
            medicare_participating,
            provider_sex,
            taxonomy_code,
            provider_city,
            provider_state,
            provider_zip,
            provider_country,
            provider_ruca,
            provider_ruca_desc,
            hcpcs_code,
            hcpcs_desc,
            hcpcs_drug_indicator,
            place_of_service,
            total_beneficiaries,
            total_services,
            avg_submitted_charge,
            avg_medicare_allowed_amount,
            avg_medicare_payment,
            avg_medicare_standardized_amount,
            payment_gap,
            medicare_coverage_pct
        FROM marts.mart_physician
    """).df()
    logger.info(f"Read {len(physician_df):,} rows from mart_physician")

    duckdb_con.close()

    #  step 2: connect to Ducklake 
    catalog_path = get_ducklake_catalog_path()
    data_path = get_ducklake_data_path()
    logger.info(f"Connecting to Ducklake: {catalog_path}")
    con = duckdb.connect()
    con.execute("INSTALL ducklake;")
    con.execute("LOAD ducklake;")

    con.execute(f"""
        ATTACH 'ducklake:{catalog_path}' AS lake (
            DATA_PATH '{data_path}',
            DATA_INLINING_ROW_LIMIT 0,
            OVERRIDE_DATA_PATH TRUE
        );
    """)
    con.execute("USE lake;")
    logger.info("Ducklake connection ready")

    #  step 3: create gold tables 
    con.execute("""
        CREATE TABLE IF NOT EXISTS gold_inpatient (
            provider_ccn          VARCHAR,
            provider_name         VARCHAR,
            provider_city         VARCHAR,
            provider_state        VARCHAR,
            provider_zip          VARCHAR,
            provider_ruca         VARCHAR,
            provider_ruca_desc    VARCHAR,
            drg_code              VARCHAR,
            drg_desc              VARCHAR,
            total_discharges      INTEGER,
            avg_submitted_charge  DOUBLE,
            avg_total_payment     DOUBLE,
            avg_medicare_payment  DOUBLE,
            payment_gap           DOUBLE,
            medicare_coverage_pct DOUBLE
        );
    """)
    logger.info("Table ready: gold_inpatient")

    con.execute("""
        CREATE TABLE IF NOT EXISTS gold_physician (
            npi                              VARCHAR,
            provider_last_name               VARCHAR,
            provider_first_name              VARCHAR,
            provider_credentials             VARCHAR,
            provider_type                    VARCHAR,
            medicare_participating           VARCHAR,
            provider_sex                     VARCHAR,
            taxonomy_code                    VARCHAR,
            provider_city                    VARCHAR,
            provider_state                   VARCHAR,
            provider_zip                     VARCHAR,
            provider_country                 VARCHAR,
            provider_ruca                    VARCHAR,
            provider_ruca_desc               VARCHAR,
            hcpcs_code                       VARCHAR,
            hcpcs_desc                       VARCHAR,
            hcpcs_drug_indicator             VARCHAR,
            place_of_service                 VARCHAR,
            total_beneficiaries              INTEGER,
            total_services                   DOUBLE,
            avg_submitted_charge             DOUBLE,
            avg_medicare_allowed_amount      DOUBLE,
            avg_medicare_payment             DOUBLE,
            avg_medicare_standardized_amount DOUBLE,
            payment_gap                      DOUBLE,
            medicare_coverage_pct            DOUBLE
        );
    """)
    logger.info("Table ready: gold_physician")

    #  step 4: load data into Ducklake 
    # MERGE creates 1 snapshot per run (vs DELETE+INSERT which creates 2)
    # WHEN MATCHED → update existing rows
    # WHEN NOT MATCHED → insert new rows
 
    logger.info("Merging gold_inpatient...")
    con.execute("""
        MERGE INTO gold_inpatient AS target
        USING inpatient_df AS source
        ON target.provider_ccn = source.provider_ccn
           AND target.drg_code = source.drg_code
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
    count = con.execute("SELECT COUNT(*) FROM gold_inpatient").fetchone()[0]
    logger.success(f"gold_inpatient merged — {count:,} rows")
 
    logger.info("Merging gold_physician...")
    con.execute("""
        MERGE INTO gold_physician AS target
        USING physician_df AS source
        ON target.npi = source.npi
           AND target.hcpcs_code = source.hcpcs_code
           AND target.place_of_service = source.place_of_service
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
    count = con.execute("SELECT COUNT(*) FROM gold_physician").fetchone()[0]
    logger.success(f"gold_physician merged — {count:,} rows")

    #  step 5: verify snapshots 
    logger.info("\nDucklake Snapshots:")
    for row in con.execute("""
        SELECT snapshot_id,
               snapshot_time::VARCHAR AS snapshot_time,
               schema_version,
               changes
        FROM ducklake_snapshots('lake');
    """).fetchall():
        logger.info(" ", row)

    logger.info("\nRows in gold_inpatient:")
    count = con.execute("SELECT COUNT(*) FROM gold_inpatient").fetchone()[0]
    logger.info(f"  {count:,} rows")

    logger.info("\nRows in gold_physician:")
    count = con.execute("SELECT COUNT(*) FROM gold_physician").fetchone()[0]
    logger.info(f"  {count:,} rows")

    con.close()
    logger.success("Ducklake loader complete!")


if __name__ == "__main__":
    main()