{{ config(materialized='view') }}

select *
from {{ source('staging', 'stripe_arr_table') }}


