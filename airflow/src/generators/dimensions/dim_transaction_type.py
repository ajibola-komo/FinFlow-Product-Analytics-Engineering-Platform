import numpy as np
import pandas as pd
from src.config.paths import RAW_DIM_TRANSACTION_TYPE_PATH, DDL_DIM_TRANSACTION_TYPE_PATH, TRANSACTION_TYPE_PARQUET_PATH

def generate_transaction_types(conn):

    create_db = DDL_DIM_TRANSACTION_TYPE_PATH.read_text()

    conn.execute(create_db)

    conn.execute(f'''
            INSERT INTO DIM_TRANSACTION_TYPE 
                 SELECT transaction_type_id,
                 transaction_type_code,
                 transaction_type_name,
                 transaction_type_description,
                 transaction_category,
                 transaction_direction
        FROM read_csv_auto('{RAW_DIM_TRANSACTION_TYPE_PATH}')
    ''')


    conn.execute(f'''
            COPY dim_transaction_type to '{TRANSACTION_TYPE_PARQUET_PATH}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE TRUE)
    ''')

    print(
        conn.execute(f'''
                        SELECT * FROM read_parquet('{TRANSACTION_TYPE_PARQUET_PATH}')
                ''').fetchdf()
)