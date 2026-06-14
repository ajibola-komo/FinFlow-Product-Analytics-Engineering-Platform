import numpy as np
import pandas as pd
from src.config.paths import (DDL_FACT_USER_EVENT_PATH, FACT_USER_EVENT_PARQUET_PATH)
from src.config.constants import (DEFAULT_TRANSACTION_START_TIMESTAMP,DEFAULT_TRANSACTION_START_DATE, DEFAULT_TRANSACTION_END_TIMESTAMP,
                                  POST_SIGN_UP_DELAYED_LOGINS, POST_SIGN_UP_IMMEDIATE_LOGINS, POST_SIGN_UP_SAME_DAY_LOGINS,
                                  IMMEDIATE_LOGINS_TIME_FRAME, SAME_DAY_LOGINS_TIME_FRAME, DELAYED_LOGINS_TIME_FRAME, 
                                  UNACTIVATED_USERS_TIME_FRAME, WALLET_ACTIVATION_SUBSET, IMMEDIATE_WALLET_ACTIVATION_TIME_FRAME, 
                                  DELAYED_WALLET_ACTIVATION_TIME_FRAME, IMMEDIATE_ACTIVATION_SUBSET, DELAYED_WALLET_ACTIVATION_LOGIN_TIME_FRAME,
                                  KYC_ACTIVATION_TIMEFRAME
                                  )
from datetime import timedelta


