import os
import subprocess
from pathlib import Path

DATA_DIR = Path("data").resolve()
BASE_URL = "https://datasets.imdbws.com"
FILES = [
    "title.basics.tsv.gz",
    "title.crew.tsv.gz",
    "title.episode.tsv.gz",
    "title.ratings.tsv.gz",
    "title.principals.tsv.gz",
    "title.akas.tsv.gz",
    "name.basics.tsv.gz",
]


def download_imdb_datasets() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        "docker", "run", "--rm",
        # curlimages/curl runs as a non-root user, so run as the host user
        # to be able to write into the mounted folder.
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{DATA_DIR}:/data",
        "-w", "/data",
        "curlimages/curl",
        "-fsS",  # fail on HTTP errors, hide progress meter, still show errors
    ]
    for name in FILES:
        cmd += ["-O", f"{BASE_URL}/{name}"]

    print("Downloading IMDb datasets...")
    subprocess.run(cmd, check=True)

    print("Done. Files in data/:")
    for f in sorted(DATA_DIR.glob("*.tsv.gz")):
        print(f" - {f.name} ({f.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    download_imdb_datasets()