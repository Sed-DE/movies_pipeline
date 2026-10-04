import duckdb

con = duckdb.connect("movies_db/movies_project.duckdb")

print("Connected. Creating table now...")
con.execute("CREATE SCHEMA IF NOT EXISTS prod")
con.execute("""
    CREATE OR REPLACE TABLE prod.tmdb_movie_details AS
    SELECT tmdb_id, budget, overview, concat('https://image.tmdb.org/t/p/w500', poster_path) as image_link, revenue, original_title, runtime
    FROM read_json(
        'tmdb_details.jsonl',
        format = 'newline_delimited',
        columns = {tmdb_id: 'INT', budget: 'INT', overview: 'VARCHAR', poster_path: 'VARCHAR', revenue: 'INT', original_title: 'VARCHAR', runtime: 'INT'},
        ignore_errors = true
    )
""")

#Quick check
print(con.execute("SELECT COUNT(*) FROM prod.tmdb_movie_details").fetchone())
print(con.execute("SELECT * FROM prod.tmdb_movie_details LIMIT 5").df())
con.close()