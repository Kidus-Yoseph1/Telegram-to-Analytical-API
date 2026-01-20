{{ config(materialized='table') }}

with messages as (
    select * from {{ ref('stg_telegram_messages') }}
),
channels as (
    select * from {{ ref('dim_channels') }}
)

select
    m.message_id,
    c.channel_key, -- Link to dim_channels
    cast(to_char(m.message_timestamp, 'YYYYMMDD') as integer) as date_key, -- Link to dim_dates
    m.message_text,
    m.message_length,
    m.view_count,
    m.forward_count,
    m.has_image,
    m.media_path 
from messages m
left join channels c on m.channel_name = c.channel_name
