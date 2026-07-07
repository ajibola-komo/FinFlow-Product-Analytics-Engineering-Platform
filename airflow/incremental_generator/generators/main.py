import duckdb as db
import numpy as np
from incremental_generator.generators.dimensions.dim_user import generate_users
#from src.generators.dimensions.dim_product import generate_products
#from src.generators.dimensions.dim_event_type import generate_event_types
#from src.generators.dimensions.dim_date import generate_dates
#from src.snowflake_setup.create_snowflake_tables import create_snowflake_bronze_tables
from dotenv import load_dotenv
from pathlib import Path
from incremental_generator.config.paths import CURRENT_PARTITION, DB_DIR, FINFLOW_DB_PATH

load_dotenv()

def create():
    #create_snowflake_bronze_tables()
    CURRENT_PARTITION.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with db.connect(FINFLOW_DB_PATH) as conn:
        generate_users(conn,100)
        print("\nFirst 10 rows:")
        print(conn.sql("SELECT distinct signup_date::DATE as reg_date FROM dim_user LIMIT 10").fetchdf())

    
    #upload_parquet_files()
    #upload_from_s3_to_snowflake()
    #upload_to_gcs()
    #upload_from_gcs_to_snowflake()
    #run_dbt_models()


create()
