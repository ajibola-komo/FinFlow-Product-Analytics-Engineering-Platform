import numpy as np
import pandas as pd
from incremental_generator.config.paths import (CURRENT_FACT_USER_EVENT_PARQUET_PATH, CURRENT_FACT_INVESTMENT_POSITION_PARQUET_PATH, CURRENT_FACT_TRANSACTION_PARQUET_PATH)
from incremental_generator.config.constants import (IMMEDIATE_LOGINS_TIME_FRAME, KYC_ACTIVATION_TIMEFRAME, USERS_MAKES_FIRST_INVESTMENT_AFTER_FUNDING,
                                  CUSTOMER_BEHAVIOUR_SEGMENT_MAP, FIRST_INVESTMENT_TYPE, EARLY_WITHDRAWAL_BEHAVIOUR, INVESTMENT_WITHDRAWAL_PROCESSING_TIME,
                                  MUTUAL_FUNDS_CUTOFF_DATE, TODAY, GENERATION_START_TIMESTAMP, GENERATION_END_TIMESTAMP, GENERATION_START_DATE)
                                  
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from incremental_generator.generators.facts.helper_functions import (update_last_login_timestamp, update_kyc_completion_status, update_wallet_balance_topup,
debit_wallet_balance, wallet_activation_funding, get_current_wallet_balance )


