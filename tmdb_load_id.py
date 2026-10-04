import duckdb

con = duckdb.connect("movies_db/movies_project.duckdb")

print("Connected. Creating table now..")
con.execute("CREATE SCHEMA IF NOT EXISTS prod")
con.execute("""
    CREATE OR REPLACE TABLE prod.tmdb_ids AS
    SELECT DISTINCT imdb_id, tmdb_id
    FROM read_json(
        'tmdb_progress.jsonl',
        format = 'newline_delimited',
        columns = {imdb_id: 'VARCHAR', tmdb_id: 'INT'},
        ignore_errors = true
    )
""")

#Quick check
print(con.execute("SELECT COUNT(*) FROM prod.tmdb_ids").fetchone())
print(con.execute("SELECT * FROM prod.tmdb_ids LIMIT 5").df())
con.close()


