import numpy as np
import pandas as pd
from incremental_generator.config.paths import (CURRENT_WALLETS_PARQUET_PATH)
from incremental_generator.config.constants import (GENERATION_START_TIMESTAMP,GENERATION_END_TIMESTAMP)

def generate_list_of_wallets(conn):

    users_data = conn.execute(f'''
            SELECT * FROM dim_user 
            WHERE signup_date between '{GENERATION_START_TIMESTAMP}' and '{GENERATION_END_TIMESTAMP}'
                              order by signup_date
    ''').df()

    total_users = len(users_data)

    wallet_ids = users_data["user_id"]

    user_ids = users_data["user_id"]

    wallet_created_at = np.array(users_data["signup_date"])

    print(pd.isna(wallet_created_at).sum())

    wallet_activated_at = np.empty(
        total_users,
        dtype=object
    )


    wallet_activated_at_id = np.empty(total_users,dtype=object)

    wallet_created_at_id = [int(pd.Timestamp(wallet_created_at[i]).strftime('%Y%m%d')) for i in range(total_users)]
    

    wallet_currency = np.array(["GBP"] * total_users)

    created_at = wallet_created_at
    last_updated_at = created_at

    df_raw = pd.DataFrame({
        'wallet_id':wallet_ids,
        'user_id':user_ids,
        'wallet_currency':wallet_currency,
        'wallet_created_at':wallet_created_at,
        'wallet_activated_at':wallet_activated_at,
        'wallet_created_at_id':wallet_created_at_id,
        'wallet_activated_at_id':wallet_activated_at_id,
        'created_at':created_at,
        'last_updated_at':last_updated_at
    })
    conn.register('df_raw', df_raw)

    conn.execute('''INSERT into dim_wallet select * from df_raw''')

    






    