import numpy as np
import pandas as pd
from incremental_generator.config.paths import (CURRENT_FACT_USER_EVENT_PARQUET_PATH, CURRENT_FACT_INVESTMENT_POSITION_PARQUET_PATH, CURRENT_FACT_TRANSACTION_PARQUET_PATH)
from incremental_generator.config.constants import (IMMEDIATE_LOGINS_TIME_FRAME, CUSTOMER_BEHAVIOUR_SEGMENT_MAP, FIRST_INVESTMENT_TYPE, GENERATION_START_TIMESTAMP, 
                                                    GENERATION_END_TIMESTAMP, GENERATION_START_DATE)
                                  
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from incremental_generator.generators.facts.helper_functions import (incremental_vested_investment_events,incremental_vested_investments_proceeds_transfer_events,
                                                                     upload_newly_created_investments_to_db,incremental_early_withdrawal_investments_proceeds_transfer,
                                                                     request_early_withdrawal_events,incremental_assets_sale_investment_proceeds_wallet_transfer_events,
                                                                     update_asset_sale_events)
from incremental_generator.logic.EventContext import load_event_context
from src.logic.helper_functions import (signup_completion_events, app_login_events, kyc_completion_events, wallet_activation_events, vested_investments_events, 
                                        vested_investments_proceeds_transfer_events,review_plan_options_events,new_investment_creation,review_current_investment_events,
                                        assets_sale_events)


