from src.config.paths import (DDL_DIM_DATE_PATH)

def generate_dates(conn):

    #read the DDL SQL file and execute it to create the dim_date table
    create_db = DDL_DIM_DATE_PATH.read_text()

    conn.execute(create_db)