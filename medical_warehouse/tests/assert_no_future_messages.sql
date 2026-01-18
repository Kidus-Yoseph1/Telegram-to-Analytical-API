-- This test ensures all messages have a date that is not in the future.
-- If it returns rows, it means there is a data quality issue.

select
    message_id,
    message_timestamp
from {{ ref('stg_telegram_messages') }}
where message_timestamp > current_timestamp
