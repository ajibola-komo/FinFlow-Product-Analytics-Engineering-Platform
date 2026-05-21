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
        sql_path = ddl_path
        with open(sql_path, "r") as f:
            ddl = f.read()
        
        cursor.execute(ddl)

    cursor.close()
    conn.close()