{{ config(materialized='view') }}

select *
from {{ source('staging', 'prepaid_account_table') }}


