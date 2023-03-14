{{ config(materialized='table') }}

WITH feat_desp AS (
    SELECT 
      FEATURE_KEY as feature_key,
      FEATURE_NAME as feature_name
    FROM {{ ref('dim_features') }} 
),
features AS (
    SELECT
      PARSE_DATE('%Y-%m-%d', WEEK) AS week,
      WORKSPACE_ID as workspace_id,
      FEATURE_KEY as feature_key,
      USERS_COUNT as users_count,
      EVENTS_COUNT as events_count
    FROM {{ ref('workspaces_feature_usage_weekly') }}    
)
SELECT features.week,
        feat_desp.feature_name,
        features.workspace_id,
        features.users_count,
        features.events_count
FROM features
JOIN feat_desp
ON features.feature_key = feat_desp.feature_key

