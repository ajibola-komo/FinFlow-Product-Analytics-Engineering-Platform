import numpy as np
import pandas as pd
from src.config.paths import (DDL_FACT_EVENT_PATH, FACT_EVENTS_PARQUET_PATH)
from src.config.constants import (DEFAULT_TRANSACTION_START_TIMESTAMP,DEFAULT_TRANSACTION_START_DATE, DEFAULT_TRANSACTION_END_TIMESTAMP)
from datetime import timedelta


def generate_fact_events(conn, num_of_events):

    create_db = DDL_FACT_EVENT_PATH.read_text()

    conn.execute(create_db)

    users_data = conn.execute(f'''SELECT user_id, signup_date FROM dim_user
     where signup_date >= '{DEFAULT_TRANSACTION_START_DATE}' order by signup_date''').df()

    event_type_lookup = conn.execute(
    '''
    SELECT event_type_code, event_type_id
    FROM dim_event_type
    '''
).df()
    
    event_type_map = dict(zip(
    event_type_lookup["event_type_code"],
    event_type_lookup["event_type_id"]
))

    #event_id, user_id, event_type_id,investment_id wallet_id, event_time,event_date_id

    event_time = np.empty(num_of_events, dtype=object)

    user_ids = np.empty(num_of_events, dtype=object)

    event_type_ids = np.empty(num_of_events, dtype=object)

    total_signups = len(users_data)

    user_ids[:total_signups] = users_data["user_id"]
    event_time[:total_signups] = users_data["signup_date"]
    event_type_ids[:total_signups] = event_type_map["signup_completed"]

    post_registration_logins = total_signups * 2

    signup_dates = users_data["signup_date"] 
    random_offset = np.random.randint(60,300,size=total_signups)
    user_ids[total_signups:post_registration_logins] = users_data["user_id"]
    event_time[total_signups:post_registration_logins] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd, ro in zip(signup_dates, random_offset)]
    event_type_ids[total_signups:post_registration_logins] = event_type_map["app_login"]

    
    activated_users = conn.execute(f'''SELECT * FROM dim_user where kyc_completed = TRUE and signup_date >= '{DEFAULT_TRANSACTION_START_DATE}' order by signup_date''').df()

    total_activated_users = len(activated_users)

    kyc_activated_transactions = post_registration_logins + total_activated_users

    random_offset = np.random.randint(300, 345600, size=total_activated_users)
    activated_users_signup_dates = activated_users["signup_date"]

    user_ids[post_registration_logins:kyc_activated_transactions] = activated_users["user_id"]
    event_time[post_registration_logins:kyc_activated_transactions] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd, ro in zip(activated_users_signup_dates, random_offset)]
    event_type_ids[post_registration_logins:kyc_activated_transactions] = event_type_map["kyc_completed"]

    kyc_completion_time = event_time[post_registration_logins:kyc_activated_transactions]

    kyc_dict = dict(zip(activated_users["user_id"], kyc_completion_time))

    subset_size = int(len(users_data) * 0.6)
    
    customer_subset = conn.execute(f'''SELECT du.user_id, du.signup_date, dw.wallet_id FROM dim_user du
                                   inner join dim_wallet dw
                                   on du.user_id = dw.user_id 
                                   where kyc_completed = TRUE and signup_date >= '{DEFAULT_TRANSACTION_START_DATE}'
                                   limit {subset_size}''').df()
    
    total_wallet_activation_events = len(customer_subset)

    wallet_activation_transactions = kyc_activated_transactions + total_wallet_activation_events

    wallet_ids = np.empty(num_of_events, dtype=object)
    transaction_ids = np.empty(num_of_events, dtype=object)

    random_offset = np.random.randint(60,10080, size=total_wallet_activation_events)

    user_ids[kyc_activated_transactions:wallet_activation_transactions] = customer_subset["user_id"]
    event_time[kyc_activated_transactions:wallet_activation_transactions] = [kyc_dict[uid] + timedelta(minutes=int(ro)) for uid, ro in zip(user_ids[kyc_activated_transactions:wallet_activation_transactions], random_offset)]
    wallet_ids[kyc_activated_transactions:wallet_activation_transactions] = customer_subset["wallet_id"]
    event_type_ids[kyc_activated_transactions:wallet_activation_transactions] = event_type_map["wallet_funded"]
    transaction_ids[kyc_activated_transactions:wallet_activation_transactions] = np.arange(101, total_wallet_activation_events + 101)

    


    #populated_events = pd.notna(event_time)
    
    #valid_event_times = event_time[populated_events]

    event_date_ids = np.empty(num_of_events, dtype=object)

    event_date_ids = np.array([
    int(pd.Timestamp(ts).strftime('%Y%m%d'))
    for ts in event_time
    ], dtype=np.int32)


    investment_id = np.arange(1,num_of_events + 1)

    df_raw = pd.DataFrame({
        "user_id":user_ids,
        "event_type_id":event_type_ids,
        "investment_id":investment_id,
        "wallet_id":wallet_ids,
        "event_time":event_time,
        "event_date_id":event_date_ids
    })

    df_raw = df_raw.sort_values(
    by='event_time'
    ).reset_index(drop=True)

    df_raw['event_id'] = np.arange(
    1,
    len(df_raw) + 1
    )

    df_raw = df_raw[[
        "event_id",
        "user_id",
        "event_type_id",
        "investment_id",
        "wallet_id",
        "event_time",
        "event_date_id"
    ]]

    conn.register("df_raw",df_raw)

    conn.execute('''INSERT INTO fact_event SELECT * FROM df_raw''')

    conn.execute(f'''COPY FACT_EVENT TO '{FACT_EVENTS_PARQUET_PATH}' (FORMAT PARQUET) ''')