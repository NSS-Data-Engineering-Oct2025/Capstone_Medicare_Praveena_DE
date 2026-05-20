select

    trim(NPI)                                                               as npi,
    trim("Entity Type Code")                                                as entity_type_code,
    upper(trim("Provider Last Name (Legal Name)"))                          as provider_last_name,
    upper(trim("Provider First Name"))                                      as provider_first_name,
    trim("Provider Credential Text")                                        as provider_credentials,
    trim("Provider Sex Code")                                               as provider_sex,
    upper(trim("Provider Business Practice Location Address City Name"))    as provider_city,
    upper(trim("Provider Business Practice Location Address State Name"))   as provider_state,
    trim("Provider Business Practice Location Address Postal Code")         as provider_zip,
    trim("Healthcare Provider Taxonomy Code_1")                             as taxonomy_code,
    trim("Last Update Date")                                                as last_update_date,
    trim("NPI Deactivation Date")                                           as deactivation_date,
    trim("NPI Reactivation Date")                                           as reactivation_date
 
from {{ source('raw', 'npi_data') }}
 
where NPI is not null