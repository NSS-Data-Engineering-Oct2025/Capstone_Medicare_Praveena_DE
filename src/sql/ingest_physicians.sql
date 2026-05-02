-- ingest_physicians.sql
-- Merges data from staging into final physician_data table
-- Unique key: Rndrng_NPI + HCPCS_Cd + Place_Of_Srvc
-- (one provider + one service code + one place of service = one row)

MERGE INTO {FINAL_TABLE} AS target
USING {STAGE_TABLE} AS source
ON target.Rndrng_NPI       = source.Rndrng_NPI
   AND target.HCPCS_Cd     = source.HCPCS_Cd
   AND target.Place_Of_Srvc = source.Place_Of_Srvc

WHEN MATCHED THEN UPDATE SET
    Rndrng_Prvdr_Last_Org_Name     = source.Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_First_Name        = source.Rndrng_Prvdr_First_Name,
    Rndrng_Prvdr_MI                = source.Rndrng_Prvdr_MI,
    Rndrng_Prvdr_Crdntls           = source.Rndrng_Prvdr_Crdntls,
    Rndrng_Prvdr_Ent_Cd            = source.Rndrng_Prvdr_Ent_Cd,
    Rndrng_Prvdr_St1               = source.Rndrng_Prvdr_St1,
    Rndrng_Prvdr_St2               = source.Rndrng_Prvdr_St2,
    Rndrng_Prvdr_City              = source.Rndrng_Prvdr_City,
    Rndrng_Prvdr_State_Abrvtn      = source.Rndrng_Prvdr_State_Abrvtn,
    Rndrng_Prvdr_State_FIPS        = source.Rndrng_Prvdr_State_FIPS,
    Rndrng_Prvdr_Zip5              = source.Rndrng_Prvdr_Zip5,
    Rndrng_Prvdr_RUCA              = source.Rndrng_Prvdr_RUCA,
    Rndrng_Prvdr_RUCA_Desc         = source.Rndrng_Prvdr_RUCA_Desc,
    Rndrng_Prvdr_Cntry             = source.Rndrng_Prvdr_Cntry,
    Rndrng_Prvdr_Type              = source.Rndrng_Prvdr_Type,
    Rndrng_Prvdr_Mdcr_Prtcptg_Ind  = source.Rndrng_Prvdr_Mdcr_Prtcptg_Ind,
    HCPCS_Desc                     = source.HCPCS_Desc,
    HCPCS_Drug_Ind                 = source.HCPCS_Drug_Ind,
    Tot_Benes                      = source.Tot_Benes,
    Tot_Srvcs                      = source.Tot_Srvcs,
    Tot_Bene_Day_Srvcs             = source.Tot_Bene_Day_Srvcs,
    Avg_Sbmtd_Chrg                 = source.Avg_Sbmtd_Chrg,
    Avg_Mdcr_Alowd_Amt             = source.Avg_Mdcr_Alowd_Amt,
    Avg_Mdcr_Pymt_Amt              = source.Avg_Mdcr_Pymt_Amt,
    Avg_Mdcr_Stdzd_Amt             = source.Avg_Mdcr_Stdzd_Amt

WHEN NOT MATCHED THEN INSERT (
    Rndrng_NPI,
    Rndrng_Prvdr_Last_Org_Name,
    Rndrng_Prvdr_First_Name,
    Rndrng_Prvdr_MI,
    Rndrng_Prvdr_Crdntls,
    Rndrng_Prvdr_Ent_Cd,
    Rndrng_Prvdr_St1,
    Rndrng_Prvdr_St2,
    Rndrng_Prvdr_City,
    Rndrng_Prvdr_State_Abrvtn,
    Rndrng_Prvdr_State_FIPS,
    Rndrng_Prvdr_Zip5,
    Rndrng_Prvdr_RUCA,
    Rndrng_Prvdr_RUCA_Desc,
    Rndrng_Prvdr_Cntry,
    Rndrng_Prvdr_Type,
    Rndrng_Prvdr_Mdcr_Prtcptg_Ind,
    HCPCS_Cd,
    HCPCS_Desc,
    HCPCS_Drug_Ind,
    Place_Of_Srvc,
    Tot_Benes,
    Tot_Srvcs,
    Tot_Bene_Day_Srvcs,
    Avg_Sbmtd_Chrg,
    Avg_Mdcr_Alowd_Amt,
    Avg_Mdcr_Pymt_Amt,
    Avg_Mdcr_Stdzd_Amt
) VALUES (
    source.Rndrng_NPI,
    source.Rndrng_Prvdr_Last_Org_Name,
    source.Rndrng_Prvdr_First_Name,
    source.Rndrng_Prvdr_MI,
    source.Rndrng_Prvdr_Crdntls,
    source.Rndrng_Prvdr_Ent_Cd,
    source.Rndrng_Prvdr_St1,
    source.Rndrng_Prvdr_St2,
    source.Rndrng_Prvdr_City,
    source.Rndrng_Prvdr_State_Abrvtn,
    source.Rndrng_Prvdr_State_FIPS,
    source.Rndrng_Prvdr_Zip5,
    source.Rndrng_Prvdr_RUCA,
    source.Rndrng_Prvdr_RUCA_Desc,
    source.Rndrng_Prvdr_Cntry,
    source.Rndrng_Prvdr_Type,
    source.Rndrng_Prvdr_Mdcr_Prtcptg_Ind,
    source.HCPCS_Cd,
    source.HCPCS_Desc,
    source.HCPCS_Drug_Ind,
    source.Place_Of_Srvc,
    source.Tot_Benes,
    source.Tot_Srvcs,
    source.Tot_Bene_Day_Srvcs,
    source.Avg_Sbmtd_Chrg,
    source.Avg_Mdcr_Alowd_Amt,
    source.Avg_Mdcr_Pymt_Amt,
    source.Avg_Mdcr_Stdzd_Amt
);