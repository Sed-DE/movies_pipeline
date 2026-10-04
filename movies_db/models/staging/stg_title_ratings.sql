
select
  tconst as title_id,
  averageRating as avg_rating,
  cast(numVotes as INT) as num_of_votes

from {{ source('source_data', 'title_ratings') }}