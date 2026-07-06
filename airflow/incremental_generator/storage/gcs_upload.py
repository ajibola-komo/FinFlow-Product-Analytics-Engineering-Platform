import os
from dotenv import load_dotenv
from src.config.paths import (
   GCS_FILE_NAMES, LOCAL_FILE_PATHS
)
from google.cloud import storage


load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def upload_to_gcs():

    client = storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET_NAME)

    for file_name, local_path in zip(GCS_FILE_NAMES, LOCAL_FILE_PATHS):

        blob = bucket.blob(file_name)

        blob.upload_from_filename(local_path)

        print(
            f"Uploaded {local_path} "
            f"to gs://{GCS_BUCKET_NAME}/{file_name}"
        )
