import pandas as pd
import numpy as np

from src.config.paths import (FACT_WALLET_BALANCE_PARQUET_PATH, DDL_FACT_WALLET_BALANCE_PATH)
from src.config.constants import (DEFAULT_SIGNUP_START_TIMESTAMP, DEFAULT_TRANSACTION_START_TIMESTAMP,DEFAULT_WALLET_BALANCE_TOPUP_SIMULATION_START_DATE)
from src.logic.helper_functions import (initial_wallet_balance_creation)

def generate_wallet_balance(conn):

    create_db = DDL_FACT_WALLET_BALANCE_PATH.read_text()

    conn.execute(create_db)

    wallets_data = conn.execute(f'''select wallet_id, user_id, wallet_created_at,wallet_activated_at,last_updated_at from dim_wallet order by wallet_id''').df()

    wallet_ids = wallets_data['wallet_id']
    user_ids = wallets_data['user_id']
    current_wallet_balance = np.zeros(len(wallets_data),dtype=np.float64)
    updated_at = wallets_data['wallet_created_at']
    last_transaction_id = np.full(len(wallets_data), pd.NA, dtype=object)
    created_at = wallets_data['wallet_created_at']
    last_updated_at = wallets_data['last_updated_at']

    df_raw = pd.DataFrame({
        'wallet_id':wallet_ids,
        'user_id':user_ids,
        'current_balance':current_wallet_balance,
        'last_updated_date':last_updated_at,
        'last_updated_date_id':last_updated_at.dt.strftime("%Y%m%d").astype(int),
        'last_transaction_id':last_transaction_id,
        'created_at':created_at,
        'updated_at':updated_at
        
    })

    conn.register('wallet_balance_df', df_raw)

    conn.execute(f'''insert into fact_wallet_balance (wallet_id, user_id, current_balance, last_updated_date,last_updated_date_id, last_transaction_id, created_at, updated_at)
                     select wallet_id, user_id, current_balance, last_updated_date,last_updated_date_id, last_transaction_id, created_at, updated_at from wallet_balance_df''')

    conn.unregister('wallet_balance_df')

    eligible_wallets_df = conn.execute(f'''SELECT w.*, u.customer_behaviour_segment FROM dim_wallet w inner join dim_user u on w.user_id = u.user_id
    WHERE wallet_activated_at between '{DEFAULT_SIGNUP_START_TIMESTAMP}' AND '{DEFAULT_WALLET_BALANCE_TOPUP_SIMULATION_START_DATE}' 
    ORDER BY RANDOM() LIMIT 1000
    ''').df()

    high_nw_segments = ['High_Engagement_High_Balance', 'Moderate_Engagement_High_Balance', 'Low_Engagement_High_Balance']
    low_nw_segments = ['Low_Engagement_Low_Balance','Moderate_Engagement_Low_Balance','High_Engagement_Low_Balance']

    high_nw_users = eligible_wallets_df[eligible_wallets_df['customer_behaviour_segment'].isin(high_nw_segments)].copy()
    low_nw_users = eligible_wallets_df[eligible_wallets_df['customer_behaviour_segment'].isin(low_nw_segments)].copy()

    high_nw_users_df = high_nw_users.sample(frac=0.4)
    low_nw_users_df = low_nw_users.sample(frac=0.1)

    eligible_users_df = pd.concat([high_nw_users_df,low_nw_users_df],axis=0)

    random_offset = np.random.randint(800, 21600, size=len(eligible_users_df))

    eligible_users_df['funding_time'] = (pd.to_datetime(DEFAULT_WALLET_BALANCE_TOPUP_SIMULATION_START_DATE) + pd.to_timedelta(random_offset, unit='m'))

    eligible_users_df = eligible_users_df.sort_values(by='funding_time').reset_index(drop=True)

    eligible_users_df['transaction_ids'] = np.arange(1, len(eligible_users_df) + 1)

    initial_wallet_balance_creation(conn, eligible_users_df)



    




