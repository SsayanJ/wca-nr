""" Code Deployed on Google Functions to update the Database from the WCA website.
It is associated with a cron job on Google Scheduler to run this code every 2 days.
"""

from google.cloud import storage
import requests, json, io, os
from zipfile import ZipFile
import pandas as pd


# Could remove the source files to save on storage if needed
FILES_TO_SAVE = [
    "WCA_export_Persons.tsv", 
    "WCA_export_RanksAverage.tsv", 
    "WCA_export_RanksSingle.tsv", 
    "metadata.json",
    "WCA_records_single.csv",
    "WCA_records_avg.csv"
    ]
TEMP_PATH = "/tmp/"

def load_data(folder_path):
  ranks_avg = pd.read_csv(os.path.join(folder_path, "WCA_export_RanksAverage.tsv"), sep="\t", dtype={'eventId': 'str'})
  ranks_single = pd.read_csv(os.path.join(folder_path, "WCA_export_RanksSingle.tsv"), sep="\t", dtype={'eventId': 'str'})
  persons = pd.read_csv(os.path.join(folder_path, "WCA_export_Persons.tsv"), sep="\t")
  #keep only current IDs (due to name or country changes, some people have several lines with the same ID and a subid)
  persons = persons[persons["subid"]==1]
  return ranks_avg, ranks_single, persons

def create_record_table(ranks_table, persons):
  ranks_table = ranks_table[ranks_table["countryRank"]==1]
  records_table = persons.merge(ranks_table, left_on="id", right_on="personId")
  return records_table

def extract_target_files(file_bytes, destination_folder):
  # Create a ZipFile Object from the content in bytes
  zf = ZipFile(io.BytesIO(file_bytes))
  # Get a list of all archived file names from the zip
  file_names = zf.namelist()
  # Iterate over the file names
  for f_name in file_names:
    # Check filename is in the target list
    if f_name in FILES_TO_SAVE:
      # Extract a single file from zip
      zf.extract(f_name, destination_folder)

def process_data():
  ranks_avg, ranks_single, persons = load_data(TEMP_PATH) 
  records_table_single = create_record_table(ranks_single, persons)
  records_table_avg = create_record_table(ranks_avg, persons)
  records_table_single.to_csv(f"{TEMP_PATH}/WCA_records_single.csv")
  records_table_avg.to_csv(f"{TEMP_PATH}/WCA_records_avg.csv")

def run(event, context):
  db_bucket = "wca-nr-db"
  
  storage_client = storage.Client()

  bucket = storage_client.get_bucket(db_bucket)

  wca_response = requests.get("https://www.worldcubeassociation.org/api/v0/export/public").json()
  metadata_blob = bucket.blob("metadata.json")
  
  current_data = json.loads(metadata_blob.download_as_string(client=None))
  # Compare date only (10 first characters), hour is stored in different format
  if wca_response["export_date"][:10] != current_data["export_date"][:10]:
    dl_file = requests.get(wca_response["tsv_url"]).content
    extract_target_files(dl_file, TEMP_PATH)
    process_data()

    for f_name in FILES_TO_SAVE:
      # Name of the file on the GCS once uploaded
      blob = bucket.blob(f_name)
      # Path of the local file
      blob.upload_from_filename(TEMP_PATH + f_name)
  
