"""
database_init.py — Run this ONCE before anything else.
usage:
    uv run python -m  scripts.database_init
"""
import duckdb
from loguru import logger
from src.config import settings
 
# DuckDB path comes from .env → DUCKDB_PATH
DUCKDB_PATH = settings.duckdb_path
 
 
def get_connection():
    # connect to the persistent DuckDB file
    # it will be created automatically if it doesn't exist
    con = duckdb.connect(DUCKDB_PATH)
    return con
 
 
def create_schema(con):
    # create the raw schema if it doesn't exist
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    logger.info("Schema created: raw")
 
 
def create_inpatient_tables(con):
    # ── Final table ───────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.inpatient_hospitals (
            Rndrng_Prvdr_CCN        VARCHAR,
            Rndrng_Prvdr_Org_Name   VARCHAR,
            Rndrng_Prvdr_City       VARCHAR,
            Rndrng_Prvdr_St         VARCHAR,
            Rndrng_Prvdr_State_FIPS VARCHAR,
            Rndrng_Prvdr_Zip5       VARCHAR,
            Rndrng_Prvdr_State_Abrvtn VARCHAR,
            Rndrng_Prvdr_RUCA       VARCHAR,
            Rndrng_Prvdr_RUCA_Desc  VARCHAR,
            DRG_Cd                  VARCHAR,
            DRG_Desc                VARCHAR,
            Tot_Dschrgs             DOUBLE,
            Avg_Submtd_Cvrd_Chrg    DOUBLE,
            Avg_Tot_Pymt_Amt        DOUBLE,
            Avg_Mdcr_Pymt_Amt       DOUBLE,
 
            -- unique key: one row per hospital + DRG code combo
            PRIMARY KEY (Rndrng_Prvdr_CCN, DRG_Cd)
        );
    """)
    logger.info("Table created: raw.inpatient_hospitals")
 
    # ── Staging table (same structure, no primary key) ────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.stg_inpatient_hospitals (
            Rndrng_Prvdr_CCN        VARCHAR,
            Rndrng_Prvdr_Org_Name   VARCHAR,
            Rndrng_Prvdr_City       VARCHAR,
            Rndrng_Prvdr_St         VARCHAR,
            Rndrng_Prvdr_State_FIPS VARCHAR,
            Rndrng_Prvdr_Zip5       VARCHAR,
            Rndrng_Prvdr_State_Abrvtn VARCHAR,
            Rndrng_Prvdr_RUCA       VARCHAR,
            Rndrng_Prvdr_RUCA_Desc  VARCHAR,
            DRG_Cd                  VARCHAR,
            DRG_Desc                VARCHAR,
            Tot_Dschrgs             DOUBLE,
            Avg_Submtd_Cvrd_Chrg    DOUBLE,
            Avg_Tot_Pymt_Amt        DOUBLE,
            Avg_Mdcr_Pymt_Amt       DOUBLE
        );
    """)
    logger.info("Table created: raw.stg_inpatient_hospitals")
 
 
def create_physician_tables(con):
    # ── Final table ────
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.physician_data (
            Rndrng_NPI                      VARCHAR,
            Rndrng_Prvdr_Last_Org_Name      VARCHAR,
            Rndrng_Prvdr_First_Name         VARCHAR,
            Rndrng_Prvdr_MI                 VARCHAR,
            Rndrng_Prvdr_Crdntls            VARCHAR,
            Rndrng_Prvdr_Ent_Cd             VARCHAR,
            Rndrng_Prvdr_St1                VARCHAR,
            Rndrng_Prvdr_St2                VARCHAR,
            Rndrng_Prvdr_City               VARCHAR,
            Rndrng_Prvdr_State_Abrvtn       VARCHAR,
            Rndrng_Prvdr_State_FIPS         VARCHAR,
            Rndrng_Prvdr_Zip5               VARCHAR,
            Rndrng_Prvdr_RUCA               VARCHAR,
            Rndrng_Prvdr_RUCA_Desc          VARCHAR,
            Rndrng_Prvdr_Cntry              VARCHAR,
            Rndrng_Prvdr_Type               VARCHAR,
            Rndrng_Prvdr_Mdcr_Prtcptg_Ind  VARCHAR,
            HCPCS_Cd                        VARCHAR,
            HCPCS_Desc                      VARCHAR,
            HCPCS_Drug_Ind                  VARCHAR,
            Place_Of_Srvc                   VARCHAR,
            Tot_Benes                       DOUBLE,
            Tot_Srvcs                       DOUBLE,
            Tot_Bene_Day_Srvcs              DOUBLE,
            Avg_Sbmtd_Chrg                  DOUBLE,
            Avg_Mdcr_Alowd_Amt              DOUBLE,
            Avg_Mdcr_Pymt_Amt               DOUBLE,
            Avg_Mdcr_Stdzd_Amt              DOUBLE,
 
            -- unique key: one row per provider + service code + place of service
            PRIMARY KEY (Rndrng_NPI, HCPCS_Cd, Place_Of_Srvc)
        );
    """)
    logger.info("Table created: raw.physician_data")
 
    # ── Staging table (same structure, no primary key) ────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.stg_physician_data (
            Rndrng_NPI                      VARCHAR,
            Rndrng_Prvdr_Last_Org_Name      VARCHAR,
            Rndrng_Prvdr_First_Name         VARCHAR,
            Rndrng_Prvdr_MI                 VARCHAR,
            Rndrng_Prvdr_Crdntls            VARCHAR,
            Rndrng_Prvdr_Ent_Cd             VARCHAR,
            Rndrng_Prvdr_St1                VARCHAR,
            Rndrng_Prvdr_St2                VARCHAR,
            Rndrng_Prvdr_City               VARCHAR,
            Rndrng_Prvdr_State_Abrvtn       VARCHAR,
            Rndrng_Prvdr_State_FIPS         VARCHAR,
            Rndrng_Prvdr_Zip5               VARCHAR,
            Rndrng_Prvdr_RUCA               VARCHAR,
            Rndrng_Prvdr_RUCA_Desc          VARCHAR,
            Rndrng_Prvdr_Cntry              VARCHAR,
            Rndrng_Prvdr_Type               VARCHAR,
            Rndrng_Prvdr_Mdcr_Prtcptg_Ind  VARCHAR,
            HCPCS_Cd                        VARCHAR,
            HCPCS_Desc                      VARCHAR,
            HCPCS_Drug_Ind                  VARCHAR,
            Place_Of_Srvc                   VARCHAR,
            Tot_Benes                       DOUBLE,
            Tot_Srvcs                       DOUBLE,
            Tot_Bene_Day_Srvcs              DOUBLE,
            Avg_Sbmtd_Chrg                  DOUBLE,
            Avg_Mdcr_Alowd_Amt              DOUBLE,
            Avg_Mdcr_Pymt_Amt               DOUBLE,
            Avg_Mdcr_Stdzd_Amt              DOUBLE
        );
    """)
    logger.info("Table created: raw.stg_physician_data")
 
 
