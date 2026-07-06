import snowflake.connector
import os
from dotenv import load_dotenv
from src.config.envariables import SNOWFLAKE_CONFIG
from src.config.paths import SNOWFLAKE_SQL_DIR, SNOWFLAKE_DDL_PATHS

load_dotenv()

def create_snowflake_bronze_tables():
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cursor = conn.cursor()
    

    database_name = SNOWFLAKE_CONFIG.get("database")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")


    schema_name = SNOWFLAKE_CONFIG.get("schema")
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database_name}.{schema_name}")

    cursor.execute(f"USE DATABASE {database_name}")
    cursor.execute(f"USE SCHEMA {database_name}.{schema_name}")

    for ddl_path in SNOWFLAKE_DDL_PATHS:
        try:
            print(f"Running: {ddl_path}")

            with open(ddl_path, "r") as f:
                ddl = f.read()

                cursor.execute(ddl)

            print(f"SUCCESS: {ddl_path}")

        except Exception as e:
            print(f"FAILED: {ddl_path}")
            print(e)
            raise

    cursor.close()
    conn.close()