def generate_facts(conn, num_of_events):

    context = load_event_context(conn)

    #populate all possible signups within the project duration
    new_signups_data = conn.execute(f'''SELECT * FROM dim_user
     where signup_date BETWEEN '{GENERATION_START_TIMESTAMP}' AND '{GENERATION_END_TIMESTAMP}' order by signup_date''').df()
    
    all_users_data = conn.execute('''SELECT * FROM dim_user order by signup_date''').df()
    all_wallets_data = conn.execute('''SELECT * from dim_wallet order by wallet_created_at''').df()

    last_investment_id = conn.execute('''SELECT coalesce(max(investment_id),0) as investment_id from fact_investment_position''').fetchone()[0]

    device_type_map = dict(zip(all_users_data["user_id"],all_users_data["device_type"]))
    
    wallet_id_map = dict(zip(all_wallets_data["user_id"],all_wallets_data["wallet_id"]))

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

    last_transaction_id = conn.execute('''SELECT coalesce(max(transaction_id),0) from fact_transaction''').fetchone()[0]
    # new user signups
    total_signups = len(new_signups_data)

    dtypes = [device_type_map.get(uid for uid in new_signups_data['user_id'])]

    start_position = 0
    end_position = total_signups

    signup_completion_events(context, 0,total_signups, user_ids, new_signups_data['user_id'], event_time,new_signups_data['signup_date'],device_types,dtypes, event_type_ids)

    #new user logins

    new_users_logins = new_signups_data[new_signups_data['is_immediate_login'] == True]

    total_new_users_logins = len(new_users_logins)

    
    start_position = end_position
    end_position = start_position + total_new_users_logins
    
    #post signup immediate logins - login timeframe is between 1 and 5 minutes
    immediate_login_timeframe = np.random.randint(IMMEDIATE_LOGINS_TIME_FRAME[0],IMMEDIATE_LOGINS_TIME_FRAME[1], size=total_new_users_logins)

    etime = pd.to_datetime(new_users_logins['signup_date']) + pd.to_timedelta(immediate_login_timeframe,unit='s')
    dtypes = [device_type_map.get(uid for uid in new_users_logins['user_id'])]
    
    app_login_events(conn,context, start_position, end_position, user_ids, new_users_logins['user_id'], event_time, etime, device_types,dtypes, event_type_ids)



    #kyc_completed_users

    all_users_data['kyc_completion_date'] = pd.to_datetime(all_users_data['kyc_completion_date'],errors='coerce')

    
    sure_kyc_completed_users = all_users_data[all_users_data['kyc_completion_date'].dt.date == GENERATION_START_DATE].copy()
    
    kyc_activation_time =  sure_kyc_completed_users["kyc_completion_date"]#assuming wallet activation happens after KYC completion, we can set the KYC activation timeframe to be slightly less than the wallet activation timeframe for those users

    ro = np.random.randint(5,16,size=len(sure_kyc_completed_users))

    kyc_logins_time = kyc_activation_time - pd.to_timedelta(ro,unit="m") #assuming KYC completion happens after the last login, we can set the KYC activation timeframe to be slightly more than the last login timeframe

    
    start_position = end_position
    end_position = start_position + len(sure_kyc_completed_users)

    
    uids = sure_kyc_completed_users['user_id']
    dtypes = [device_type_map.get(uid for uid in sure_kyc_completed_users['user_id'])]

    app_login_events(conn, context, start_position, end_position, user_ids, uids, event_time, kyc_logins_time, device_types, dtypes, event_type_ids)

    start_position = end_position
    end_position = start_position + len(sure_kyc_completed_users)

    kyc_completion_events(conn, context, start_position, end_position, user_ids,uids, event_time, kyc_activation_time, device_types, dtypes, event_type_ids )


    #wallet activation

    all_users_data['supposed_activation_date'] = pd.to_datetime(all_users_data['supposed_activation_date'])
    wallet_activation_df = all_users_data[all_users_data['supposed_activation_date'].dt.date == GENERATION_START_DATE].copy()
    
    start_position = end_position
    end_position = start_position + len(wallet_activation_df)

    uids = wallet_activation_df['user_id']
    dtypes = [device_type_map.get(uid for uid in uids)]
    
    

    wallet_activation_dict = wallet_activation_events(conn,context,start_position,end_position,user_ids,uids, event_time, wallet_activation_df['supposed_activation_date'],device_types, dtypes,
                                                      event_type_ids, wallet_ids, uids, is_money_movement_activities, transaction_type_ids, transaction_ids, transaction_amounts,
                                                      transaction_statuses, last_transaction_id)


    last_transaction_id = wallet_activation_dict['last_transaction_id']
    end_position = wallet_activation_dict['updated_end_position']

    #let's model investment vesting events

    #first we will start with already vested investments yet to be transferred to the user's wallet

    matured_investments_df = conn.execute(''' SELECT * FROM FACT_INVESTMENT_POSITION WHERE investment_status = 'Matured' ''')

    start_position = end_position
    end_position = start_position + len(matured_investments_df)

    dtypes = [device_type_map.get(uid for uid in matured_investments_df['user_id'])]

    last_transaction_id = incremental_vested_investments_proceeds_transfer_events(conn, context, start_position, end_position, user_ids, event_time, wallet_ids,
                                                                                  last_transaction_id, is_money_movement_activities, transaction_type_ids, transaction_ids,
                                                                                  transaction_amounts, transaction_statuses, event_type_ids, device_types,dtypes,
                                                                                  investment_ids,matured_investments_df)



    #then we will have make today's matured investments vest
    vestable_investments = conn.execute(f'''SELECT * from fact_investment_position where investment_maturity_date::DATE = '{GENERATION_START_DATE}' ''').df()

    start_position = end_position
    end_position = start_position + len(vestable_investments)

    dtypes = [device_type_map.get(uid for uid in vestable_investments['user_id'])]
    inv_ids = vestable_investments['investment_id']

    incremental_vested_investment_events(conn,context,start_position,end_position,user_ids,event_time, event_type_ids, investment_ids,device_types, dtypes,vestable_investments)

    
    #people that create investments
    all_users = conn.execute(f'''SELECT w.user_id as user_id, u.customer_behaviour_segment, i.user_id as unused, w.wallet_activated_at FROM dim_wallet w join dim_user u on 
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

    uids = customer_subset_1['user_id']
    etime = customer_subset_1['wallet_activated_at'] + pd.to_timedelta(ro for ro in random_offset)
    dtypes = device_type_map.get(uid for uid in uids)

    app_login_events(conn,context,start_position, end_position,user_ids,uids,event_time,etime,device_types,dtypes,event_type_ids )

    start_position = end_position
    end_position = start_position + total_customer_subset_1

    uids = customer_subset_1['user_id']
    dtypes = [device_type_map.get(uid for uid in uids)]

    review_plan_options_events(conn,context,start_position,end_position,user_ids,uids, event_time, event_type_ids,device_types,dtypes)


    #these users will invest
    total_customer_subset_2 = len(customer_subset_2) 

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    customer_subset_2 = customer_subset_2.copy().reset_index(drop=True)


    start_position = end_position
    end_position = start_position + total_customer_subset_2

    uids = customer_subset_2['user_id']
    random_offset = np.random.randint(0,1200,size=total_customer_subset_2)
    etime = pd.to_datetime(GENERATION_START_TIMESTAMP) + pd.to_timedelta(ro for ro in random_offset)
    dtypes = [device_type_map.get(uid for uid in uids)]

    inv_type = np.array([
    np.random.choice(FIRST_INVESTMENT_TYPE,p=CUSTOMER_BEHAVIOUR_SEGMENT_MAP[cbs]['first_investment_type_probability'])
    for cbs in customer_subset_2['customer_behaviour_segment']])

    return_dict = new_investment_creation(conn,context, start_position, end_position, user_ids, uids, wallet_ids, event_time,etime,inv_type,device_types,dtypes,is_money_movement_activities,
                                          transaction_ids, last_transaction_id,transaction_type_ids, event_type_ids, transaction_amounts, transaction_statuses,investment_ids,last_investment_id)


    last_transaction_id = return_dict['last_transaction_id']
    new_investments_df = return_dict['all_investments_df']
    end_position = return_dict['updated_end_position']
    last_investment_id = return_dict['last_investment_id']

    upload_newly_created_investments_to_db(conn,new_investments_df)

    

    #engagement from users who have existing investments
    users_with_existing_investments = conn.execute('''
        SELECT d.user_id, d.customer_behaviour_segment from fact_investment_position f inner join dim_user d on f.user_id = d.user_id where investment_status = 'Active'
    ''').df()

    high_engagement_mask = (users_with_existing_investments["customer_behaviour_segment"] == 'High_Engagement_High_Balance') | (users_with_existing_investments["customer_behaviour_segment"] == 'High_Engagement_Low_Balance')
    moderate_engagement_mask = (users_with_existing_investments["customer_behaviour_segment"] == 'Moderate_Engagement_High_Balance') | (users_with_existing_investments["customer_behaviour_segment"] == 'Moderate_Engagement_Low_Balance')
    low_engagement_mask = (users_with_existing_investments["customer_behaviour_segment"] == 'Low_Engagement_High_Balance') | (users_with_existing_investments["customer_behaviour_segment"] == 'Low_Engagement_Low_Balance')

    high_engagement_subset = users_with_existing_investments[high_engagement_mask].sample(frac=0.6,random_state=1)
    moderate_engagement_subset = users_with_existing_investments[moderate_engagement_mask].sample(frac=0.3,random_state=1)
    low_engagement_subset = users_with_existing_investments[low_engagement_mask].sample(frac=0.1,random_state=1)

    customer_subset_3 = pd.concat([high_engagement_subset, moderate_engagement_subset, low_engagement_subset],ignore_index=True)

    total_customer_subset_3 = len(customer_subset_3)

    random_offset = np.random.randint(0,1200,size=total_customer_subset_3)

    start_position = end_position
    end_position = start_position + total_customer_subset_3

    uids = customer_subset_3['user_id']
    etime = pd.to_datetime(GENERATION_START_DATE) + pd.to_timedelta(random_offset,unit="m")

    updated_end_position = review_current_investment_events(conn,context,start_position, end_position,user_ids,uids,event_time)

    end_position = updated_end_position
    #let's simulate previous early withdrawals proceeds transfer
    pending_early_withdrawals_df = conn.execute(f'''
                SELECT * FACT_INVESTMENT_POSITION WHERE investment_status = 'withdrawn_early'
    ''').df()

    start_position = end_position
    end_position = start_position + len(pending_early_withdrawals_df)

    dtypes = [device_type_map.get(uid for uid in uids)]

    return_dict = incremental_early_withdrawal_investments_proceeds_transfer(conn, context, start_position, end_position, user_ids, wallet_ids, is_money_movement_activities, last_transaction_id, event_time, device_types, dtypes,
                                                                             pending_early_withdrawals_df, event_type_ids, transaction_type_ids, transaction_ids, transaction_amounts, transaction_statuses, investment_ids)


    last_transaction_id = return_dict['last_transaction_id']
    end_position = return_dict['updated_end_position']

    #let's simulate early withdrawals
    possible_early_maturity_users = conn.execute(f'''
            with get_users as (
                 SELECT *, investment_maturity_date - '{GENERATION_START_DATE}'::DATE as days_held, 
                 row_number() over(
                    partition by user_id
                    order by investment_maturity_date asc
                 ) as rn
                 from fact_investment_position where investment_status = 'Active' and is_withdrawn_early = False and investment_maturity_date is not null
                 ) select * from get_users where rn = 1 and days_held between 0 and 30 
                 order by random()
                 limit 10
    ''').df()

    customer_subset_4 = possible_early_maturity_users

    total_customer_subset_4 = len(customer_subset_4)

    start_position = end_position
    end_position = start_position + total_customer_subset_4

    random_offset = np.random.randint(10,1000,size = total_customer_subset_4)
    customer_subset_4['withdrawal_request_date'] = GENERATION_START_DATE + pd.to_timedelta(random_offset,unit='m')

    start_position = end_position
    end_position = start_position + total_customer_subset_4

    uids = customer_subset_4['user_id']
    dtypes = device_type_map.get(uid for uid in uids)


    #we are logging in first, then reviewing current investments, then making an early withdrawal request
    updated_end_position = request_early_withdrawal_events(conn, context, start_position, end_position, user_ids, event_time, event_type_ids, investment_ids, device_types, dtypes, customer_subset_4)

    end_position = updated_end_position

    pending_sales_df = conn.execute(''' SELECT * FROM FACT_INVESTMENT_POSITION WHERE investment_status = 'sale_processing' ''').df()

    start_position = end_position
    end_position = start_position + len(pending_sales_df)

    dtypes = [device_type_map.get(uid for uid in pending_sales_df['user_id'])]

    last_transaction_id = incremental_assets_sale_investment_proceeds_wallet_transfer_events(conn, context, start_position, end_position, user_ids, wallet_ids,event_time, device_types,
                                                                                             dtypes, transaction_type_ids, transaction_ids, last_transaction_id, event_type_ids,
                                                                                             is_money_movement_activities, transaction_amounts, transaction_statuses,investment_ids,
                                                                                             pending_sales_df)
    


    possible_asset_sale_users = conn.execute(f'''
            with get_users as (
                 SELECT *, '{GENERATION_START_DATE}'::DATE - investment_start_date as days_since_registration, row_number() over(
                    partition by user_id
                    order by investment_start_date asc
                 ) as rn
                 from fact_investment_position where investment_status = 'active' and investment_maturity_date is null
                 ) select * from get_users where rn = 1 and days_since_registration > 90 
                 order by random()
                 limit 5
    ''').df()

    customer_subset_5 = possible_asset_sale_users.copy()

    total_customer_subset_5 = len(customer_subset_5)

    start_position = updated_end_position
    end_position = start_position + total_customer_subset_5

    random_offset = np.random.randint(10,1000,size = total_customer_subset_5)


    uids = customer_subset_5['user_id']
    dtypes = device_type_map.get(uid for uid in uids)
    customer_subset_5['redemption_request_date'] = pd.to_datetime(GENERATION_START_DATE) + pd.to_timedelta(random_offset,unit='m')

    assets_sale_events(context, start_position, end_position,user_ids, event_time, event_type_ids, device_types,dtypes,investment_ids,customer_subset_5)
    update_asset_sale_events(conn,customer_subset_5['redemption_request_date'],customer_subset_5)


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