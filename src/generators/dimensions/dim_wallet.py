import numpy as np
import pandas as pd
from src.config.paths import (DDL_DIM_WALLET_PATH, WALLETS_PARQUET_PATH)
from src.config.constants import (DEFAULT_SIGNUP_START_TIMESTAMP, DEFAULT_TRANSACTION_START_TIMESTAMP)
from datetime import timedelta

def generate_list_of_wallets(conn):
    create_db = DDL_DIM_WALLET_PATH.read_text()

    conn.execute(create_db)

    users_data = conn.execute('''
            SELECT * FROM dim_user order by signup_date ASC
    ''').df()

    users_data = users_data.copy()

    total_users = len(users_data)

    wallet_ids = users_data["user_id"]

    user_ids = users_data["user_id"]

    wallet_created_at = pd.to_datetime(users_data["signup_date"]).dt.tz_localize("UTC")

    assert wallet_created_at.notna().all(), "Wallet creation date cannot be null"

    is_activated_user = users_data["is_activated_user"]
    
    supposed_activation_date = users_data["supposed_activation_date"]

    supposed_activation_date = pd.to_datetime(
    supposed_activation_date
).dt.tz_localize("UTC")

    transaction_start_timestamp = pd.to_datetime(
    DEFAULT_TRANSACTION_START_TIMESTAMP
)

    assert is_activated_user.notna().all(),"Activation status cannot be null"

    active_mask = np.where((is_activated_user == True) & (supposed_activation_date.notna()) &
                           (supposed_activation_date < transaction_start_timestamp))[0]
    
    inactive_mask = np.where(is_activated_user == False)[0]

    activation_timeframe = users_data["wallet_activation_timeframe"]

    assert (activation_timeframe.iloc[active_mask] > 0).all(), "activation timeframe must be greater than 0"

    wallet_activated_at = pd.Series(
    pd.NaT,
    index=range(total_users),
    dtype="datetime64[ns, UTC]"
)


    wallet_activated_at.iloc[active_mask] = supposed_activation_date[active_mask]
    wallet_activated_at.iloc[inactive_mask] = None

    assert (wallet_created_at.iloc[active_mask] < wallet_activated_at.iloc[active_mask]).all(),"Wallet cannot be activated before creation"

    wallet_activated_at_id = pd.Series(pd.NA,index=range(total_users),dtype="Int64")

    wallet_created_at_id = (wallet_created_at.dt.strftime('%Y%m%d').astype("int64"))

    wallet_activated_at_id.iloc[active_mask] = (wallet_activated_at.iloc[active_mask].dt.strftime("%Y%m%d").astype("int64"))

    wallet_currency = "GBP"

    created_at = wallet_created_at

    last_updated_at = users_data["last_updated_at"].copy()

    #last_updated_at = pd.to_datetime(last_updated_at).dt.tz_localize("UTC")
    #last_updated_at[active_mask] = wallet_activated_at[active_mask]

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

    updation_df = df_raw.iloc[active_mask].copy()

    conn.register("updation_df",updation_df)

    conn.execute('''
            UPDATE dim_wallet w set last_updated_at = u.wallet_activated_at from updation_df u where w.wallet_id = u.wallet_id
    ''')

    conn.unregister("updation_df")

    df = conn.execute(f'''SELECT * FROM dim_wallet where wallet_activated_at > '{DEFAULT_TRANSACTION_START_TIMESTAMP}' ''').df()

    print(df.head(50))

    






    