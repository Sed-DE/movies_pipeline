

from pathlib import Path
import duckdb

data_dir = Path("data") 
parquet_dir = Path("parquet_data")


def convert_files():
    # Create parquet_data directory
    parquet_dir.mkdir(parents=True, exist_ok=True)

    # Loop through all .tsv files
    for tsv_file in data_dir.glob("*.tsv.gz"):
        print(f"Converting TSV file: {tsv_file.name} to parquet")
        file_name = (str(tsv_file.name).replace(".tsv.gz", "").replace(".", "_"))
        parquet_filename = f"{file_name}.parquet"
        parquet_filepath = parquet_dir / parquet_filename

        if parquet_filepath.exists():
            print(f"Skipping {parquet_filename}. It already exists\n")
            continue

        # Written to a .tmp path in the parquet_dir, then renamed on success.
        # If COPY crashes halfway (disk full, killed process, etc.), the
        # .tmp file is left behind instead of a broken file sitting at the
        # real filename — so a future run won't mistake a corrupt/partial
        # file for a finished one via the .exists() check above.
        tmp_filepath = parquet_filepath.with_suffix(".tmp")

        try:
            duckdb.sql(f"""
                COPY (
                    SELECT * FROM read_csv(
                        '{tsv_file}',
                        delim='\t',
                        nullstr='\\N'
                    )
                ) TO '{tmp_filepath}' (FORMAT PARQUET)
            """)
            # Only becomes the "real" file once the copy fully succeeded
            tmp_filepath.rename(parquet_filepath)
            print(f"{parquet_filepath} has completed!\n")

        #Catches error if copy process or rename process failed
        except Exception as e:
            if tmp_filepath.exists():
                tmp_filepath.unlink() #deletes broken .tmp file
            print(f"FAILED converting {tsv_file.name}: {e}\n")
            raise
            #Stop the code if broken temp file is found
            #If you want the code to continue regardless, delete "raise"

if __name__ == "__main__":
    convert_files()

    print("Connecting to database...\n")
    with duckdb.connect("movies_db/movies_project.duckdb") as con:
        print("Connected. Creating schema...")
        con.execute("CREATE SCHEMA IF NOT EXISTS prod")
        print("Schema ready.\n")

        for parquet_file in parquet_dir.glob("*.parquet"):
            table_name = (str(parquet_file.name).replace(".parquet", ""))
            print(f"Building {table_name} table...")
            con.execute(f"""
                CREATE OR REPLACE TABLE prod.{table_name} AS
                SELECT * FROM read_parquet('{parquet_file}')
            """)

            #Check if all rows are present... For your sanity
            result = con.execute(f"SELECT COUNT(*) FROM prod.{table_name}").fetchone()
            print(f"Done with {table_name} table creation — {result[0]:,} rows\n")

    print("👍")