import os
import snowflake.connector

from dotenv import load_dotenv

from src.config.paths import TABLE_NAMES
from src.config.envariables import SNOWFLAKE_CONFIG

load_dotenv()

FILE_FORMAT_NAME = "my_parquet_format"
STAGE_NAME = "finflow_stage"

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
SNOWFLAKE_GCS_INTEGRATION = os.getenv("SNOWFLAKE_GCS_INTEGRATION")


def upload_from_gcs_to_snowflake():

    conn = snowflake.connector.connect(
        **SNOWFLAKE_CONFIG
    )

    try:

        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE OR REPLACE FILE FORMAT {FILE_FORMAT_NAME}
            TYPE = PARQUET
            BINARY_AS_TEXT = FALSE
            USE_VECTORIZED_SCANNER = TRUE;
        """)

        cursor.execute(f"""
            CREATE OR REPLACE STAGE {STAGE_NAME}
            URL = 'gcs://{GCS_BUCKET_NAME}'
            STORAGE_INTEGRATION = {SNOWFLAKE_GCS_INTEGRATION}
            FILE_FORMAT = (
                FORMAT_NAME = '{FILE_FORMAT_NAME}'
            );
        """)

        for table_name in TABLE_NAMES:

            print(f"Loading {table_name}...")

            cursor.execute(
                f"TRUNCATE TABLE {table_name}"
            )

            copy_sql = f"""
                COPY INTO {table_name}
                FROM @{STAGE_NAME}
                FILES = ('{table_name}.parquet')
                FILE_FORMAT = (
                    FORMAT_NAME = '{FILE_FORMAT_NAME}'
                )
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                FORCE = TRUE;
            """

            results = cursor.execute(copy_sql).fetchall()

            print(f"Successfully loaded {table_name}")

            for row in results:
                print(row)

    finally:

        cursor.close()
        conn.close()