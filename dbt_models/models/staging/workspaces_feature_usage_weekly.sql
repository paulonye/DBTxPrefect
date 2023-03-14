{{ config(materialized='view') }}

select *
from {{ source('staging', 'workspaces_feature_usage_weekly_table') }}


