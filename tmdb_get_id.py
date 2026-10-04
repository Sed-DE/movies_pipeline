
import os
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import duckdb
import requests
from tqdm import tqdm


# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------

def get_list_of_ids() -> list[str]:
  """Get IMDb ids (tconst) from the DuckDB table, for titles with 5000+ votes."""
  con = duckdb.connect("movies_db/movies_project.duckdb")
  list_of_imdb_ids = con.execute("""
      SELECT tconst
      FROM prod.title_ratings 
      WHERE numVotes >= 5000
  """).df()["tconst"].tolist()

  print(f"{len(list_of_imdb_ids)} total rows obtained") 
  return list_of_imdb_ids
  

def load_done_ids() -> set[str]:
    """Read whatever's already been fetched, so we don't redo it."""
    done = set() # Sets give fast "is this id already done?" lookups
    if progress_file.exists():
      with open(progress_file) as f:
          for line in f:
              try:
                record = json.loads(line) 
                done.add(record["imdb_id"]) # Add loaded imdb_id records inside set
              except (json.JSONDecodeError, KeyError):
                # Bad line (e.g. cut off by Ctrl+C mid-write) or missing key.
                # Skip it; that id isn't marked done, so it gets refetched.
                continue
    return done
    

# ---------------------------------------------------------------------------
# API CALL (runs inside worker threads)
# ---------------------------------------------------------------------------


def fetch_id(imdb_id) -> dict:
    """Look up the TMDB id for one IMDb id.

    Returns:
        {"imdb_id": ..., "tmdb_id": ...}  if TMDB answered (tmdb_id is None if no match)
        {"imdb_id": ..., "error": ...}    if every attempt failed
    """
    for attempt in range(2):
        try:
            r = requests.get(
                f"https://api.themoviedb.org/3/find/{imdb_id}",
                params={"api_key": API_KEY, "external_source": "imdb_id"},
                timeout=10
            )
            # 429 = Too Many Requests: wait as long as the API says, then retry
            if r.status_code == 429: 
                time.sleep(float(r.headers.get("Retry-After", 2)))
                continue #Retry request

            r.raise_for_status() # turn other HTTP errors (401, 500...) into exceptions

            data = r.json()
            tmdb_id = data["movie_results"][0]["id"] if data.get("movie_results") else None

            return {"imdb_id": imdb_id, "tmdb_id": tmdb_id}
        
        except requests.RequestException:
            time.sleep(2)

    # If every attempt fails
    return {"imdb_id": imdb_id, "error": "failed after retries"}


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def run_thread_executor(): 
    """Fetch all remaining ids in parallel and append results to the progress file."""
    done_ids = load_done_ids()
    imdb_ids = get_list_of_ids()

    # Only fetch ids we haven't already saved
    remaining = [id for id in imdb_ids if id not in done_ids]
    print(f"{len(done_ids)} already done, {len(remaining)} left to fetch\n")

    failed = [] # ids that failed all attempts

    with open(progress_file, "a") as f, ThreadPoolExecutor(max_workers=10) as executor:

            # Queue one task per id; submit() returns immediately
            futures = [executor.submit(fetch_id, imdb_id) for imdb_id in remaining]

            try:
                # as_completed yields futures as they finish; tqdm shows the progress bar
                for future in tqdm(
                    as_completed(futures), 
                    total=len(remaining), 
                    desc="Fetching API tmdb Data"
                    ):
                        record = future.result()
                        if "error" in record:
                            failed.append(record["imdb_id"])
                            continue
                        f.write(json.dumps(record) + "\n")
                        f.flush() # push to disk now, not later
                        
            except KeyboardInterrupt:
                # Ctrl+C: drop tasks still waiting in the queue
                executor.shutdown(wait=False, cancel_futures=True)
                raise

            print(f"DONE! {len(failed)} failed, rerun to retry them")
    

if __name__ == '__main__':
  API_KEY = os.environ["API_KEY"] # read the API key from an environment variable
  progress_file = Path("tmdb_progress.jsonl") # .jsonl = one JSON object per line
  run_thread_executor()