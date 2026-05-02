-- ingest_npi.sql
-- Merges data from staging into final npi_data table
-- Unique key: NPI (National Provider Identifier — always unique per provider)

MERGE INTO {FINAL_TABLE} AS target
USING {STAGE_TABLE} AS source
ON target.NPI = source.NPI

WHEN MATCHED THEN UPDATE SET
    "Entity Type Code"                                        = source."Entity Type Code",
    "Provider Organization Name (Legal Business Name)"        = source."Provider Organization Name (Legal Business Name)",
    "Provider Last Name (Legal Name)"                         = source."Provider Last Name (Legal Name)",
    "Provider First Name"                                     = source."Provider First Name",
    "Provider Middle Name"                                    = source."Provider Middle Name",
    "Provider Credential Text"                                = source."Provider Credential Text",
    "Provider Business Mailing Address Telephone Number"      = source."Provider Business Mailing Address Telephone Number",
    "Provider Business Practice Location Address City Name"   = source."Provider Business Practice Location Address City Name",
    "Provider Business Practice Location Address State Name"  = source."Provider Business Practice Location Address State Name",
    "Provider Business Practice Location Address Postal Code" = source."Provider Business Practice Location Address Postal Code",
    "Provider Enumeration Date"                               = source."Provider Enumeration Date",
    "Last Update Date"                                        = source."Last Update Date",
    "NPI Deactivation Date"                                   = source."NPI Deactivation Date",
    "NPI Reactivation Date"                                   = source."NPI Reactivation Date",
    "Provider Sex Code"                                       = source."Provider Sex Code",
    "Healthcare Provider Taxonomy Code_1"                     = source."Healthcare Provider Taxonomy Code_1",
    "Provider License Number_1"                               = source."Provider License Number_1",
    "Provider License Number State Code_1"                    = source."Provider License Number State Code_1",
    "Healthcare Provider Primary Taxonomy Switch_1"           = source."Healthcare Provider Primary Taxonomy Switch_1",
    "Is Sole Proprietor"                                      = source."Is Sole Proprietor",
    "Is Organization Subpart"                                 = source."Is Organization Subpart",
    "Certification Date"                                      = source."Certification Date"

WHEN NOT MATCHED THEN INSERT (
    NPI,
    "Entity Type Code",
    "Provider Organization Name (Legal Business Name)",
    "Provider Last Name (Legal Name)",
    "Provider First Name",
    "Provider Middle Name",
    "Provider Credential Text",
    "Provider Business Mailing Address Telephone Number",
    "Provider Business Practice Location Address City Name",
    "Provider Business Practice Location Address State Name",
    "Provider Business Practice Location Address Postal Code",
    "Provider Enumeration Date",
    "Last Update Date",
    "NPI Deactivation Date",
    "NPI Reactivation Date",
    "Provider Sex Code",
    "Healthcare Provider Taxonomy Code_1",
    "Provider License Number_1",
    "Provider License Number State Code_1",
    "Healthcare Provider Primary Taxonomy Switch_1",
    "Is Sole Proprietor",
    "Is Organization Subpart",
    "Certification Date"
) VALUES (
    source.NPI,
    source."Entity Type Code",
    source."Provider Organization Name (Legal Business Name)",
    source."Provider Last Name (Legal Name)",
    source."Provider First Name",
    source."Provider Middle Name",
    source."Provider Credential Text",
    source."Provider Business Mailing Address Telephone Number",
    source."Provider Business Practice Location Address City Name",
    source."Provider Business Practice Location Address State Name",
    source."Provider Business Practice Location Address Postal Code",
    source."Provider Enumeration Date",
    source."Last Update Date",
    source."NPI Deactivation Date",
    source."NPI Reactivation Date",
    source."Provider Sex Code",
    source."Healthcare Provider Taxonomy Code_1",
    source."Provider License Number_1",
    source."Provider License Number State Code_1",
    source."Healthcare Provider Primary Taxonomy Switch_1",
    source."Is Sole Proprietor",
    source."Is Organization Subpart",
    source."Certification Date"
);