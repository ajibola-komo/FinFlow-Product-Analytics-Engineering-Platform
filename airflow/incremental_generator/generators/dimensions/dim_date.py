from src.config.paths import (DDL_DIM_DATE_PATH, DATES_PARQUET_PATH)

def generate_dates(conn):

    #read the DDL SQL file and execute it to create the dim_date table
    create_db = DDL_DIM_DATE_PATH.read_text()

    conn.execute(create_db)

    #write the dim_date table to a parquet file
    conn.execute(f'''
                    COPY dim_date TO '{DATES_PARQUET_PATH}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE TRUE)
''')