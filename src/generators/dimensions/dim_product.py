import pandas as pd
import numpy as np
from src.config.paths import (DDL_DIM_PRODUCT_PATH, RAW_DIM_PRODUCT_PATH, PRODUCTS_PARQUET_PATH)

def generate_products(conn):

    create_db = DDL_DIM_PRODUCT_PATH.read_text()

    conn.execute(create_db)

    conn.execute(f'''
            INSERT INTO DIM_PRODUCT SELECT * FROM read_csv_auto('{RAW_DIM_PRODUCT_PATH}')
    ''')

    conn.execute(f'''
                COPY DIM_PRODUCT TO '{PRODUCTS_PARQUET_PATH}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE TRUE) 

''')