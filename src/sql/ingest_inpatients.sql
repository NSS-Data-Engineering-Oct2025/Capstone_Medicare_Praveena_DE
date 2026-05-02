-- ingest_inpatients.sql
-- Merges data from staging into final inpatient_hospitals table
-- Unique key: Rndrng_Prvdr_CCN + DRG_Cd (one hospital + one procedure = one row)
 
MERGE INTO {FINAL_TABLE} AS target
USING {STAGE_TABLE} AS source
ON target.Rndrng_Prvdr_CCN = source.Rndrng_Prvdr_CCN
   AND target.DRG_Cd = source.DRG_Cd
 
WHEN MATCHED THEN UPDATE SET
    Rndrng_Prvdr_Org_Name     = source.Rndrng_Prvdr_Org_Name,
    Rndrng_Prvdr_City         = source.Rndrng_Prvdr_City,
    Rndrng_Prvdr_St           = source.Rndrng_Prvdr_St,
    Rndrng_Prvdr_State_FIPS   = source.Rndrng_Prvdr_State_FIPS,
    Rndrng_Prvdr_Zip5         = source.Rndrng_Prvdr_Zip5,
    Rndrng_Prvdr_State_Abrvtn = source.Rndrng_Prvdr_State_Abrvtn,
    Rndrng_Prvdr_RUCA         = source.Rndrng_Prvdr_RUCA,
    Rndrng_Prvdr_RUCA_Desc    = source.Rndrng_Prvdr_RUCA_Desc,
    DRG_Desc                  = source.DRG_Desc,
    Tot_Dschrgs               = source.Tot_Dschrgs,
    Avg_Submtd_Cvrd_Chrg      = source.Avg_Submtd_Cvrd_Chrg,
    Avg_Tot_Pymt_Amt          = source.Avg_Tot_Pymt_Amt,
    Avg_Mdcr_Pymt_Amt         = source.Avg_Mdcr_Pymt_Amt
 
WHEN NOT MATCHED THEN INSERT (
    Rndrng_Prvdr_CCN,
    Rndrng_Prvdr_Org_Name,
    Rndrng_Prvdr_City,
    Rndrng_Prvdr_St,
    Rndrng_Prvdr_State_FIPS,
    Rndrng_Prvdr_Zip5,
    Rndrng_Prvdr_State_Abrvtn,
    Rndrng_Prvdr_RUCA,
    Rndrng_Prvdr_RUCA_Desc,
    DRG_Cd,
    DRG_Desc,
    Tot_Dschrgs,
    Avg_Submtd_Cvrd_Chrg,
    Avg_Tot_Pymt_Amt,
    Avg_Mdcr_Pymt_Amt
) VALUES (
    source.Rndrng_Prvdr_CCN,
    source.Rndrng_Prvdr_Org_Name,
    source.Rndrng_Prvdr_City,
    source.Rndrng_Prvdr_St,
    source.Rndrng_Prvdr_State_FIPS,
    source.Rndrng_Prvdr_Zip5,
    source.Rndrng_Prvdr_State_Abrvtn,
    source.Rndrng_Prvdr_RUCA,
    source.Rndrng_Prvdr_RUCA_Desc,
    source.DRG_Cd,
    source.DRG_Desc,
    source.Tot_Dschrgs,
    source.Avg_Submtd_Cvrd_Chrg,
    source.Avg_Tot_Pymt_Amt,
    source.Avg_Mdcr_Pymt_Amt
);