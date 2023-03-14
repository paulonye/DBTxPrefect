{{ config(materialized='view') }}

select *
from {{ source('staging', 'plan_feature_definitions_table') }}


