import snowflake.connector
import os
from dotenv import load_dotenv
from src.config.paths import (TABLE_NAMES)
from src.config.envariables import(SNOWFLAKE_CONFIG)

load_dotenv()


def upload_from_s3_to_snowflake():

    conn = snowflake.connector.connect(
        **SNOWFLAKE_CONFIG
    )

    cursor = conn.cursor()


    sql_stage = f"""
        CREATE OR REPLACE FILE FORMAT my_parquet_format
            TYPE = 'PARQUET'
            BINARY_AS_TEXT = FALSE
            USE_VECTORIZED_SCANNER = TRUE;
"""
    
    cursor.execute(sql_stage)

    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

    sql = f"""
    CREATE STAGE IF NOT EXISTS finflow_stage
    URL='s3://finflow-s3-bucket'
    CREDENTIALS=(AWS_KEY_ID='{aws_key}' AWS_SECRET_KEY='{aws_secret}')
    FILE_FORMAT=(FORMAT_NAME = 'my_parquet_format')
    REGION='us-east-1';
"""
    cursor.execute(sql)

    for table_name in TABLE_NAMES:

        cursor.execute(f"TRUNCATE TABLE {table_name}")

        cursor.execute(f"""
        COPY INTO {table_name}
        FROM @finflow_stage
        FILES = ('{table_name}.parquet')
        FILE_FORMAT = (FORMAT_NAME = 'my_parquet_format')
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        FORCE=TRUE;
        """)

    cursor.close()
    conn.close()



