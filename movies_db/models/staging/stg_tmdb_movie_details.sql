
select
  tmdb_id as tmdb_id,
  budget as budget,
  overview as overview,
  image_link as movie_poster,
  revenue as revenue,
  original_title as original_title,
  runtime as runtime_in_minutes

from {{ source('source_data', 'tmdb_movie_details') }}