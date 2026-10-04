--Movies in 2026 with the biggest budget
select 
  d.primary_title,
  d.overview,
  d.year_of_release,
  f.budget,
  f.revenue,
  rank() over(order by budget desc) as rank_budget,
  f.runtime_in_minutes,
  f.avg_rating,
  f.num_of_votes,
  d.genres

from {{ ref('fcts_movies') }} as f
left join {{ ref('dim_movie_details') }} as d
on f.title_id = d.title_id
where d.year_of_release = 2026