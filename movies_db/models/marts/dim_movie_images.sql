
select 
  tmdb_id,
  movie_poster

from {{ ref('stg_tmdb_movie_details') }}


