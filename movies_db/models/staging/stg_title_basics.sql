
select 
  tconst as title_id,
  titleType as title_type,
  primaryTitle as primary_title,
  originalTitle as original_title,
  isAdult as is_adult_title,
  startYear as year_of_release,
  endYear as end_year,
  cast(runtimeMinutes as INT) as runtime_in_minutes,
  genres as genres

from {{ source('source_data', 'title_basics') }}
