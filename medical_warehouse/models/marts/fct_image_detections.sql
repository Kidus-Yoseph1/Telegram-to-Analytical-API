{{ config(materialized='table') }}

WITH raw_yolo AS (
    SELECT * FROM {{ ref('enriched_detection_objects') }}
),

message_lookup AS (
    SELECT 
        message_id, 
        channel_key, 
        date_key, 
        media_path 
    FROM {{ ref('fct_messages') }}
    -- Filter out rows that don't have images to make the join faster
    WHERE media_path IS NOT NULL 
)

SELECT 
    m.message_id,
    m.channel_key,
    m.date_key,
    y.image_path,
    y.detected_objects,
    y.max_confidence,
    y.image_category
FROM raw_yolo y
LEFT JOIN message_lookup m 
  ON y.image_path = m.media_path
