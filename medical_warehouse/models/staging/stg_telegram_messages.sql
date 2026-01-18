with raw_messages as (
    select * from {{ source('raw_data_source', 'telegram_messages') }}
)

select
    -- Rename columns to consistent naming conventions
    cast(msg_id as bigint) as message_id,
    cast(channel as text) as channel_name,
    
    -- Cast data types appropriately
    cast(date as timestamp) as message_timestamp,
    
    -- Clean messy text (Standardize nulls to empty strings)
    coalesce(text, '') as message_text,
    
    -- Cast integers for metrics
    cast(views as integer) as view_count,
    cast(forwards as integer) as forward_count,
    
    -- Add calculated fields
    length(text) as message_length,
    case 
        when media_path is not null then true 
        else false 
    end as has_image,
    
    media_path

from raw_messages
-- Remove or filter invalid records
where msg_id is not null 
  and date is not null
