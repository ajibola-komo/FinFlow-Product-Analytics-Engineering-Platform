import pandas as pd
import numpy as np

from incremental_generator.config.constants import (GENERATION_START_DATE, GENERATION_START_TIMESTAMP, GENERATION_END_TIMESTAMP)


def generate_wallet_balance(conn):

    wallets_data = conn.execute(f'''
            SELECT wallet_id, user_id, wallet_created_at from dim_wallet where wallet_created_at between '{GENERATION_START_TIMESTAMP}'
            AND '{GENERATION_END_TIMESTAMP}'
    ''').df()

    wallet_ids = wallets_data['wallet_id']
    user_ids = wallets_data['user_id']
    current_wallet_balance = np.zeros(len(wallets_data))
    updated_at = wallets_data['wallet_created_at']
    last_transaction_id = np.empty(len(wallets_data), dtype=object)
    last_event_id = np.empty(len(wallets_data), dtype=object)
    created_at = wallets_data['wallet_created_at']
    last_updated_at = wallets_data['wallet_created_at']

    df_raw = pd.DataFrame({
        'wallet_id':wallet_ids,
        'user_id':user_ids,
        'current_balance':current_wallet_balance,
        'updated_at':updated_at,
        'last_transaction_id':last_transaction_id,
        'last_event_id':last_event_id,
        'created_at':created_at,
        'last_updated_at':last_updated_at
    })

    conn.register('wallet_balance_df', df_raw)

    conn.execute(f'''insert into fact_wallet_balance (wallet_id, user_id, current_balance, updated_at, last_transaction_id, last_event_id, created_at, last_updated_at)
                     select wallet_id, user_id, current_balance, updated_at, last_transaction_id, last_event_id, created_at, last_updated_at from wallet_balance_df''')
    

    conn.unregister('wallet_balance_df')
    