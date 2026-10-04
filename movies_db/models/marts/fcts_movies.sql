
select
  md.tmdb_id,
  tm.imdb_id as title_id,
  md.budget,
  md.revenue,
  md.runtime_in_minutes,
  r.avg_rating,
  r.num_of_votes

from {{ ref('stg_tmdb_movie_details') }} as md
left join {{ ref('stg_tmdb_ids') }} as tm
on md.tmdb_id = tm.tmdb_id
left join {{ ref('stg_title_ratings') }} as r 
on tm.imdb_id = r.title_id