select

    trim(Rndrng_NPI)                        as npi,
    trim(Rndrng_Prvdr_Last_Org_Name)        as provider_last_name,
    trim(Rndrng_Prvdr_First_Name)           as provider_first_name,
    trim(Rndrng_Prvdr_Crdntls)              as provider_credentials,
    trim(Rndrng_Prvdr_Type)                 as provider_type,
    trim(Rndrng_Prvdr_Mdcr_Prtcptg_Ind)     as medicare_participating,
    trim(Rndrng_Prvdr_City)                 as provider_city,
    upper(trim(Rndrng_Prvdr_State_Abrvtn))  as provider_state,
    trim(Rndrng_Prvdr_Zip5)                 as provider_zip,
    trim(Rndrng_Prvdr_Cntry)                as provider_country,
    trim(Rndrng_Prvdr_RUCA)                 as provider_ruca,
    trim(Rndrng_Prvdr_RUCA_Desc)            as provider_ruca_desc,
    trim(HCPCS_Cd)                          as hcpcs_code,
    trim(HCPCS_Desc)                        as hcpcs_desc,
    trim(HCPCS_Drug_Ind)                    as hcpcs_drug_indicator,
    trim(Place_Of_Srvc)                     as place_of_service,
    cast(Tot_Benes as integer)              as total_beneficiaries,
    cast(Tot_Srvcs as double)               as total_services,
    cast(Avg_Sbmtd_Chrg as double)          as avg_submitted_charge,
    cast(Avg_Mdcr_Alowd_Amt as double)      as avg_medicare_allowed_amount,
    cast(Avg_Mdcr_Pymt_Amt as double)       as avg_medicare_payment,
    cast(Avg_Mdcr_Stdzd_Amt as double)      as avg_medicare_standardized_amount
 
from {{ source('raw', 'physician_data') }}
 
where Rndrng_NPI is not null
  and HCPCS_Cd is not null
  and trim(Rndrng_Prvdr_RUCA_Desc) != 'Unknown'