{{ config(materialized='view') }}

select *
from {{ source('staging', 'dim_features_table') }}


