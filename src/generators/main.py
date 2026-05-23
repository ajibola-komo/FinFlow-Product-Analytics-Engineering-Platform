import duckdb as db
import numpy as np
from generators.dimensions.dim_user import generate_users
from generators.dimensions.dim_product import generate_products
from generators.dimensions.dim_event_type import generate_event_types
from generators.dimensions.dim_date import generate_dates
from src.snowflake_setup.create_snowflake_tables import create_snowflake_bronze_tables
from dotenv import load_dotenv
from src.storage.s3_upload import upload_parquet_files
from src.storage.snowflake_upload import upload_from_s3_to_snowflake
from src.run_dbt.run_dbt import run_dbt_models
from generators.dimensions.dim_plan import generate_dim_plan

load_dotenv()

def create():
    create_snowflake_bronze_tables()
    with db.connect() as conn:
        generate_dates(conn)
        generate_products(conn)
        generate_event_types(conn)
        generate_dim_plan(conn)
        generate_users(conn,50000)
    
    upload_parquet_files()
    upload_from_s3_to_snowflake()
    run_dbt_models()


create()
