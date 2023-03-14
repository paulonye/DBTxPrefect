{{ config(materialized='view') }}

select *
from {{ source('staging', 'users_table') }}


