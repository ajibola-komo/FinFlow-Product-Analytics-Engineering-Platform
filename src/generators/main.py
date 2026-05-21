import duckdb as db
import numpy as np
from src.generators.dim_user import generate_users
from src.generators.dim_product import generate_products
from src.generators.dim_event_type import generate_event_types
from src.generators.dim_date import generate_dates
from src.snowflake_setup.create_snowflake_tables import create_snowflake_bronze_tables

def create():
    conn = db.connect()
    create_snowflake_bronze_tables()
    generate_dates(conn)
    generate_products(conn)
    generate_event_types(conn)
    generate_users(conn,50000)

create()
