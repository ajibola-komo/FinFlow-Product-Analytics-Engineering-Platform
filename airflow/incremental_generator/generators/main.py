import duckdb as db
import numpy as np
from incremental_generator.generators.dimensions.dim_user import generate_users
from incremental_generator.generators.dimensions.dim_wallet import generate_list_of_wallets
from incremental_generator.generators.facts.fact_wallet_balance import generate_wallet_balance
from incremental_generator.generators.facts.facts_tables import generate_facts
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
        generate_list_of_wallets(conn)
        generate_wallet_balance(conn)
        generate_facts(conn, 100_000)

    
    #upload_parquet_files()
    #upload_from_s3_to_snowflake()
    #upload_to_gcs()
    #upload_from_gcs_to_snowflake()
    #run_dbt_models()


create()
