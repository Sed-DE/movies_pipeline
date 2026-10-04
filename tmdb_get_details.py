import os
import json
import tmdbsimple as tmdb
import time
from tqdm import tqdm

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def get_tmdb_ids() -> list[int]:
  """Gets tmdb_ids from json file"""
  ids = [] 
  with open("tmdb_progress.jsonl") as f:
    for line in f:
      record = json.loads(line)

      if record.get("tmdb_id") is None:
       continue  

      ids.append(record["tmdb_id"]) 

  return ids


def load_done_ids() -> set[str]:
    """Read whatever's already been fetched, so we don't redo it."""
    done = set() # Sets give fast "is this id already done?" lookups
    if progress_file.exists():
      with open(progress_file) as f:
          for line in f:
              try:
                record = json.loads(line) 
                done.add(record["tmdb_id"]) # Add loaded tmdb_id records inside set
              except (json.JSONDecodeError, KeyError):
                # Bad line (e.g. cut off by Ctrl+C mid-write) or missing key.
                # Skip it; that id isn't marked done, so it gets refetched.
                continue
    return done


# ---------------------------------------------------------------------------
# API call (runs inside worker threads)
# ---------------------------------------------------------------------------

def get_movie_details(tmdb_id):
  """Get details with tmdb id"""
  for attempt in range(2): #total tries per id
    try:
      movie = tmdb.Movies(id=tmdb_id)
      response = movie.info()

      return {"tmdb_id": tmdb_id, 
              "budget": movie.budget, 
              "overview": movie.overview, 
              "poster_path": movie.poster_path,
              "revenue": movie.revenue,
              "original_title": movie.original_title,
              "runtime": movie.runtime
              }
    
    except tmdb.requests.RequestException:
      time.sleep(0.8)

  return{"tmdb_id": tmdb_id, "failed_error": "wasn't able to get details"}


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------
    
def run_thread_executor():
  ids = get_tmdb_ids()
  done_ids = load_done_ids() 

   # Only fetch ids we haven't already saved
  remaining = [id for id in ids if id not in done_ids]
  print(f"{len(done_ids)} already done, {len(remaining)} left to fetch\n")
  
  failed = [] # ids that failed all attempts

  with open("tmdb_details.jsonl", "a") as f, ThreadPoolExecutor(max_workers=10) as executor:

    # Queue one task per id; submit() returns immediately
    futures = [executor.submit(get_movie_details, tmdb_id) for tmdb_id in remaining]  

    try:
     # as_completed yields futures as they finish; tqdm shows the progress bar
     for future in tqdm(
         as_completed(futures), 
         total=len(remaining), 
         desc="Fetching tmdb movie details"
         ):
             record = future.result()
             if "failed_error" in record:
                failed.append(record["tmdb_id"])
                continue

             # Save the result right away so progress survives a crash
             f.write(json.dumps(record) + "\n")
             f.flush() # push to disk now, not later
             
    except KeyboardInterrupt:
       # Ctrl+C: drop tasks still waiting in the queue
       executor.shutdown(wait=False, cancel_futures=True)
       raise

  print(f"DONE! {len(failed)} failed, rerun to retry them")
  #Some of the the ids belong to tv series,
  #So they won't work for the movie function.
  #Print them out so you can confirm
  print(failed)


if __name__ == '__main__':
  progress_file = Path("tmdb_details.jsonl") # .jsonl = one JSON object per line
  tmdb.REQUESTS_TIMEOUT = 10 #request timeout
  tmdb.API_KEY = os.environ["API_KEY"] #api key
  run_thread_executor()