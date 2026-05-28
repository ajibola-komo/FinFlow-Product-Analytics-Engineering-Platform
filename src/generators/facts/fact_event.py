import numpy as np
import pandas as pd
from src.config.paths import (DDL_FACT_EVENT_PATH, FACT_EVENTS_PARQUET_PATH)
from src.config.constants import (DEFAULT_TRANSACTION_START_TIMESTAMP,DEFAULT_TRANSACTION_START_DATE, DEFAULT_TRANSACTION_END_TIMESTAMP,
                                  POST_SIGN_UP_DELAYED_LOGINS, POST_SIGN_UP_IMMEDIATE_LOGINS, POST_SIGN_UP_SAME_DAY_LOGINS,
                                  IMMEDIATE_LOGINS_TIME_FRAME, SAME_DAY_LOGINS_TIME_FRAME, DELAYED_LOGINS_TIME_FRAME, 
                                  UNACTIVATED_USERS_TIME_FRAME, WALLET_ACTIVATION_SUBSET, IMMEDIATE_WALLET_ACTIVATION_TIME_FRAME, 
                                  DELAYED_WALLET_ACTIVATION_TIME_FRAME, IMMEDIATE_ACTIVATION_SUBSET
                                  )
from datetime import timedelta


def generate_fact_events(conn, num_of_events):

    create_db = DDL_FACT_EVENT_PATH.read_text()

    conn.execute(create_db)

    #populate all possible signups within the project uration
    users_data = conn.execute(f'''SELECT user_id, signup_date, kyc_completed FROM dim_user
     where signup_date >= '{DEFAULT_TRANSACTION_START_DATE}' order by signup_date''').df()
    
    user_wallet_data = conn.execute(f'''SELECT user_id, wallet_id from dim_wallet''').df()

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
    
    wallet_id_map = dict(zip(
        user_wallet_data["user_id"],
        user_wallet_data["wallet_id"]
    ))

    #event_id, user_id, event_type_id,investment_id wallet_id, event_time,event_date_id

    event_time = np.empty(num_of_events, dtype=object)

    user_ids = np.empty(num_of_events, dtype=object)

    event_type_ids = np.empty(num_of_events, dtype=object)

    wallet_ids = np.empty(num_of_events, dtype=object)

    transaction_ids = np.empty(num_of_events, dtype=object)

    investment_ids = np.empty(num_of_events, dtype=object)


    total_signups = len(users_data)

    user_ids[:total_signups] = users_data["user_id"]
    event_time[:total_signups] = users_data["signup_date"]
    event_type_ids[:total_signups] = event_type_map["signup_completed"]

    

    signups_df = pd.DataFrame(
        {
            "user_id": users_data["user_id"],
            "signup_date":users_data["signup_date"],
            "kyc_completed":users_data["kyc_completed"]
        }
    )

    signups_df = signups_df.sample(frac=1).reset_index(drop=True)

    activated_df = signups_df[signups_df["kyc_completed"] == True].copy()

    activated_df["login_segment"] = np.random.choice(
    ["immediate", "same_day", "delayed"],
    size=len(activated_df),
    p=[POST_SIGN_UP_IMMEDIATE_LOGINS, POST_SIGN_UP_SAME_DAY_LOGINS, POST_SIGN_UP_DELAYED_LOGINS]
)

    #immediate logins
    immediate_logins_df = activated_df[activated_df["login_segment"] == "immediate"].copy()
    n_immediate = len(immediate_logins_df)
    immediate_end  = total_signups + n_immediate
    
    

    random_offset = np.random.randint(IMMEDIATE_LOGINS_TIME_FRAME[0],IMMEDIATE_LOGINS_TIME_FRAME[1],size=len(immediate_logins_df))
    user_ids[total_signups:immediate_end] = immediate_logins_df["user_id"]
    signup_dates = immediate_logins_df["signup_date"]
    event_time[total_signups:immediate_end] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd, ro in zip(signup_dates, random_offset)]
    event_type_ids[total_signups:immediate_end] = event_type_map["app_login"]

    #same day logins
    same_day_logins_df = activated_df[activated_df["login_segment"] == "same_day"].copy()
    n_same_day  = len(same_day_logins_df)
    same_day_end   = immediate_end + n_same_day
    random_offset = np.random.randint(SAME_DAY_LOGINS_TIME_FRAME[0],SAME_DAY_LOGINS_TIME_FRAME[1], size=len(same_day_logins_df))
    user_ids[immediate_end:same_day_end] = same_day_logins_df["user_id"]
    signup_dates = same_day_logins_df["signup_date"]
    event_time[immediate_end:same_day_end] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd,ro in zip(signup_dates, random_offset)]
    event_type_ids[immediate_end:same_day_end] = event_type_map["app_login"]

    #delayed logins
    delayed_logins_df = activated_df[activated_df["login_segment"] == "delayed"].copy()
    n_delayed   = len(delayed_logins_df)
    delayed_end    = same_day_end  + n_delayed
    random_offset = np.random.randint(DELAYED_LOGINS_TIME_FRAME[0],DELAYED_LOGINS_TIME_FRAME[1], size=len(delayed_logins_df))
    user_ids[same_day_end:delayed_end] = delayed_logins_df["user_id"]
    signup_dates = delayed_logins_df["signup_date"]
    event_time[same_day_end:delayed_end] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd,ro in zip(signup_dates, random_offset)]
    event_type_ids[same_day_end:delayed_end] = event_type_map["app_login"]

    unactivated_users_df = signups_df[signups_df["kyc_completed"] == False].copy()
    unactivated_users_df = unactivated_users_df.sample(frac=0.2).reset_index(drop=True)

    unactivated_users_login = len(unactivated_users_df)
    unactivated_end = delayed_end + unactivated_users_login

    random_offset = np.random.randint(UNACTIVATED_USERS_TIME_FRAME[0],UNACTIVATED_USERS_TIME_FRAME[1], size=unactivated_users_login)

    user_ids[delayed_end:unactivated_end] = unactivated_users_df["user_id"]
    signup_dates = unactivated_users_df["signup_date"]
    event_time[delayed_end:unactivated_end] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd,ro in zip(signup_dates, random_offset)]
    event_type_ids[delayed_end:unactivated_end] = event_type_map["app_login"]

    immediate_logins_df["last_login_time"] = event_time[total_signups:immediate_end]
    same_day_logins_df["last_login_time"] = event_time[immediate_end:same_day_end]
    delayed_logins_df["last_login_time"] = event_time[same_day_end:delayed_end]
    
    kyc_completed_users = pd.concat([immediate_logins_df,same_day_logins_df, delayed_logins_df], ignore_index=True)

    total_activated_users = len(kyc_completed_users)

    kyc_activated_transactions = unactivated_end + total_activated_users

    random_offset = np.random.randint(300, 345600, size=total_activated_users)

    user_ids[unactivated_end:kyc_activated_transactions] = kyc_completed_users["user_id"]
    event_time[unactivated_end:kyc_activated_transactions] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd, ro in zip(kyc_completed_users["last_login_time"], random_offset)]
    event_type_ids[unactivated_end:kyc_activated_transactions] = event_type_map["kyc_completed"]

    kyc_completion_time = event_time[unactivated_end:kyc_activated_transactions]

    #wallet activation
    kyc_dict = dict(zip(kyc_completed_users["user_id"], kyc_completion_time))
    
    customer_subset_df = kyc_completed_users.sample(frac=WALLET_ACTIVATION_SUBSET, random_state=42)

    split_index = int(len(customer_subset_df) * IMMEDIATE_ACTIVATION_SUBSET)

    immediate_wallet_activation_df = customer_subset_df.iloc[:split_index]
    delayed_wallet_activation_df = customer_subset_df.iloc[split_index:]
    
    immediate_wallet_activation_events = len(immediate_wallet_activation_df)

    immediate_wallet_activation_transactions = kyc_activated_transactions + immediate_wallet_activation_events


    random_offset = np.random.randint(IMMEDIATE_WALLET_ACTIVATION_TIME_FRAME[0],IMMEDIATE_WALLET_ACTIVATION_TIME_FRAME[1], size=immediate_wallet_activation_events)

    uids = immediate_wallet_activation_df["user_id"].values

    user_ids[kyc_activated_transactions:immediate_wallet_activation_transactions] = immediate_wallet_activation_df["user_id"]
    event_time[kyc_activated_transactions:immediate_wallet_activation_transactions] = [kyc_dict[uid] + timedelta(minutes=int(ro)) for uid, ro in zip(user_ids[kyc_activated_transactions:immediate_wallet_activation_transactions], random_offset)]
    wallet_ids[kyc_activated_transactions:immediate_wallet_activation_transactions] = [wallet_id_map.get(uid) for uid in uids]
    event_type_ids[kyc_activated_transactions:immediate_wallet_activation_transactions] = event_type_map["wallet_funded"]
    transaction_ids[kyc_activated_transactions:immediate_wallet_activation_transactions] = np.arange(101, immediate_wallet_activation_transactions + 101)

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