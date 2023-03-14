{{ config(materialized='table') }}

SELECT
  DATE(CREATED_AT) AS date_column,
  USER_ID as user_id,
  IS_GMAIL_DOMAIN as gmail_domain,
  SALESFORCE_LAST_SYNCED_AT as salesforce_sync
FROM {{ ref('users') }} 