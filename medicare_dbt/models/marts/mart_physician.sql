select

    p.npi,
    p.provider_last_name,
    p.provider_first_name,
    p.provider_credentials,
    p.provider_type,
    p.medicare_participating,
    n.provider_sex,
    n.taxonomy_code,
    n.entity_type_code,
    n.deactivation_date,
    n.reactivation_date,
    n.last_update_date,
    p.provider_city,
    p.provider_state,
    p.provider_zip,
    p.provider_country,
    p.provider_ruca,
    p.provider_ruca_desc,
    p.hcpcs_code,
    p.hcpcs_desc,
    p.hcpcs_drug_indicator,
    p.place_of_service,
    p.total_beneficiaries,
    p.total_services,
    p.avg_submitted_charge,
    p.avg_medicare_allowed_amount,
    p.avg_medicare_payment,
    p.avg_medicare_standardized_amount,
    -- payment gap: difference between submitted and medicare payment
    round(p.avg_submitted_charge - p.avg_medicare_payment, 2)                   as payment_gap,
 
    -- medicare coverage rate: what % of submitted charge does medicare pay
    round(p.avg_medicare_payment / nullif(p.avg_submitted_charge, 0) * 100, 2)  as medicare_coverage_pct
 
from {{ ref('clean_physician_data') }} p
left join {{ ref('clean_npi_data') }} n
    on p.npi = n.npi