
with title_movie_basics as ( 
  select 
  *
  from {{ ref('stg_title_basics') }}
  where title_type = 'movie'
),

movie_details as (
  select 
    d.imdb_id as title_id,
    d.tmdb_id,
    b.primary_title,
    d.overview,
    b.original_title,
    b.is_adult_title,
    b.year_of_release,
    b.genres

  from {{ ref('ini_details_joined') }} as d
  left join title_movie_basics as b
  on d.imdb_id = b.title_id

)

select * from movie_details
