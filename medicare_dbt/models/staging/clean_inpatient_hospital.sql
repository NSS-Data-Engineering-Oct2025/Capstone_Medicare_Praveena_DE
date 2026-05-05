select

    trim(Rndrng_Prvdr_CCN)                  as provider_ccn,
    trim(Rndrng_Prvdr_Org_Name)             as provider_name,
    trim(Rndrng_Prvdr_City)                 as provider_city,
    trim(Rndrng_Prvdr_St)                   as provider_street,
    upper(trim(Rndrng_Prvdr_State_Abrvtn))  as provider_state,

    trim(Rndrng_Prvdr_Zip5)                 as provider_zip,
    trim(Rndrng_Prvdr_RUCA)                 as provider_ruca,
    trim(Rndrng_Prvdr_RUCA_Desc)            as provider_ruca_desc,
    trim(DRG_Cd)                            as drg_code,
    trim(DRG_Desc)                          as drg_desc,
    cast(Tot_Dschrgs as integer)            as total_discharges,
    cast(Avg_Submtd_Cvrd_Chrg as double)    as avg_submitted_charge,
    cast(Avg_Tot_Pymt_Amt as double)        as avg_total_payment,
    cast(Avg_Mdcr_Pymt_Amt as double)       as avg_medicare_payment
 
from {{ source('raw', 'inpatient_hospitals') }}
 
where Rndrng_Prvdr_CCN is not null
  and DRG_Cd is not null
  and trim(Rndrng_Prvdr_RUCA_Desc) != 'Unknown'