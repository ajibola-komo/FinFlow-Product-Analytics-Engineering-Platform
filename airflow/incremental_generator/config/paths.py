from pathlib import Path
from incremental_generator.config.constants import CURRENT_DATE
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = PROJECT_ROOT / "raw"

EXPORT_DIR = DATA_DIR / "exports"
PARQUET_DIR = EXPORT_DIR / "parquet"
CURRENT_PARTITION = PARQUET_DIR / f"load_date_{CURRENT_DATE.strftime('%Y-%m-%d')}"
DB_DIR = PROJECT_ROOT / "db"
FINFLOW_DB_PATH = DB_DIR / "finflow.db"

RAW_DIM_EVENT_TYPE_PATH = RAW_DIR / "dim_event_type.csv"
RAW_DIM_PRODUCT_PATH = RAW_DIR / "dim_product.csv"
RAW_DIM_PLAN_PATH = RAW_DIR / "dim_plan.csv"
RAW_DIM_TRANSACTION_TYPE_PATH = RAW_DIR / "dim_transaction_type.csv"


#incremental Loads
CURRENT_DATE_PARTITION = pd.to_datetime(CURRENT_DATE).strftime("%Y-%m-%d")

CURRENT_DATES_PARQUET_PATH = CURRENT_PARTITION / f"dim_date_partition_{CURRENT_DATE_PARTITION}.parquet"

CURRENT_USERS_PARQUET_PATH = CURRENT_PARTITION / f"dim_user_partition_{CURRENT_DATE_PARTITION}.parquet"

CURRENT_WALLETS_PARQUET_PATH = CURRENT_PARTITION / f"dim_wallet_partition_{CURRENT_DATE_PARTITION}.parquet"

CURRENT_FACT_USER_EVENT_PARQUET_PATH = CURRENT_PARTITION / f"fact_user_event_partition_{CURRENT_DATE_PARTITION}.parquet"

CURRENT_FACT_INVESTMENT_POSITION_PARQUET_PATH = CURRENT_PARTITION / f"fact_investment_position_partition_{CURRENT_DATE_PARTITION}.parquet"

CURRENT_FACT_TRANSACTION_PARQUET_PATH = CURRENT_PARTITION / f"fact_transaction_partition_{CURRENT_DATE_PARTITION}.parquet"

CURRENT_FACT_WALLET_BALANCE_PARQUET_PATH = CURRENT_PARTITION / f"fact_wallet_balance_partition_{CURRENT_DATE_PARTITION}.parquet"

CURRENT_PARTITION_FILE_PATHS = [CURRENT_USERS_PARQUET_PATH, CURRENT_WALLETS_PARQUET_PATH, CURRENT_FACT_USER_EVENT_PARQUET_PATH, CURRENT_FACT_INVESTMENT_POSITION_PARQUET_PATH,
                                CURRENT_FACT_TRANSACTION_PARQUET_PATH, CURRENT_FACT_WALLET_BALANCE_PARQUET_PATH]

FILE_NAMES = ["dim_user.parquet","dim_wallet.parquet","fact_user_event.parquet","fact_investment_position.parquet","fact_transaction.parquet","fact_wallet_balance.parquet"]
