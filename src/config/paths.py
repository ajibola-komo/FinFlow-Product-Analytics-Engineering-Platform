from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = PROJECT_ROOT / "raw"

EXPORT_DIR = DATA_DIR / "exports"
PARQUET_DIR = EXPORT_DIR / "parquet"

RAW_DIM_EVENT_TYPE_PATH = RAW_DIR / "dim_event_type.csv"
RAW_DIM_PRODUCT_PATH = RAW_DIR / "dim_product.csv"

# SQL PATHS
SQL_DIR = PROJECT_ROOT / "sql"
DDL_SQL_DIR = SQL_DIR / "ddl"
SNOWFLAKE_SQL_DIR = SQL_DIR / "snowflake_ddl"

DDL_DIM_EVENT_TYPE_PATH = DDL_SQL_DIR / "dim_event_type.sql"
DDL_DIM_PRODUCT_PATH = DDL_SQL_DIR / "dim_product.sql"
DDL_DIM_USER_PATH = DDL_SQL_DIR / "dim_user.sql"
DDL_DIM_WALLET_PATH = DDL_SQL_DIR / "dim_wallet.sql"
DDL_DIM_DATE_PATH = DDL_SQL_DIR / "dim_date.sql"


SNOWFLAKE_DIM_EVENT_TYPE_PATH = SNOWFLAKE_SQL_DIR / "dim_event_type.sql"
SNOWFLAKE_DIM_PRODUCT_PATH = SNOWFLAKE_SQL_DIR / "dim_product.sql"
SNOWFLAKE_DIM_USER_PATH = SNOWFLAKE_SQL_DIR / "dim_user.sql"
SNOWFLAKE_DIM_WALLET_PATH = SNOWFLAKE_SQL_DIR / "dim_wallet.sql"
SNOWFLAKE_DIM_DATE_PATH = SNOWFLAKE_SQL_DIR / "dim_date.sql"

SNOWFLAKE_DDL_PATHS = [SNOWFLAKE_DIM_EVENT_TYPE_PATH, SNOWFLAKE_DIM_PRODUCT_PATH, 
                         SNOWFLAKE_DIM_USER_PATH, SNOWFLAKE_DIM_WALLET_PATH, SNOWFLAKE_DIM_DATE_PATH
                         ]


#parquet paths
DATES_PARQUET_PATH = PARQUET_DIR / "dim_date.parquet"
PRODUCTS_PARQUET_PATH = PARQUET_DIR / "dim_product.parquet"
USERS_PARQUET_PATH = PARQUET_DIR / "dim_user.parquet"
WALLETS_PARQUET_PATH = PARQUET_DIR / "dim_wallet.parquet"
EVENT_TYPES_PARQUET_PATH = PARQUET_DIR / "dim_event_type.parquet"