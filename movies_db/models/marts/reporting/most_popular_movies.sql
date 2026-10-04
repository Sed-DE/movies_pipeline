--Most popular movies 

select 
  d.primary_title,
  d.overview,
  d.year_of_release,
  f.budget,
  f.revenue,
  rank() over(order by num_of_votes desc) as rank_votes,
  f.runtime_in_minutes,
  f.avg_rating,
  f.num_of_votes,
  d.genres

from {{ ref('fcts_movies') }} as f
left join {{ ref('dim_movie_details') }} as d
on f.title_id = d.title_id
