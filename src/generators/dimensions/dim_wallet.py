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

    wallet_id = np.arange(1, total_users + 1)

    user_ids = users_data["user_id"]

    created_at = users_data["signup_date"]

    kyc_status = users_data["kyc_completed"]

    activated_at = np.empty(
        total_users,
        dtype="datetime64[ns]"
    )

    onboarded_customers = kyc_status == True

    random_offsets = np.random.randint(0,30,size=onboarded_customers.sum())

    activated_at[onboarded_customers] = [ca + timedelta(days=(int(ro))) for ca,ro in zip(created_at[onboarded_customers], random_offsets)]
    activated_at[~onboarded_customers] = None

    activated_at_id = np.empty(total_users, dtype=object)

    created_at_id = [int(pd.Timestamp(created_at[i]).strftime('%Y%m%d')) for i in range(total_users)]
    activated_at_id[onboarded_customers] = [int(pd.Timestamp(i).strftime('%Y%m%d')) for i in activated_at[onboarded_customers]]


    df_raw = pd.DataFrame({
        "wallet_id":wallet_id,
        "user_id":user_ids,
        "created_at":created_at,
        "activated_at":activated_at,
        "wallet_created_at_id":created_at_id,
        "wallet_activated_at_id":activated_at_id
    })
    conn.register('df_raw', df_raw)

    conn.execute('''INSERT into dim_wallet select * from df_raw''')

    conn.execute(f'''COPY dim_wallet to '{WALLETS_PARQUET_PATH}' (FORMAT PARQUET) ''')

    






    