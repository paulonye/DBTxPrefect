{{ config(materialized='view') }}

select *
from {{ source('staging', 'workspaces_table') }}