def create_npi_tables(con):
    # ── Final table ────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.npi_data (
            NPI                                                         VARCHAR,
            "Entity Type Code"                                          VARCHAR,
            "Provider Organization Name (Legal Business Name)"          VARCHAR,
            "Provider Last Name (Legal Name)"                           VARCHAR,
            "Provider First Name"                                       VARCHAR,
            "Provider Middle Name"                                      VARCHAR,
            "Provider Credential Text"                                  VARCHAR,
            "Provider Business Mailing Address Telephone Number"        VARCHAR,
            "Provider Business Practice Location Address City Name"     VARCHAR,
            "Provider Business Practice Location Address State Name"    VARCHAR,
            "Provider Business Practice Location Address Postal Code"   VARCHAR,
            "Provider Enumeration Date"                                 VARCHAR,
            "Last Update Date"                                          VARCHAR,
            "NPI Deactivation Date"                                     VARCHAR,
            "NPI Reactivation Date"                                     VARCHAR,
            "Provider Sex Code"                                         VARCHAR,
            "Healthcare Provider Taxonomy Code_1"                       VARCHAR,
            "Provider License Number_1"                                 VARCHAR,
            "Provider License Number State Code_1"                      VARCHAR,
            "Healthcare Provider Primary Taxonomy Switch_1"             VARCHAR,
            "Is Sole Proprietor"                                        VARCHAR,
            "Is Organization Subpart"                                   VARCHAR,
            "Certification Date"                                        VARCHAR,
 
            -- unique key: NPI is a unique national identifier
            PRIMARY KEY (NPI)
        );
    """)
    logger.info("Table created: raw.npi_data")
 
    # ── Staging table (same structure, no primary key) ────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.stg_npi_data (
            NPI                                                         VARCHAR,
            "Entity Type Code"                                          VARCHAR,
            "Provider Organization Name (Legal Business Name)"          VARCHAR,
            "Provider Last Name (Legal Name)"                           VARCHAR,
            "Provider First Name"                                       VARCHAR,
            "Provider Middle Name"                                      VARCHAR,
            "Provider Credential Text"                                  VARCHAR,
            "Provider Business Mailing Address Telephone Number"        VARCHAR,
            "Provider Business Practice Location Address City Name"     VARCHAR,
            "Provider Business Practice Location Address State Name"    VARCHAR,
            "Provider Business Practice Location Address Postal Code"   VARCHAR,
            "Provider Enumeration Date"                                 VARCHAR,
            "Last Update Date"                                          VARCHAR,
            "NPI Deactivation Date"                                     VARCHAR,
            "NPI Reactivation Date"                                     VARCHAR,
            "Provider Sex Code"                                         VARCHAR,
            "Healthcare Provider Taxonomy Code_1"                       VARCHAR,
            "Provider License Number_1"                                 VARCHAR,
            "Provider License Number State Code_1"                      VARCHAR,
            "Healthcare Provider Primary Taxonomy Switch_1"             VARCHAR,
            "Is Sole Proprietor"                                        VARCHAR,
            "Is Organization Subpart"                                   VARCHAR,
            "Certification Date"                                        VARCHAR
        );
    """)
    logger.info("Table created: raw.stg_npi_data")
 
 
def verify_tables(con):
    # print all tables created so we can confirm everything is there
    logger.info("=" * 50)
    logger.info("Verifying tables in raw schema...")
    result = con.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'raw'
        ORDER BY table_name;
    """).fetchall()
 
    for row in result:
        logger.info(f" raw.{row[0]}")
 
    logger.info(f"Total tables: {len(result)}")
 
 
def main():
    logger.info("Starting database initialization...")
    logger.info(f"DuckDB file: {DUCKDB_PATH}")
 
    con = get_connection()
 
    # step 1 - create raw schema
    create_schema(con)
 
    # step 2 - create inpatient tables
    create_inpatient_tables(con)
 
    # step 3 - create physician tables
    create_physician_tables(con)
 
    # step 4 - create npi tables
    create_npi_tables(con)
 
    # step 5 - verify everything was created
    verify_tables(con)
 
    con.close()
    logger.success("Database initialization complete!")
 
 
if __name__ == "__main__":
    main()