import duckdb as db
import numpy as np
from src.generators.dim_user import generate_users
from src.generators.dim_product import generate_products
from src.generators.dim_event_type import generate_event_types
from src.generators.dim_date import generate_dates

def create():
    conn = db.connect()

    generate_dates(conn)
    generate_products(conn)
    generate_event_types(conn)
    generate_users(conn,50000)

create()
