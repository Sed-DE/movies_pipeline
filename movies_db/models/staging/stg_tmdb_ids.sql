
select
  imdb_id as imdb_id,
  tmdb_id as tmdb_id

from {{ source('source_data', 'tmdb_ids') }}