def generate_facts(conn, num_of_events):

    #populate all possible signups within the project duration
    new_signups_data = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, 
                              wallet_activation_timeframe, customer_behaviour_segment, device_type, is_immediate_login
                              FROM dim_user
     where signup_date BETWEEN '{GENERATION_START_TIMESTAMP}' AND '{GENERATION_END_TIMESTAMP}' order by signup_date''').df()
    
    all_users_data = conn.execute('''SELECT user_id, signup_date, customer_behaviour_segment, device_type,supposed_activation_date, kyc_completion_date  FROM dim_user order by signup_date''').df()
    all_wallets_data = conn.execute('''SELECT user_id, wallet_id, wallet_created_at, wallet_activated_at from dim_wallet order by wallet_created_at''').df()

    last_investment_id = conn.execute('''SELECT coalesce(max(investment_id),0) as investment_id from fact_investment_position''').fetchone()[0]

    plans_data = conn.execute('''SELECT * FROM dim_plan''').df()

    device_type_map = dict(zip(all_users_data["user_id"],all_users_data["device_type"]))

    event_type_lookup = conn.execute('''SELECT event_type_code, event_type_id FROM dim_event_type''').df()
    
    transaction_type_lookup = conn.execute('''SELECT transaction_type_code, transaction_type_id FROM dim_transaction_type''').df()
    
    event_type_map = dict(zip(event_type_lookup["event_type_code"],event_type_lookup["event_type_id"]))
    
    transaction_type_map = dict(zip(transaction_type_lookup["transaction_type_code"],transaction_type_lookup["transaction_type_id"]))
    
    wallet_id_map = dict(zip(all_wallets_data["user_id"],all_wallets_data["wallet_id"]))

    plan_id_map = dict(zip(plans_data["plan_id"],plans_data["tenure_days"]))

    event_time = np.empty(num_of_events, dtype=object)

    user_ids = np.empty(num_of_events, dtype=object)

    event_type_ids = np.empty(num_of_events, dtype=object)

    wallet_ids = np.empty(num_of_events, dtype=object)

    plan_ids = np.empty(num_of_events, dtype=object)

    device_types = np.empty(num_of_events, dtype=object)

    amount_invested = np.empty(num_of_events,dtype = object)

    is_money_movement_activities = np.empty(num_of_events, dtype=bool)

    transaction_type_ids = np.empty(num_of_events, dtype=object)

    transaction_ids = np.empty(num_of_events, dtype=object)

    investment_ids = np.empty(num_of_events, dtype=object)

    transaction_amounts = np.zeros(num_of_events, dtype=np.float64)
    transaction_statuses = np.empty(num_of_events, dtype = object)
    is_withdrawn_early = np.full(num_of_events,False,dtype=bool)
    withdrawal_date = np.empty(num_of_events,dtype=object)
    last_event_id = conn.execute('''select max(event_id) from fact_user_event''').fetchone()[0]
    event_ids = np.empty(num_of_events,dtype=object)
    # new user signups
    total_signups = len(new_signups_data)

    user_ids[:total_signups] = new_signups_data["user_id"]
    event_time[:total_signups] = new_signups_data["signup_date"]
    event_type_ids[:total_signups] = event_type_map.get("signup_completed")
    device_types[:total_signups] = np.array([device_type_map.get(uid) for uid in new_signups_data["user_id"]])
    event_ids[:total_signups] = np.arange(last_event_id + 1, last_event_id + total_signups + 1)
    last_event_id = event_ids[:total_signups].max()

    #new user logins
    new_users_logins = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, customer_behaviour_segment,
                                    is_immediate_login FROM dim_user where signup_date 
                                    BETWEEN '{GENERATION_START_TIMESTAMP}' AND '{GENERATION_END_TIMESTAMP}' AND 
                                    is_immediate_login = True order by signup_date''').df()
    
    #post signup immediate logins 
    immediate_login_timeframe = np.random.randint(IMMEDIATE_LOGINS_TIME_FRAME[0],IMMEDIATE_LOGINS_TIME_FRAME[1], size=len(new_users_logins))
    
    total_new_users = len(new_users_logins)

    start_immediate_logins = total_signups
    end_immediate_logins = start_immediate_logins + total_new_users

    user_ids[start_immediate_logins:end_immediate_logins] = new_users_logins["user_id"]
    event_time[start_immediate_logins:end_immediate_logins] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd, ro in zip(new_users_logins["signup_date"], immediate_login_timeframe)]
    event_type_ids[start_immediate_logins:end_immediate_logins] = event_type_map.get("app_login")
    device_types[start_immediate_logins:end_immediate_logins] = np.array([device_type_map.get(uid) for uid in new_users_logins["user_id"]])
    event_ids[start_immediate_logins:end_immediate_logins] = np.arange(last_event_id + 1, 1 + last_event_id + total_new_users)
    last_event_id = event_ids[start_immediate_logins:end_immediate_logins].max()

    update_last_login_timestamp(conn,new_users_logins["user_id"].values,event_time[start_immediate_logins:end_immediate_logins])

    #kyc_completed_users
    sure_kyc_completed_users = conn.execute(f'''SELECT user_id, kyc_completed, device_type, kyc_completion_date from dim_user 
                                            where kyc_completion_date::DATE = '{GENERATION_START_DATE}' ''').df()

    
    kyc_activation_time =  sure_kyc_completed_users["kyc_completion_date"]#assuming wallet activation happens after KYC completion, we can set the KYC activation timeframe to be slightly less than the wallet activation timeframe for those users

    kyc_logins_time = kyc_activation_time - pd.to_timedelta(10,unit="m") #assuming KYC completion happens after the last login, we can set the KYC activation timeframe to be slightly more than the last login timeframe

    start_position = end_immediate_logins
    end_position = start_position + len(sure_kyc_completed_users)

    user_ids[start_position:end_position] = sure_kyc_completed_users["user_id"]
    event_time[start_position:end_position] = kyc_logins_time
    event_type_ids[start_position:end_position] = event_type_map.get("app_login")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in sure_kyc_completed_users["user_id"]])
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, 1 + last_event_id + len(sure_kyc_completed_users))
    last_event_id = event_ids[start_position:end_position].max()

    update_last_login_timestamp(conn,sure_kyc_completed_users["user_id"],event_time[start_position:end_position])


    start_position = end_position
    end_position = start_position + len(sure_kyc_completed_users)

    user_ids[start_position:end_position] = sure_kyc_completed_users["user_id"]
    event_time[start_position:end_position] = sure_kyc_completed_users["kyc_completion_date"]
    event_type_ids[start_position:end_position] = event_type_map.get("kyc_completed")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in sure_kyc_completed_users["user_id"]])
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, 1 + last_event_id + len(sure_kyc_completed_users))
    last_event_id = event_ids[start_position:end_position].max()

    update_kyc_completion_status(conn,sure_kyc_completed_users["user_id"])

    #wallet activation
    wallet_activation_events = conn.execute(f'''SELECT * FROM dim_user where supposed_activation_date::DATE = '{GENERATION_START_DATE}' ''').df()

    segment_customers = dict(zip(
        wallet_activation_events["user_id"],
        wallet_activation_events["customer_behaviour_segment"]
    ))

    wallet_activation_events["customer_behaviour_segment"] = wallet_activation_events["user_id"].map(segment_customers)

    wallet_activation_events["transaction_amount"] = np.array([
        np.random.randint(CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["average_investment_amount"][0],
            CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["average_investment_amount"][1]
            
        )
        for bh in wallet_activation_events["customer_behaviour_segment"]
    ])

    total_wallet_activated_events = len(wallet_activation_events)
    last_transaction_id = conn.execute('''SELECT coalesce(max(transaction_id),0) from fact_transaction''').fetchone()[0]

    #wallet activation

    start_wallet_activations = end_position
    end_wallet_activations = start_wallet_activations + total_wallet_activated_events

    user_ids[start_wallet_activations:end_wallet_activations] = wallet_activation_events["user_id"]
    event_time[start_wallet_activations:end_wallet_activations] = wallet_activation_events["supposed_activation_date"]
    event_type_ids[start_wallet_activations:end_wallet_activations] = event_type_map.get("wallet_funded")
    is_money_movement_activities[start_wallet_activations:end_wallet_activations] = True
    wallet_ids[start_wallet_activations:end_wallet_activations] = [wallet_id_map.get(uid) for uid in wallet_activation_events["user_id"]]
    transaction_type_ids[start_wallet_activations:end_wallet_activations] = [transaction_type_map.get("wallet_funding") for _ in range(len(wallet_activation_events))]
    transaction_ids[start_wallet_activations:end_wallet_activations] = np.arange(last_transaction_id + 1, last_transaction_id + total_wallet_activated_events + 1)
    last_transaction_id = transaction_ids[start_wallet_activations:end_wallet_activations].max()
    device_types[start_wallet_activations:end_wallet_activations] = np.array([device_type_map.get(uid) for uid in wallet_activation_events["user_id"]])
    transaction_statuses[start_wallet_activations:end_wallet_activations] = ["success"]* len(wallet_activation_events)
    transaction_amounts[start_wallet_activations:end_wallet_activations] = wallet_activation_events["transaction_amount"]
    event_ids[start_wallet_activations:end_wallet_activations] = np.arange(last_event_id + 1, 1 + last_event_id + total_wallet_activated_events)
    last_event_id = event_ids[start_wallet_activations:end_wallet_activations].max()

    wallet_user_ids = wallet_activation_events["user_id"]
    amount = wallet_activation_events["transaction_amount"]
    updated_at = wallet_activation_events["supposed_activation_date"]
    tran_ids = transaction_ids[start_wallet_activations:end_wallet_activations]
    ev_ids = event_ids[start_wallet_activations:end_wallet_activations]

    wallet_activation_funding(conn, wallet_user_ids, amount, updated_at, tran_ids, ev_ids)

    #let's model investment vesting events
    vestable_investments = conn.execute(F'''SELECT * from fact_investment_position where investment_maturity_date::DATE = '{GENERATION_START_DATE}' ''').df()

    start_position = end_position
    end_position = start_position + len(vestable_investments)

    user_ids[start_position:end_position] = vestable_investments['user_id'].values
    event_time[start_position:end_position] = vestable_investments['investment_maturity_date']
    event_type_ids[start_position:end_position] = [event_type_map.get('investment_vests')] * len(vestable_investments)
    device_types[start_position:end_position] = [device_type_map.get(uid) for uid in vestable_investments['user_id'].values]
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, 1 + last_event_id + len(vestable_investments))
    last_event_id = event_ids[start_position:end_position].max()

    #investment proceeds wallet transfer

    start_position = end_position
    end_position = start_position + len(vestable_investments)
    
    user_ids[start_position:end_position] = vestable_investments['user_id'].values
    event_time[start_position:end_position] = vestable_investments['investment_maturity_date'] + pd.to_timedelta(3,unit='h')
    event_type_ids[start_position:end_position] = [event_type_map.get('investment_proceeds_wallet_transfer')] * len(vestable_investments)
    device_types[start_position:end_position] = [device_type_map.get(uid) for uid in vestable_investments['user_id'].values]

    wallet_ids[start_position:end_position] = [wallet_id_map.get(uid) for uid in vestable_investments['user_id'].values]
    is_money_movement_activities[start_position:end_position] = True
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, 1 + len(vestable_investments) +  last_transaction_id)
    last_transaction_id = transaction_ids[start_position:end_position].max()
    amount_invested[start_position:end_position] = vestable_investments["amount_invested"]
    transaction_type_ids[start_position:end_position] = [transaction_type_map.get("investment_proceeds_transfer") for _ in range(len(vestable_investments))]
    investment_ids[start_position:end_position] = vestable_investments["investment_id"]
    transaction_amounts[start_position:end_position] = vestable_investments["amount_invested"]
    transaction_statuses[start_position:end_position] = ["success" for _ in range(len(vestable_investments))]
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, 1 + last_event_id + len(vestable_investments))
    last_event_id = event_ids[start_position:end_position].max()

    conn.register("vestable_investment_ids",vestable_investments[["investment_id"]])

    conn.execute('''
        UPDATE fact_investment_position f set investment_status = 'Redeemed' from vestable_investment_ids v where f.investment_id = v.investment_id
    ''')

    conn.unregister('vestable_investment_ids')

    #people that create investments
    all_users = conn.execute(f'''SELECT w.user_id as user_id, u.customer_behaviour_segment, i.user_id as unused FROM dim_wallet w join dim_user u on 
                             w.user_id = u.user_id left join fact_investment_position i on i.user_id = u.user_id where w.wallet_activated_at::DATE 
    between '{GENERATION_START_DATE}' - interval 7 day and '{GENERATION_START_DATE}' - interval 1 day and i.user_id is null ''').df()
    
    #these users will just login and review plan options, but will not make an investment. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.
    customer_subset_1 = all_users.sample(frac = 0.7, random_state=1)

    #these are the users that will create an investment today
    customer_subset_2 = all_users.drop(customer_subset_1.index)

    total_customer_subset_1 = len(customer_subset_1)

    random_offset = np.random.randint(0,1440,size=total_customer_subset_1)

    #these users will just login and review plan options, but will not make an investment. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.

    start_position = end_position
    end_position = start_position + total_customer_subset_1

    user_ids[start_position:end_position] = customer_subset_1["user_id"]
    event_time[start_position:end_position] = [GENERATION_START_DATE + pd.to_timedelta(ro,unit="m") for ro in random_offset]
    event_type_ids[start_position:end_position] = event_type_map.get("app_login")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_1["user_id"]])
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, last_event_id + 1 + total_customer_subset_1 )
    last_event_id = event_ids[start_position:end_position].max() 

    login_time_for_review_plan_options = event_time[start_position:end_position]

    update_last_login_timestamp(conn,user_ids[start_position:end_position], login_time_for_review_plan_options)

    start_position = end_position
    end_position = start_position + total_customer_subset_1

    user_ids[start_position:end_position] = customer_subset_1["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(2, 5)) for last_login in login_time_for_review_plan_options]
    event_type_ids[start_position:end_position] = event_type_map.get("review_plan_options")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_1["user_id"]])
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, last_event_id + 1 + total_customer_subset_1 )
    last_event_id = event_ids[start_position:end_position].max()


    total_customer_subset_2 = len(customer_subset_2) 

    first_investment_type = [np.random.choice(
        FIRST_INVESTMENT_TYPE,
        p= CUSTOMER_BEHAVIOUR_SEGMENT_MAP[cp][
            'first_investment_type_probability'
        ]
    )
    for cp in customer_subset_2['customer_behaviour_segment']]

    uids = customer_subset_2['user_id']

    customer_subset_2['first_investment_type'] = first_investment_type

    balances = get_current_wallet_balance(conn,uids)

    customer_subset_2 = customer_subset_2.merge(balances, on='user_id', how='left')

    customer_subset_2 = customer_subset_2.copy().reset_index(drop=True)

    random_offset = np.random.randint(0,1200,size=total_customer_subset_2)

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [GENERATION_START_DATE + pd.to_timedelta(ro,unit="m") for ro in random_offset]
    event_type_ids[start_position:end_position] = event_type_map.get("app_login")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, last_event_id + 1 + total_customer_subset_2 )
    last_event_id = event_ids[start_position:end_position].max()

    login_time_for_review_plan_options_2 = event_time[start_position:end_position]

    update_last_login_timestamp(conn, customer_subset_2["user_id"],  login_time_for_review_plan_options_2)

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(2, 5)) for last_login in login_time_for_review_plan_options_2]
    event_type_ids[start_position:end_position] = event_type_map.get("review_plan_options")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, last_event_id + 1 + total_customer_subset_2 )
    last_event_id = event_ids[start_position:end_position].max()

    last_review_time_for_investment = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_review + timedelta(minutes=np.random.randint(1, 3)) for last_review in last_review_time_for_investment]
    event_type_ids[start_position:end_position] = event_type_map.get("plan_selected")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, last_event_id + 1 + total_customer_subset_2 )
    last_event_id = event_ids[start_position:end_position].max()


    last_plan_selected_time = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_review + timedelta(minutes=np.random.randint(3,6)) for last_review in last_plan_selected_time]
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])

    investment_type_event_type = [
    "savings_plan_created"
    if inv == "Savings"
    else "investment_plan_created"
    for inv in customer_subset_2["first_investment_type"]
    ]

    print("Absent invesment type selections",pd.isna(investment_type_event_type).sum())
    
    event_type_ids[start_position:end_position] = [event_type_map.get(inv) for inv in investment_type_event_type]
    is_money_movement_activities[start_position:end_position] = True
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, last_transaction_id +  len(customer_subset_2) + 1)
    transaction_type_ids[start_position:end_position] = [transaction_type_map.get("investment_funding") for _ in range(len(customer_subset_2))]
    investment_ids[start_position:end_position] = np.arange(last_investment_id+1, last_investment_id+ 1 + len(customer_subset_2))
    last_investment_id = investment_ids[start_position:end_position].max()

    customer_subset_2['select_plan_ids'] = np.empty(len(customer_subset_2),dtype=object)

    savings_plans = conn.execute('''SELECT * FROM dim_plan WHERE plan_category = 'Savings' ''').df()
    print("Savings Plans: ",savings_plans["plan_id"])
    investment_plans = conn.execute('''SELECT * FROM dim_plan WHERE plan_category = 'Investments' ''').df()
    print("Investement Plans: ",investment_plans["plan_id"])

    savings_mask = customer_subset_2["first_investment_type"] == 'Savings'
    investments_mask = customer_subset_2["first_investment_type"] == 'Investments'
    print("First Investment Type Unique Values", customer_subset_2["first_investment_type"].unique())

    customer_subset_2.loc[savings_mask,'select_plan_ids'] = [np.random.choice(savings_plans["plan_id"], 
                                            p = savings_plans["plan_weight"] / savings_plans["plan_weight"].sum())
                                     for _ in range(savings_mask.sum())]
    customer_subset_2.loc[investments_mask,'select_plan_ids'] = [np.random.choice(investment_plans["plan_id"], 
                                        p = investment_plans["plan_weight"] / investment_plans["plan_weight"].sum())
                                         for _ in range(investments_mask.sum())]

    plan_ids[start_position:end_position] = customer_subset_2['select_plan_ids']
    print(customer_subset_2['select_plan_ids'])
    wallet_ids[start_position:end_position] = [wallet_id_map.get(uid) for uid in customer_subset_2["user_id"]]
    investment_pct = np.random.uniform(
    0.5,
    0.95,
    len(customer_subset_2)
)
    amount_invested[start_position:end_position] = (customer_subset_2["current_balance"] * investment_pct)

    transaction_statuses[start_position:end_position] = ["success" for _ in range(len(customer_subset_2))]
    transaction_amounts[start_position:end_position] = (customer_subset_2["current_balance"].values * investment_pct)
    event_ids[start_position:end_position] = np.arange(last_event_id + 1, last_event_id + total_customer_subset_2 + 1)

    last_transaction_id = transaction_ids[start_position:end_position].max()

    debit_wallet_balance(conn,customer_subset_2['user_id'], transaction_amounts[start_position:end_position], event_time[start_position:end_position],
                         transaction_ids[start_position:end_position], event_ids[start_position:end_position])





    total_events = end_position
    

    #invesment df
    main_df = pd.DataFrame({
        "user_id":user_ids[:total_events],
        "event_type_id":event_type_ids[:total_events],
        "wallet_id":wallet_ids[:total_events],
        "plan_id":plan_ids[:total_events],
        "event_time":event_time[:total_events],
        "device_type":device_types[:total_events],
        "is_money_movement_activity":is_money_movement_activities[:total_events],
        "transaction_type_id":transaction_type_ids[:total_events],
        "transaction_id":transaction_ids[:total_events],
        "investment_id":investment_ids[:total_events],
        "transaction_status":transaction_statuses[:total_events],
        "transaction_amount":transaction_amounts[:total_events],
        "is_withdrawn_early":is_withdrawn_early[:total_events],
        "early_withdrawal_date":withdrawal_date[:total_events]
    })

    main_df["event_date_id"] = np.array([
    int(pd.Timestamp(ts).strftime('%Y%m%d'))
    for ts in main_df["event_time"]
    ], dtype=np.int32)

    print("Missing event_time:", np.sum(pd.isna(event_time[:total_events])))

    missing_idx = np.where(pd.isna(event_time[:total_events]))[0]
    print(missing_idx[:20])

    bad_rows = main_df[
    main_df["event_time"].map(lambda x: not isinstance(x, pd.Timestamp))
]

    print(bad_rows[[
    "event_time",
    "event_type_id",
    "user_id",
    "investment_id",
    "transaction_id"
]])

    print(main_df["event_time"].map(type).value_counts())

    print(
    main_df.loc[
        main_df["event_time"].map(lambda x: not isinstance(x, pd.Timestamp)),
        ["event_type_id", "event_time", "transaction_id", "investment_id"]
    ]
)
    main_df = main_df.sort_values(by='event_time').reset_index(drop=True)

    money_mov_mask = main_df["transaction_id"].notna()

    main_df.loc[money_mov_mask,"transaction_id"] = np.arange(968, money_mov_mask.sum() + 968)
    
    transactions_df = main_df[main_df["transaction_id"].notna()].copy()

    transaction_events_df = pd.DataFrame({
        "transaction_id":transactions_df["transaction_id"],
        "wallet_id":transactions_df["wallet_id"],
        "transaction_type_id":transactions_df["transaction_type_id"],
        "transaction_amount":transactions_df["transaction_amount"],
        "transaction_status": transactions_df["transaction_status"],
        "transaction_timestamp":transactions_df["event_time"],
        "transaction_date_id":transactions_df["event_date_id"]
    })

    conn.register("tr_events",transaction_events_df)

    conn.execute('''INSERT INTO fact_transaction SELECT * FROM tr_events''')

    conn.execute(f'''
                    COPY fact_transaction TO '{CURRENT_FACT_TRANSACTION_PARQUET_PATH}' (FORMAT PARQUET)
    ''')

    conn.execute('''INSERT INTO FACT_INVESTMENT_POSITION SELECT * FROM INVESTMENT_DF''')

    conn.execute(f'''COPY FACT_INVESTMENT_POSITION TO '{CURRENT_FACT_INVESTMENT_POSITION_PARQUET_PATH}' (FORMAT PARQUET) ''')

    df_raw = pd.DataFrame({
        "user_id":user_ids[:total_events],
        "event_type_id":event_type_ids[:total_events],
        "wallet_id":wallet_ids[:total_events],
        "plan_id":plan_ids[:total_events],
        "event_time":event_time[:total_events],
        "event_date_id":np.array([
    int(pd.Timestamp(ts).strftime('%Y%m%d'))
    for ts in event_time[:total_events]
    ], dtype=np.int32),
        "device_type":device_types[:total_events],
        "is_money_movement_activity":is_money_movement_activities[:total_events],
        "transaction_type_id":transaction_type_ids[:total_events],
        "transaction_id":transaction_ids[:total_events],
        "investment_id":investment_ids[:total_events]
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
        "wallet_id",
        "plan_id",
        "event_time",
        "event_date_id",
        "device_type",
        "is_money_movement_activity",
        "transaction_type_id",
        "transaction_id",
        "investment_id"
    ]]

    conn.register("df_raw",df_raw)

    conn.execute('''INSERT INTO fact_user_event SELECT * FROM df_raw''')

    conn.execute(f'''COPY FACT_USER_EVENT TO '{CURRENT_FACT_USER_EVENT_PARQUET_PATH}' (FORMAT PARQUET) ''')