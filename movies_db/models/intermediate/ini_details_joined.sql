
select
  d.tmdb_id,
  t.imdb_id,
  d.original_title,
  d.overview

from {{ ref('stg_tmdb_movie_details') }} as d 
left join {{ ref('stg_tmdb_ids') }} as t
on d.tmdb_id = t.tmdb_id