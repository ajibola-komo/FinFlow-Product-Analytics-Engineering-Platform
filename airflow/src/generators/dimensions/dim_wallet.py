import numpy as np
import pandas as pd
from src.config.paths import (DDL_DIM_WALLET_PATH, WALLETS_PARQUET_PATH)
from src.config.constants import (DEFAULT_TRANSACTION_START_TIMESTAMP, DEFAULT_TRANSACTION_END_TIMESTAMP)
from datetime import timedelta

def generate_list_of_wallets(conn):
    create_db = DDL_DIM_WALLET_PATH.read_text()

    conn.execute(create_db)

    users_data = conn.execute('''
            SELECT * FROM dim_user order by signup_date
    ''').df()

    total_users = len(users_data)

    wallet_ids = np.arange(1, total_users + 1)

    user_ids = users_data["user_id"]

    created_at = np.array(users_data["signup_date"])

    print(pd.isna(created_at).sum())

    is_activated_user = users_data["is_activated_user"]

    active_mask = np.where(is_activated_user == True)[0]
    inactive_mask = np.where(is_activated_user == False)[0]

    activation_timeframe = users_data["wallet_activation_timeframe"]

    activated_at = np.empty(
        total_users,
        dtype=object
    )


    activated_at[active_mask] = np.array([ca + pd.to_timedelta(int(ro),unit="m") for ca,ro in zip(created_at[active_mask], activation_timeframe[active_mask])])
    activated_at[inactive_mask] = None

    activated_at_id = np.empty(total_users,
        dtype=object)

    created_at_id = [int(pd.Timestamp(created_at[i]).strftime('%Y%m%d')) for i in range(total_users)]
    activated_at_id[active_mask] = [int(pd.Timestamp(i).strftime('%Y%m%d')) for i in activated_at[active_mask]]

    wallet_currency = np.array(["GBP"] * total_users)

    df_raw = pd.DataFrame({
        "wallet_id":wallet_ids,
        "user_id":user_ids,
        'wallet_currency':wallet_currency,
        "created_at":created_at,
        "activated_at":activated_at,
        "wallet_created_at_id":created_at_id,
        "wallet_activated_at_id":activated_at_id
    })
    conn.register('df_raw', df_raw)

    conn.execute('''INSERT into dim_wallet select * from df_raw''')

    conn.execute(f'''COPY dim_wallet to '{WALLETS_PARQUET_PATH}' (FORMAT PARQUET) ''')

    read_parquet = conn.execute(f'''select * from read_parquet('{WALLETS_PARQUET_PATH}')''').fetchdf()

    print(read_parquet.head(10))

    






    