from src.config.paths import(DDL_DIM_PRODUCT_PATH, PRODUCTS_PARQUET_PATH, RAW_DIM_PRODUCT_PATH)

def generate_products(conn):
    #read SQL file for product DDL and execute it to create the dim_product table
    create_db = DDL_DIM_PRODUCT_PATH.read_text()

    conn.execute(create_db)

    #read the dim_product csv file and export it to a parquet file
    conn.execute(f'''

        INSERT INTO dim_product SELECT * FROM read_csv_auto('{RAW_DIM_PRODUCT_PATH}')

    ''')

    #write the dim_product table to a parquet file
    conn.execute(f"""
                    COPY dim_product TO '{PRODUCTS_PARQUET_PATH}' (FORMAT PARQUET, OVERWRITE_OR_IGNORE TRUE) 
                """)
    