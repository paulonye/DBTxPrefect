{{ config(materialized='table') }}

WITH workspace AS (
  SELECT WORKSPACE_ID as workspace_id, 
          STRIPE_ID_HASH as stripe_id,
          member_id        
  FROM {{ ref('workspaces') }}
  CROSS JOIN UNNEST(SPLIT(MEMBERS, ',')) AS member_id),
payment AS (
  SELECT STRIPE_ID_HASH as stripe_id,
          PAYMENT_SOURCE_COUNTRY_CODE as country,
          PURCHASED_SEATS as seats_purchased,
          ARR_AMOUNT as arr_amount
  FROM {{ ref('stripe_arr') }}
),
features AS (
  SELECT WORKSPACE_ID as workspace_id, 
          COUNT(DISTINCT (FEATURE_KEY)) as number_of_features_used
  FROM {{ ref('workspaces_feature_usage_weekly') }} 
  GROUP BY WORKSPACE_ID
)
SELECT workspace.workspace_id,
        payment.stripe_id,
        payment.country,
        payment.seats_purchased,
        payment.arr_amount,
        COUNT(DISTINCT workspace.member_id) AS num_members,
        features.number_of_features_used,
        IF(payment.stripe_id IS NULL, 'Unpaid Subscription', 'Paid Subscription') AS payment_status
FROM workspace
LEFT JOIN payment
ON workspace.stripe_id = payment.stripe_id
LEFT JOIN features
ON workspace.workspace_id = features.workspace_id
GROUP BY workspace.workspace_id,
        payment.stripe_id,
        payment.country,
        payment.seats_purchased,
        payment.arr_amount,
        features.number_of_features_used
ORDER BY payment.arr_amount desc