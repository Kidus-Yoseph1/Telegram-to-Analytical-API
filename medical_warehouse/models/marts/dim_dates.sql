with date_series as (
    -- Generates a list of dates from 2023 to 2026
    select generate_series(
        '2020-01-01'::date, 
        '2026-12-31'::date, 
        '1 day'::interval
    )::date as full_date
)
select
    -- date_key in YYYYMMDD format (standard practice)
    cast(to_char(full_date, 'YYYYMMDD') as integer) as date_key,
    full_date,
    extract(dow from full_date) as day_of_week,
    to_char(full_date, 'Day') as day_name,
    extract(week from full_date) as week_of_year,
    extract(month from full_date) as month,
    to_char(full_date, 'Month') as month_name,
    extract(quarter from full_date) as quarter,
    extract(year from full_date) as year,
    case when extract(isodow from full_date) in (6, 7) then true else false end as is_weekend
from date_series
