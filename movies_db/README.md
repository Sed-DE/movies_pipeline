# movies_db (dbt)

dbt project that models IMDb and TMDB movie data in DuckDB.

## Scope

Only titles with more than 5,000 votes (`numVotes >= 5000`) are included. The filter is applied in `tmdb_get_id.py`, which only looks up TMDB IDs for IMDb titles that pass it. 

## Prerequisites

- Python environment managed with `uv` (`uv sync`)
- A TMDB API key exported as `API_KEY`:
```bash
  export API_KEY="your_tmdb_key"
```

## Layers

- **staging**: one model per raw table. Renames columns and casts types, nothing else.
- **intermediate**: joins necessary staging models together.
- **marts**: `fcts_movies` (budget, revenue, runtime, rating, votes), `dim_movie_details`, `dim_movie_images`.
- **reporting**: answers for specific questions, built on the fact and dims:
  - `most_popular_movies`: all movies ranked by number of votes
  - `most_popular_2026`: most popular movies of 2026
  - `highest_rated_2026`: highest rated movies of 2026
  - `biggest_budget_2026`: movies with the biggest budgets in 2026
  - `highest_revenue`: movies with the highest revenues

Marts are materialized as tables. Membership depends on the vote threshold and ratings change over time, so a full rebuild is simpler than incremental.

## Tests

`unique` and `not_null` on primary keys, `relationships` tests on the fact's foreign keys. Missing posters only raise a warning.

## Run it

```bash
uv sync
uv run dbt build
```

## profiles.yml

Lives in `~/.dbt/profiles.yml`, not in the repo:

```yaml
movies_db:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../movies_project.duckdb
      schema: dev
      threads: 1
      settings:
        memory_limit: '2.5GB' #feel free to increase or decrease depending on your machine
```

Raw tables are read from the `prod` schema (see `models/staging/sources.yml`).