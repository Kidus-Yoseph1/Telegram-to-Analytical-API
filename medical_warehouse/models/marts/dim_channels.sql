with channel_metrics as (
    select
        channel_name,
        min(message_timestamp) as first_post_date,
        max(message_timestamp) as last_post_date,
        count(message_id) as total_posts,
        avg(view_count) as avg_views
    from {{ ref('stg_telegram_messages') }}
    group by 1
)
select
    -- Surrogate Key: A unique ID for the channel
    md5(channel_name) as channel_key,
    channel_name,
    case 
        when channel_name = 'CheMed123' then 'Medical'
        when channel_name = 'lobelia4cosmetics' then 'Cosmetics'
        when channel_name = 'tikvahpharma' then 'Pharmaceutical'
        else 'Unknown'
    end as channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
from channel_metrics
