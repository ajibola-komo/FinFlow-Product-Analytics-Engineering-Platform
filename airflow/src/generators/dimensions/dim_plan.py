import pandas as pd
import numpy as np
from src.config.paths import (DDL_DIM_PLAN_PATH, RAW_DIM_PLAN_PATH, PLANS_PARQUET_PATH)

def generate_dim_plan(conn):

    create_db = DDL_DIM_PLAN_PATH.read_text()

    conn.execute(create_db)

    conn.execute(f'''
            INSERT INTO DIM_PLAN SELECT * FROM read_csv_auto('{RAW_DIM_PLAN_PATH}')
    ''')

    conn.execute(f'''
                COPY DIM_PLAN TO '{PLANS_PARQUET_PATH}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE TRUE) 

''')
