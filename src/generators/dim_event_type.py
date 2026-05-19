from src.config.paths import (DDL_DIM_EVENT_TYPE_PATH, EVENT_TYPES_PARQUET_PATH, RAW_DIM_EVENT_TYPE_PATH)

def generate_event_types(conn):


    #read the DDL SQL file and execute it to create the dim_event_type table
    create_db = DDL_DIM_EVENT_TYPE_PATH.read_text()

    conn.execute(create_db)

    #read the dim_event_type csv file and export it to a parquet file

    conn.execute(f'''
                INSERT INTO dim_event_type SELECT * FROM read_csv_auto('{RAW_DIM_EVENT_TYPE_PATH}')
    ''')

    conn.execute(f"""
                    COPY dim_event_type TO '{EVENT_TYPES_PARQUET_PATH}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE TRUE) """)

