--List of the most popular movies this year 2026

select 
  d.primary_title,
  d.overview,
  d.year_of_release,
  f.runtime_in_minutes,
  f.avg_rating,
  f.num_of_votes,
  rank() over (order by num_of_votes desc) as rank_num_of_votes,
  d.genres,
  i.movie_poster

from {{ ref('fcts_movies') }} as f
left join {{ ref('dim_movie_details') }} as d
on f.title_id = d.title_id
left join {{ ref('dim_movie_images') }} as i
on f.tmdb_id = i.tmdb_id
where d.year_of_release = 2026