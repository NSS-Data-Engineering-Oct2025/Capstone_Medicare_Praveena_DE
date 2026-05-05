select

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
    -- payment gap: difference between submitted and medicare payment
    round(avg_submitted_charge - avg_medicare_payment, 2)                   as payment_gap,
 
    -- medicare coverage rate: what % of submitted charge does medicare pay
    round(avg_medicare_payment / nullif(avg_submitted_charge, 0) * 100, 2)  as medicare_coverage_pct
 
from {{ ref('clean_inpatient_hospital') }}