def generate_fact_events(conn, num_of_events):

    create_db = DDL_FACT_USER_EVENT_PATH.read_text()

    conn.execute(create_db)

    #populate all possible signups within the project uration
    users_data = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, wallet_activation_timeframe, customer_behaviour_segment FROM dim_user
     where signup_date >= '{DEFAULT_TRANSACTION_START_DATE}' order by signup_date''').df()
    
    user_wallet_data = conn.execute(f'''SELECT user_id, wallet_id, wallet_activated_at from dim_wallet''').df()

    event_type_lookup = conn.execute(
    '''
    SELECT event_type_code, event_type_id
    FROM dim_event_type
    '''
).df()
    
    transaction_type_lookup = conn.execute(
        '''
            SELECT transaction_type_code, transaction_type_id
            FROM dim_transaction_type
        '''
    ).df()
    
    event_type_map = dict(zip(
    event_type_lookup["event_type_code"],
    event_type_lookup["event_type_id"]
))
    
    transaction_type_map = dict(zip(
    transaction_type_lookup["transaction_type_code"],
    transaction_type_lookup["transaction_type_id"]
    ))
    
    wallet_id_map = dict(zip(
        user_wallet_data["user_id"],
        user_wallet_data["wallet_id"]
    ))

    #event_id (PK), user_id, event_type_id, wallet_id, plan_id,event_time ,event_date_id,device_type,is_money_movement_activity
    #transaction_type_id, transaction_id, investment_id

    event_time = np.empty(num_of_events, dtype=object)

    user_ids = np.empty(num_of_events, dtype=object)

    event_type_ids = np.empty(num_of_events, dtype=object)

    wallet_ids = np.empty(num_of_events, dtype=object)

    plan_ids = np.empty(num_of_events, dtype=object)

    device_types = np.empty(num_of_events, dtype=object)

    is_money_movement_activities = np.empty(num_of_events, dtype=bool)

    transaction_type_ids = np.empty(num_of_events, dtype=object)

    transaction_ids = np.empty(num_of_events, dtype=object)

    investment_ids = np.empty(num_of_events, dtype=object)

    event_date_ids = np.empty(num_of_events, dtype=object)


    # new user signups
    total_signups = len(users_data)

    user_ids[:total_signups] = users_data["user_id"]
    event_time[:total_signups] = users_data["signup_date"]
    event_type_ids[:total_signups] = event_type_map.get("signup_completed")

    new_users_logins = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, customer_behaviour_segment FROM dim_user
     where signup_date >= '{DEFAULT_TRANSACTION_START_DATE}' AND is_immediate_login = True order by signup_date''').df()
    
    immediate_login_timeframe = np.random.randint(IMMEDIATE_LOGINS_TIME_FRAME[0],IMMEDIATE_LOGINS_TIME_FRAME[1], size=len(new_users_logins))
    
    total_new_users = len(new_users_logins)

    start_immediate_logins = total_signups
    end_immediate_logins = start_immediate_logins + total_new_users

    user_ids[start_immediate_logins:end_immediate_logins] = new_users_logins["user_id"]
    event_time[start_immediate_logins:end_immediate_logins] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd, ro in zip(new_users_logins["signup_date"], immediate_login_timeframe)]
    event_type_ids[start_immediate_logins:end_immediate_logins] = event_type_map.get("app_login")


    kyc_completed_users = users_data[users_data["kyc_completed"] == True].copy()

    signup_map = dict(zip(
    users_data["user_id"],
    users_data["signup_date"]
))

    last_login_map  = dict(zip(
        user_ids[start_immediate_logins:end_immediate_logins],
        event_time[start_immediate_logins:end_immediate_logins]
    ))

    kyc_activation_timeframe = np.empty(len(kyc_completed_users), dtype=object)
    
    unactivated_users_with_kyc = np.where(pd.isna(kyc_completed_users["wallet_activation_timeframe"]))[0]

    activated_users_with_kyc = np.where(~pd.isna(kyc_completed_users["wallet_activation_timeframe"]))[0]

    wallet_activation_timeframe = kyc_completed_users["wallet_activation_timeframe"].values

    kyc_activation_timeframe[unactivated_users_with_kyc] = np.random.randint(KYC_ACTIVATION_TIMEFRAME[0], KYC_ACTIVATION_TIMEFRAME[1], size=len(unactivated_users_with_kyc))
    kyc_activation_timeframe[activated_users_with_kyc] = wallet_activation_timeframe[activated_users_with_kyc] - 1000 #assuming wallet activation happens after KYC completion, we can set the KYC activation timeframe to be slightly less than the wallet activation timeframe for those users

    kyc_logins_timeframe = kyc_activation_timeframe - 300 #assuming KYC completion happens after the last login, we can set the KYC activation timeframe to be slightly more than the last login timeframe

    start_kyc_activations = end_immediate_logins
    end_kyc_activations = start_kyc_activations + len(kyc_completed_users)

    user_ids[start_kyc_activations:end_kyc_activations] = kyc_completed_users["user_id"]
    event_time[start_kyc_activations:end_kyc_activations] = [last_login_map.get(uid,signup_map.get(uid)) + timedelta(minutes=int(ro)) for uid, ro in zip(kyc_completed_users["user_id"], kyc_logins_timeframe)]
    event_type_ids[start_kyc_activations:end_kyc_activations] = event_type_map.get("app_login")

    start_kyc_activation_completion = end_kyc_activations
    end_kyc_activation_completion = start_kyc_activation_completion + len(kyc_completed_users)

    user_ids[start_kyc_activation_completion:end_kyc_activation_completion] = kyc_completed_users["user_id"]
    event_time[start_kyc_activation_completion:end_kyc_activation_completion] = [last_login_map.get(uid,signup_map.get(uid)) + timedelta(minutes=int(ro)) for uid, ro in zip(kyc_completed_users["user_id"], kyc_activation_timeframe)]
    event_type_ids[start_kyc_activation_completion:end_kyc_activation_completion] = event_type_map.get("kyc_completed")

    kyc_completion_time = event_time[start_kyc_activation_completion:end_kyc_activation_completion]

    #wallet activation
    kyc_dict = dict(zip(kyc_completed_users["user_id"], kyc_completion_time))
    
    wallet_activated_users = kyc_completed_users[~pd.isna(kyc_completed_users["wallet_activation_timeframe"])].copy()

    total_wallet_activated_users = len(wallet_activated_users)

    start_wallet_activations = end_kyc_activation_completion
    end_wallet_activations = start_wallet_activations + total_wallet_activated_users

    user_ids[start_wallet_activations:end_wallet_activations] = wallet_activated_users["user_id"]
    event_time[start_wallet_activations:end_wallet_activations] = [kyc_dict.get(uid,None) + timedelta(minutes=int(ro)) for uid, ro in zip(wallet_activated_users["user_id"], wallet_activated_users["wallet_activation_timeframe"])]
    event_type_ids[start_wallet_activations:end_wallet_activations] = event_type_map.get("wallet_funded")
    is_money_movement_activities[start_wallet_activations:end_wallet_activations] = True
    wallet_ids[start_wallet_activations:end_wallet_activations] = [wallet_id_map.get(uid) for uid in wallet_activated_users["user_id"]]
    transaction_type_ids[start_wallet_activations:end_wallet_activations] = transaction_type_map.get("wallet_funding")
    transaction_ids[start_wallet_activations:end_wallet_activations] = np.arange(1, total_wallet_activated_users + 1)
    last_transaction_id = transaction_ids[start_wallet_activations:end_wallet_activations].max()

    wallet_activated_users_df = pd.DataFrame(
        {
            "user_id": user_ids[start_wallet_activations:end_wallet_activations],
            "last_login_time": event_time[start_wallet_activations:end_wallet_activations]
        }
    )

    #let's create the initial investment -- login, review_plan_options then drop off for some users, and for others, they will make an investment after reviewing the plan options. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.

    segment_customers = dict(zip(
        users_data["user_id"],
        users_data["customer_behaviour_segment"]
    ))

    wallet_activated_users_df = pd.DataFrame({
        "user_id": wallet_activated_users_df["user_id"],
        "customer_behaviour_segment": wallet_activated_users_df["user_id"].map(segment_customers),
        "last_login_time": wallet_activated_users_df["last_login_time"]})
    
    customer_subset_1 = wallet_activated_users_df.sample(frac = 0.55, random_state=1)

    total_customer_subset_1 = len(customer_subset_1)

    #these users will just login and review plan options, but will not make an investment. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.

    start_position = end_wallet_activations
    end_position = start_position + total_customer_subset_1

    user_ids[start_position:end_position] = customer_subset_1["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(5, 80)) for last_login in customer_subset_1["last_login_time"]]
    event_type_ids[start_position:end_position] = event_type_map.get("app_login")

    login_time_for_review_plan_options = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_1

    user_ids[start_position:end_position] = customer_subset_1["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(2, 5)) for last_login in login_time_for_review_plan_options]
    event_type_ids[start_position:end_position] = event_type_map.get("review_plan_options")

    customer_subset_2 = wallet_activated_users_df.sample(frac = 0.65, random_state=1)

    total_customer_subset_2 = len(customer_subset_2)

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(600, 1440)) for last_login in customer_subset_2["last_login_time"]]
    event_type_ids[start_position:end_position] = event_type_map.get("app_login")

    login_time_for_review_plan_options_2 = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(2, 5)) for last_login in login_time_for_review_plan_options_2]
    event_type_ids[start_position:end_position] = event_type_map.get("review_plan_options")

    last_review_time_for_investment = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_review + timedelta(minutes=np.random.randint(1, 3)) for last_review in last_review_time_for_investment]
    event_type_ids[start_position:end_position] = event_type_map.get("plan_selected")


    
    

    event_date_ids = np.array([
    int(pd.Timestamp(ts).strftime('%Y%m%d'))
    for ts in event_time
    ], dtype=np.int32)


    investment_ids = np.arange(1,num_of_events + 1)

    registered_money_movement = pd.notna(wallet_ids)

    money_movement_transactions = registered_money_movement.sum()

    transaction_ids[registered_money_movement] = np.arange(156, money_movement_transactions + 1)

    df_raw = pd.DataFrame({
        "user_id":user_ids,
        "event_type_id":event_type_ids,
        "investment_id":investment_ids,
        "wallet_id":wallet_ids,
        "event_time":event_time,
        "event_date_id":event_date_ids,
        "transaction_id":transaction_ids
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

    conn.execute(f'''COPY FACT_EVENT TO '{FACT_USER_EVENT_PARQUET_PATH}' (FORMAT PARQUET) ''')