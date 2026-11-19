import numpy as np
import pandas as pd
from src.config.paths import (DDL_FACT_USER_EVENT_PATH, FACT_USER_EVENT_PARQUET_PATH, 
                              FACT_INVESTMENT_POSITION_PARQUET_PATH, DDL_FACT_INVESTMENT_POSITION_PATH, DDL_FACT_TRANSACTION_PATH, FACT_TRANSACTION_PARQUET_PATH,
                              FACT_WALLET_BALANCE_PARQUET_PATH, USERS_PARQUET_PATH, WALLETS_PARQUET_PATH)
from src.config.constants import (DEFAULT_TRANSACTION_START_DATE, DEFAULT_TRANSACTION_END_DATE, IMMEDIATE_LOGINS_TIME_FRAME, KYC_ACTIVATION_TIMEFRAME,
                                  CUSTOMER_BEHAVIOUR_SEGMENT_MAP, MUTUAL_FUNDS_CUTOFF_DATE
                                  )
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from src.logic.helper_functions import (signup_completion_events, app_login_events, get_last_login, kyc_completion_events,
                                        wallet_activation_events, review_plan_options_events, plan_selection_events, plan_ids_allocation, build_investment_creation_users_dataframe,
                                        investment_creation_events, get_customer_behaviour_segment, create_engagement_events, review_current_investment_events, create_wallet_funding_events,
                                        new_investment_creation, early_withdrawal_requests_events, vested_investments_events, vested_investments_proceeds_transfer_events,
                                         assets_sale_events, assets_sale_investment_proceeds_wallet_transfer_events )
from src.logic.EventContext import (load_event_context)


def generate_facts(conn, num_of_events):

    context = load_event_context(conn)

    create_fact_user_table = DDL_FACT_USER_EVENT_PATH.read_text()
    create_fact_investment_table = DDL_FACT_INVESTMENT_POSITION_PATH.read_text()
    create_fact_transaction_table = DDL_FACT_TRANSACTION_PATH.read_text()

    conn.execute(create_fact_user_table)
    conn.execute(create_fact_investment_table)
    conn.execute(create_fact_transaction_table)

    #populate all possible signups within the project duration
    users_data = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, wallet_activation_timeframe, customer_behaviour_segment, device_type, supposed_activation_date,
    is_immediate_login
    FROM dim_user where signup_date between '{DEFAULT_TRANSACTION_START_DATE}' and '{DEFAULT_TRANSACTION_END_DATE}' order by signup_date''').df()

    all_users_data = conn.execute('''SELECT user_id, device_type from dim_user''').df()
    
    user_wallet_data = conn.execute(f'''SELECT user_id, wallet_id, wallet_created_at, wallet_activated_at from dim_wallet''').df()

    device_type_map = dict(zip(all_users_data["user_id"],all_users_data["device_type"]))

    wallet_id_map = dict(zip(user_wallet_data["user_id"],user_wallet_data["wallet_id"]))

    event_time = np.empty(num_of_events, dtype=object)

    user_ids = np.empty(num_of_events, dtype=object)

    event_type_ids = np.empty(num_of_events, dtype=object)

    wallet_ids = np.empty(num_of_events, dtype=object)

    device_types = np.empty(num_of_events, dtype=object)

    is_money_movement_activities = np.empty(num_of_events, dtype=bool)

    transaction_type_ids = np.empty(num_of_events, dtype=object)

    transaction_ids = np.empty(num_of_events, dtype=object)

    investment_ids = np.empty(num_of_events, dtype=object)

    last_transaction_id = 0
    last_investment_id = 0

    #event_ids = np.empty(num_of_events, dtype=np.int64)

    transaction_amounts = np.zeros(num_of_events, dtype=np.float64)
    transaction_statuses = np.empty(num_of_events, dtype = object)

    # new user signups
    total_signups = len(users_data)

    start_position = 0
    end_position = total_signups

    dtypes = np.array([device_type_map.get(uid) for uid in users_data["user_id"]])

    print("Null device types for the users line 76:",pd.isna(dtypes).sum())

    signup_completion_events(context, start_position, end_position, user_ids, users_data["user_id"], event_time, users_data["signup_date"],device_types, dtypes,event_type_ids)

    #new user logins
    new_users_logins = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, customer_behaviour_segment FROM dim_user
    where signup_date between '{DEFAULT_TRANSACTION_START_DATE}' and '{DEFAULT_TRANSACTION_END_DATE}' AND is_immediate_login = True order by signup_date''').df()
    
    immediate_login_timeframe = np.random.randint(IMMEDIATE_LOGINS_TIME_FRAME[0],IMMEDIATE_LOGINS_TIME_FRAME[1], size=len(new_users_logins))
    
    total_new_users = len(new_users_logins)

    start_position = total_signups
    end_position = start_position + total_new_users

    etime = pd.to_datetime(new_users_logins["signup_date"]) + pd.to_timedelta(immediate_login_timeframe, unit = 's')
    uids = new_users_logins["user_id"]
    dtypes=[device_type_map.get(uid) for uid in uids]

    print("Missing device types for the users line 95:",pd.isna(dtypes).sum())

    app_login_events(conn,context,start_position, end_position, user_ids, uids, event_time, etime, device_types, dtypes, event_type_ids)

    print("Missing event time values line 95:", pd.isna(event_time[start_position:end_position]).sum())
    
    #kyc_completed_users
    kyc_completed_users = conn.execute(f'''
            SELECT * FROM dim_user where kyc_completed = True AND kyc_completion_date between '{DEFAULT_TRANSACTION_START_DATE}' and '{DEFAULT_TRANSACTION_END_DATE}' order by signup_date
''').df()

    
    # start activation by logging in
    start_position = end_position
    end_position = start_position + len(kyc_completed_users)

    random_offset = np.random.randint(10,30, size=len(kyc_completed_users))

    dtypes = [device_type_map.get(uid) for uid in kyc_completed_users["user_id"]]
    etime = kyc_completed_users["kyc_completion_date"] - pd.to_timedelta(random_offset, unit='m')

    print("Missing device types for the users line 116:",pd.isna(dtypes).sum())

    app_login_events(conn, context, start_position, end_position, user_ids,kyc_completed_users["user_id"],event_time,etime,device_types,dtypes,event_type_ids)

    print("Missing event time values line 114:", pd.isna(event_time[start_position:end_position]).sum())


    #activate kyc
    start_position = end_position
    end_position = start_position + len(kyc_completed_users)
    
    etime = pd.to_datetime(kyc_completed_users["kyc_completion_date"])
    dtypes = [device_type_map.get(uid) for uid in kyc_completed_users["user_id"]]

    print("Missing device types for the users line 130:",pd.isna(dtypes).sum())

    kyc_completion_events(conn, context, start_position, end_position, user_ids, kyc_completed_users["user_id"], 
                          event_time, etime, device_types, dtypes, event_type_ids)

    print("Missing event time values line 127:", pd.isna(event_time[start_position:end_position]).sum())


    #wallet activation
    wallet_activated_users = conn.execute(f'''
            SELECT * FROM dim_user where supposed_activation_date::DATE between '{DEFAULT_TRANSACTION_START_DATE}' and '{DEFAULT_TRANSACTION_END_DATE}' AND is_activated_user = True order by signup_date
    ''').df()

    total_wallet_activated_users = len(wallet_activated_users)

    start_position = end_position
    end_position = start_position + total_wallet_activated_users

    uids = wallet_activated_users["user_id"]
    etime = wallet_activated_users["supposed_activation_date"]
    dtypes = [device_type_map.get(uid) for uid in wallet_activated_users["user_id"]]
    wids = [wallet_id_map.get(uid) for uid in wallet_activated_users["user_id"]]

    print("Missing device types values line 153",pd.isna(dtypes).sum())
    
    return_dict = wallet_activation_events(
        conn, context, start_position, end_position,user_ids, uids, event_time, etime,
    device_types, dtypes, event_type_ids, wallet_ids, wids, is_money_movement_activities, transaction_type_ids, transaction_ids, transaction_amounts,
    transaction_statuses, last_transaction_id
    )

    last_transaction_id = return_dict['last_transaction_id']
    end_position = return_dict['updated_end_position']

    print("Missing event time values line 154:", pd.isna(event_time[start_position:end_position]).sum())
    

    #let's create the initial investment -- login, review_plan_options then drop off for some users, and for others, they will make an investment after reviewing the plan options. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.

    #these users will just login and review plan options, but will not make an investment. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.

    wallet_activated_users = conn.execute(f'''
            SELECT * FROM dim_user where supposed_activation_date::DATE between '{DEFAULT_TRANSACTION_START_DATE}' and '{DEFAULT_TRANSACTION_END_DATE}' AND is_activated_user = True order by signup_date
    ''').df()

    customer_subset_1 = wallet_activated_users.sample(frac = 0.55, random_state=1)
    

    #print("last login df",last_login_df.head(10))
    #print("customer subset 1 columns ", customer_subset_1.columns)

    #print("customer subset 1 ", customer_subset_1.head(10))

    #print("The customer subset 1 user_id and last_login_at ",customer_subset_1[['user_id','supposed_activation_date','last_login_at']])

    #print("customer subset 1 columns ", customer_subset_1.columns)

    total_customer_subset_1 = len(customer_subset_1)

    start_position = end_position
    end_position = start_position + total_customer_subset_1

    uids = customer_subset_1["user_id"]

    random_offset = np.random.randint(1800, 5000,size=len(customer_subset_1))

    etime = pd.to_datetime(customer_subset_1['last_login_at']) + pd.to_timedelta(random_offset, unit='m')
    dtypes = [device_type_map.get(uid) for uid in customer_subset_1["user_id"]]
    app_login_events(conn, context, start_position, end_position, user_ids, uids, event_time,etime, device_types, dtypes, event_type_ids)

    print("Null device types for the users line 200:",pd.isna(dtypes).sum())

    print("Missing event time values line 179:", pd.isna(event_time[start_position:end_position]).sum())


    start_position = end_position
    end_position = start_position + total_customer_subset_1

    uids = customer_subset_1["user_id"]
    dtypes = [device_type_map.get(uid) for uid in customer_subset_1["user_id"]]

    print("Null device types for the users line 209:",pd.isna(dtypes).sum())

    random_offset = np.random.randint(2, 6, size=total_customer_subset_1)

    review_time = pd.to_datetime(etime) + pd.to_timedelta(random_offset,unit='m')

    review_plan_options_events(context,start_position, end_position, user_ids, uids, event_time,review_time, event_type_ids, device_types, dtypes)

    print("Missing event time values line 194:", pd.isna(event_time[start_position:end_position]).sum())

    # These are the users who will make an investment

    wallet_activated_users_df = build_investment_creation_users_dataframe(conn, wallet_activated_users)
    
    customer_subset_2 = wallet_activated_users_df[wallet_activated_users_df['makes_first_investment'] == True]

    customer_subset_2 = customer_subset_2.copy().reset_index(drop=True)

    total_customer_subset_2 = len(customer_subset_2)

    #The user creates first investment here

    #logs in first

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    uids = customer_subset_2["user_id"]
    etime = pd.to_datetime(customer_subset_2["wallet_activated_at"]) + pd.to_timedelta(customer_subset_2["mins_to_first_investment"], unit='m')

    print("Missing last login values:", pd.isna(customer_subset_2["wallet_activated_at"]).sum())

    dtypes = [device_type_map.get(uid) for uid in customer_subset_2["user_id"]]

    print("Null device types for the users line 243:",pd.isna(dtypes).sum())

    app_login_events(conn, context, start_position, end_position, user_ids, uids, event_time, etime, device_types, dtypes, event_type_ids)

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    uids = customer_subset_2["user_id"]
    dtypes = [device_type_map.get(uid) for uid in customer_subset_2["user_id"]]

    print("Null device types for the users line 253:",pd.isna(dtypes).sum())

    random_offset = np.random.randint(1,4,size=total_customer_subset_2)

    review_time = pd.to_datetime(etime) + pd.to_timedelta(random_offset, unit='m')

    print("Missing review time values line 230:", pd.isna(review_time).sum())

    review_plan_options_events(context, start_position, end_position, user_ids, uids, event_time,review_time, event_type_ids, device_types, dtypes)

    plan_review_time = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    uids = customer_subset_2["user_id"]
    dtypes = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])

    print("Null device types for the users line 271:",pd.isna(dtypes).sum())

    investment_type_df = pd.DataFrame({
        'user_id':customer_subset_2["user_id"],
        'first_investment_type':customer_subset_2["first_investment_type"]
    })
    

    plan_selected_df = plan_selection_events(context, start_position, end_position, user_ids, uids, event_time, plan_review_time, event_type_ids, device_types, dtypes)

    plan_selected_df['first_investment_type'] = investment_type_df['first_investment_type']

    # investment creation events

    total_plan_selection_events = len(plan_selected_df)

    start_position = end_position
    end_position = start_position + total_plan_selection_events

    uids = plan_selected_df["user_id"]
    first_inv_type = plan_selected_df["first_investment_type"]
    plan_selection_time = plan_selected_df["plan_selection_time"]

    print("Missing plan selection time values line 263:", pd.isna(plan_selection_time).sum())
    dtypes = [device_type_map.get(uid) for uid in uids]

    print("Null device types for the users line 297:",pd.isna(dtypes).sum())

    investment_creation_dict = investment_creation_events(conn, context, start_position, end_position, user_ids, uids,wallet_ids, event_time, plan_selection_time, first_inv_type,
                                                          device_types, dtypes, is_money_movement_activities, transaction_ids, last_transaction_id, transaction_type_ids,
                                                          event_type_ids, transaction_amounts, transaction_statuses, investment_ids, last_investment_id)

    print("Missing event time values line 270:", pd.isna(event_time[start_position:end_position]).sum())

    last_transaction_id = investment_creation_dict["last_transaction_id"]
    all_investments_df = investment_creation_dict["all_investments_df"]
    last_investment_id = investment_creation_dict["last_investment_id"]

    
    customers_who_have_invested_df = get_last_login(conn, all_investments_df["user_id"])
    cbs_map = get_customer_behaviour_segment(conn, all_investments_df["user_id"])

    customers_who_have_invested_df['customer_behaviour_segment'] = customers_who_have_invested_df['user_id'].map(cbs_map)


    active_users_subset = customers_who_have_invested_df[
    (customers_who_have_invested_df["customer_behaviour_segment"] == "High_Engagement_High_Balance")
    |
    (customers_who_have_invested_df["customer_behaviour_segment"] == "High_Engagement_Low_Balance")
    |
    (customers_who_have_invested_df["customer_behaviour_segment"] == "Moderate_Engagement_High_Balance")
    |
    (customers_who_have_invested_df["customer_behaviour_segment"] == "Moderate_Engagement_Low_Balance")
].copy()

    low_activity_users_subset = customers_who_have_invested_df[
        (customers_who_have_invested_df["customer_behaviour_segment"] == "Low_Engagement_High_Balance")
    |
    (customers_who_have_invested_df["customer_behaviour_segment"] == "Low_Engagement_Low_Balance")
    ]

    
    active_users_sample = active_users_subset.sample(frac=0.9, random_state = 1)

    low_activity_users_sample = low_activity_users_subset.sample(frac=0.65, random_state = 1)

    engagement_sample_df = pd.concat(
    [active_users_sample, low_activity_users_sample],
    ignore_index=True)


    engagement_dict = create_engagement_events(engagement_sample_df)

    login_engagement_events = engagement_dict['login_events']
    engagement_events = engagement_dict['engagement_events']
    wallet_funding_events = engagement_dict['wallet_funding_events']
    new_investment_creation_events = engagement_dict['investment_events']


    start_position = end_position
    end_position = start_position + len(login_engagement_events)

    uids = login_engagement_events['user_id']
    etime = login_engagement_events['event_time']
    dtypes = [device_type_map.get(uid) for uid in login_engagement_events['user_id']]

    print("Null device types for the users line 357:",pd.isna(dtypes).sum())

    app_login_events(conn, context, start_position, end_position, user_ids, uids, event_time, etime, device_types, dtypes, event_type_ids)

    print("Missing event time values line 326:", pd.isna(event_time[start_position:end_position]).sum())

    start_position = end_position
    end_position = start_position + len(engagement_events)

    uids = engagement_events['user_id']
    etime = engagement_events['event_time']
    dtypes = [device_type_map.get(uid) for uid in engagement_events['user_id']]

    updated_end_position = review_current_investment_events(conn, context, start_position, end_position, user_ids, uids, event_time, etime, device_types, dtypes, event_type_ids)

    start_position = updated_end_position
    end_position = start_position + len(wallet_funding_events)

    uids = wallet_funding_events['user_id']
    dtypes = [device_type_map.get(uid) for uid in wallet_funding_events['user_id']]

    print("Null device types for the users line 378:",pd.isna(dtypes).sum())

    return_dict = create_wallet_funding_events(conn, context, start_position, end_position, user_ids,uids,wallet_ids, event_time, wallet_funding_events['event_time'], last_transaction_id,
                                                device_types, dtypes, is_money_movement_activities, event_type_ids,
                                                transaction_type_ids, transaction_ids, transaction_amounts, transaction_statuses)

    last_transaction_id = return_dict['last_transaction_id']
    updated_end_position = return_dict['updated_end_position']

    print("Missing event time values line 351:", pd.isna(event_time[start_position:end_position]).sum())

    start_position = updated_end_position
    end_position = start_position + len(new_investment_creation_events)

    uids = new_investment_creation_events['user_id']
    etime = new_investment_creation_events['event_time']
    dtypes = [device_type_map.get(uid) for uid in new_investment_creation_events['user_id']]

    print("Null device types for the users line 395:",pd.isna(dtypes).sum())

    inv_type = new_investment_creation_events['investment_type']

    return_dict = new_investment_creation(conn, context, start_position, end_position, user_ids, uids,wallet_ids, event_time, etime, inv_type, device_types, dtypes, 
                                          is_money_movement_activities, transaction_ids, last_transaction_id, transaction_type_ids, event_type_ids, transaction_amounts, 
                                          transaction_statuses, investment_ids, last_investment_id)

    print("Missing event time values line 365:", pd.isna(event_time[start_position:end_position]).sum())

    
    last_transaction_id = return_dict["last_transaction_id"]
    all_investments_df = pd.concat([all_investments_df, return_dict["all_investments_df"]],ignore_index=True)
    end_position = return_dict["updated_end_position"]
    last_investment_id = return_dict["last_investment_id"]

    all_investments_df["investment_status"] = np.select([all_investments_df["investment_maturity_date"] < pd.Timestamp.today()],["Matured"],default="Active")

    all_investments_df["customer_behaviour_segment"] = all_investments_df["user_id"].map(cbs_map)

    conn.register('all_investments_df', all_investments_df)

    plan_names = conn.execute('''select f.investment_id, f.user_id, f.plan_id, p.plan_name, p.penalty_rate_pct from all_investments_df as f inner join dim_plan p on f.plan_id = p.plan_id''').df()

    all_investments_df = all_investments_df.merge(plan_names, how="inner", on=["investment_id", "user_id", "plan_id"])

    conn.unregister('all_investments_df')

    #let's split into vestable investments and saleable investments
    vestable_investments_df = all_investments_df[(all_investments_df["tenure_days"].notna()) & (all_investments_df["investment_maturity_date"].notna()) & (all_investments_df["investment_status"] == "Matured")].copy()

    saleable_investments = all_investments_df[pd.isna(all_investments_df["tenure_days"]) & (all_investments_df["investment_start_date"] <= MUTUAL_FUNDS_CUTOFF_DATE)].copy()

    saleable_investments_df = saleable_investments.sample(frac=0.45,random_state=42)

    active_investments_df = all_investments_df[(all_investments_df["tenure_days"].notna()) & (all_investments_df["investment_status"] == "Active")].copy()


    # simulate early withdrawal requests for vestable investments based on customer behaviour segment probabilities
    vestable_investments_df["requests_early_withdrawal"] = [
        np.random.random()
    <= CUSTOMER_BEHAVIOUR_SEGMENT_MAP[segment]["early_withdrawal_probability"]
    for segment in vestable_investments_df["customer_behaviour_segment"]]

    early_withdrawal_mask = vestable_investments_df["requests_early_withdrawal"] == True
    vested_invested_mask = vestable_investments_df["requests_early_withdrawal"] == False

    vestable_investments_df.loc[early_withdrawal_mask,"investment_status"] = "Withdrawn Early"
    vestable_investments_df.loc[vested_invested_mask,"investment_status"] = "Redeemed"

    early_withrawal_df = (vestable_investments_df.loc[early_withdrawal_mask].copy())

    start_position = end_position
    end_position = start_position + len(early_withrawal_df)

    dtypes = [device_type_map.get(uid) for uid in early_withrawal_df['user_id']]

    print("Null device types for the users line 455:",pd.isna(dtypes).sum())


    #let's create the simulate early withdrawal events
    
    return_dict = early_withdrawal_requests_events(conn, context, start_position, end_position, user_ids, wallet_ids, is_money_movement_activities, last_transaction_id, event_time,
                                                   device_types, dtypes, early_withrawal_df, event_type_ids, transaction_type_ids, transaction_ids, transaction_amounts, 
                                                   transaction_statuses, investment_ids)

    print("Missing event time values line 421:", pd.isna(event_time[start_position:end_position]).sum())

    last_transaction_id = return_dict['last_transaction_id']
    end_position = return_dict['updated_end_position']
    early_withrawal_dataframe = return_dict['early_withdrawal_df']

    #model investment vests transactions for matured investments

    vested_investments_df = (vestable_investments_df.loc[vested_invested_mask].copy())

    print("Vested Investments df columns: ",vested_investments_df.columns)

    start_position = end_position
    end_position = start_position + len(vested_investments_df)

    dtypes = [device_type_map.get(uid) for uid in vested_investments_df['user_id']]

    print("Null device types for the users line 481:",pd.isna(dtypes).sum())

    vested_investments_events(context, start_position, end_position, user_ids, event_time, event_type_ids, device_types,dtypes, investment_ids, vested_investments_df)

    print("Missing event time values line 440:", pd.isna(event_time[start_position:end_position]).sum())

    #model investment proceeds wallet transfer for transactions with matured investments
    start_position = end_position
    end_position = start_position + len(vested_investments_df)

    dtypes = [device_type_map.get(uid) for uid in vested_investments_df['user_id']]

    print("Null device types for the users line 493:",pd.isna(dtypes).sum())

    return_dict = vested_investments_proceeds_transfer_events(conn, context, start_position, end_position, user_ids, event_time, wallet_ids, last_transaction_id, is_money_movement_activities,
                                                transaction_type_ids, transaction_ids, transaction_amounts, transaction_statuses, event_type_ids, device_types, dtypes, investment_ids,
                                                vested_investments_df)

    print("Missing event time values line 452: ",pd.isna(event_time[start_position:end_position]).sum())

    last_transaction_id = return_dict['last_transaction_id']
    vested_investments_dataframe = return_dict['vested_investments_df']

    
    # now let's model asset sales
    saleable_investments_df["days_held"] = (pd.Timestamp.today() - saleable_investments_df["investment_start_date"]).dt.days

    saleable_investments_df["days_held_before_sale"] = [
    int(
        np.random.triangular(
            30,
            min(180, days_held),
            days_held
        )
    )
    for days_held in saleable_investments_df["days_held"]
]

    saleable_investments_df["redemption_request_date"] = (
    saleable_investments_df["investment_start_date"]
    +
    pd.to_timedelta(saleable_investments_df["days_held_before_sale"],unit="D"))

    saleable_investments_df["redemption_request_login_date"] = (
    saleable_investments_df["redemption_request_date"]
    -
    pd.to_timedelta(5,unit="m"))

    saleable_investments_df["review_current_investment_date"] = (
    saleable_investments_df["redemption_request_login_date"]
    +
    pd.to_timedelta(3,unit="m"))

    saleable_investments_df["investment_status"] = "Redeemed"

    #let's model the login first and review of current investments
    start_position = end_position
    end_position = start_position + len(saleable_investments_df)

    dtypes = [device_type_map.get(uid) for uid in saleable_investments_df["user_id"]]

    print("Null device types for the users line 542:",pd.isna(dtypes).sum())


    review_current_investment_events(conn, context, start_position, end_position, user_ids,saleable_investments_df["user_id"],
                                     event_time, saleable_investments_df["review_current_investment_date"],
                                      device_types, dtypes, event_type_ids)

    print("Missing event time values line 500: ",pd.isna(event_time[start_position:end_position]).sum())

    start_position = end_position
    end_position = start_position + len(saleable_investments_df)

    dtypes = [device_type_map.get(uid) for uid in saleable_investments_df["user_id"]]
    
    print("Null device types for the users line 554:",pd.isna(dtypes).sum())

    assets_sale_events(context, start_position, end_position, user_ids, event_time, event_type_ids, device_types, dtypes, investment_ids,saleable_investments_df)

    saleable_investments_df["investment_maturity_date"] = saleable_investments_df["redemption_request_date"]
    saleable_investments_df['investment_maturity_date_id'] = (pd.to_datetime(saleable_investments_df["redemption_request_date"]).dt.strftime('%Y%m%d').astype(int))

    start_position = end_position
    end_position = start_position + len(saleable_investments_df)

    dtypes = [device_type_map.get(uid) for uid in saleable_investments_df["user_id"]]

    print("Null device types for the users line 566:",pd.isna(dtypes).sum())

    return_dict = assets_sale_investment_proceeds_wallet_transfer_events(conn, context, start_position, end_position, user_ids, wallet_ids, event_time, device_types, dtypes, transaction_type_ids,transaction_ids, last_transaction_id,
                                                                         event_type_ids, is_money_movement_activities, transaction_amounts, transaction_statuses, investment_ids,
                                                                         saleable_investments_df)

    last_transaction_id = return_dict['last_transaction_id']
    saleable_investments_df = return_dict['saleable_investments_df']

    saleable_investments_df = saleable_investments_df.drop(
    columns=[
        "days_held",
        "days_held_before_sale",
        "redemption_request_login_date",
        "review_current_investment_date"
    ]
)

    
    print("Null date values ", pd.isna(event_time[:end_position]).sum())
    print("Null device types",pd.isna(device_types[:end_position]).sum())

    # vestable - early_withdrawal_df and vested_investment_df
    # saleable - saleable_investments_df

    vestable_investments_df = pd.concat([early_withrawal_dataframe, vested_investments_dataframe], ignore_index=True)

    saleable_investments.loc[saleable_investments_df.index] = saleable_investments_df

    all_investments_df = pd.concat([active_investments_df, vestable_investments_df, saleable_investments], ignore_index = True)

    #all_investments_df = all_investments_df.drop(['plan_name','tenure_days','penalty_rate_pct'])

    total_events = end_position

    
    #invesment df
    main_df = pd.DataFrame({
        "user_id":user_ids[:total_events],
        "event_type_id":event_type_ids[:total_events],
        "wallet_id":wallet_ids[:total_events],
        "event_time":event_time[:total_events],
        "device_type":device_types[:total_events],
        "is_money_movement_activity":is_money_movement_activities[:total_events],
        "transaction_type_id":transaction_type_ids[:total_events],
        "transaction_id":transaction_ids[:total_events],
        "investment_id":investment_ids[:total_events],
        "transaction_status":transaction_statuses[:total_events],
        "transaction_amount":transaction_amounts[:total_events]
    })

    main_df["event_date_id"] = np.array([
    int(pd.to_datetime(ts).strftime('%Y%m%d'))
    for ts in main_df["event_time"]
    ], dtype=np.int32)

    main_df = main_df.sort_values(by='event_time').reset_index(drop=True)
    
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

    #conn.execute(f'''COPY fact_transaction TO '{FACT_TRANSACTION_PARQUET_PATH}' (FORMAT PARQUET)''')

    investment_positions_df = pd.DataFrame({
        "investment_id":all_investments_df["investment_id"],
        "user_id":all_investments_df["user_id"],
        "wallet_id":all_investments_df["wallet_id"],
        "plan_id":all_investments_df["plan_id"],
        "amount_invested":all_investments_df["amount_invested"],
        "expected_maturity_value":all_investments_df["expected_maturity_value"],
        "investment_start_date":all_investments_df["investment_start_date"],
        "investment_start_date_id": all_investments_df["investment_start_date_id"],
        "investment_maturity_date":all_investments_df["investment_maturity_date"],
        "investment_maturity_date_id":all_investments_df["investment_maturity_date_id"],
        "investment_status":all_investments_df["investment_status"],
        "is_withdrawn_early":all_investments_df["is_withdrawn_early"],
        "penalty_amount":all_investments_df["penalty_amount"],
        "amount_paid_out":all_investments_df["amount_paid_out"],
        "redemption_request_date":all_investments_df["redemption_request_date"],
        "early_withdrawal_date":all_investments_df["early_withdrawal_date"],
        "early_withdrawal_date_id":all_investments_df["early_withdrawal_date_id"],
        "created_at":all_investments_df["created_at"],
        "last_updated_at":all_investments_df["last_updated_at"]
    })

    conn.register("investment_df",investment_positions_df)

    conn.execute('''INSERT INTO FACT_INVESTMENT_POSITION SELECT * FROM INVESTMENT_DF''')

    conn.execute(f'''COPY FACT_INVESTMENT_POSITION TO '{FACT_INVESTMENT_POSITION_PARQUET_PATH}' (FORMAT PARQUET) ''')

    df_raw = pd.DataFrame({
        "user_id":user_ids[:total_events],
        "event_type_id":event_type_ids[:total_events],
        "wallet_id":wallet_ids[:total_events],
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

    conn.execute(f'''COPY FACT_USER_EVENT TO '{FACT_USER_EVENT_PARQUET_PATH}' (FORMAT PARQUET) ''')

    conn.execute(f'''COPY FACT_WALLET_BALANCE TO '{FACT_WALLET_BALANCE_PARQUET_PATH}' (FORMAT PARQUET)''')

    conn.execute(f'''COPY (
                            SELECT user_id, first_name, last_name, country, region, city, email_address, reported_annual_income,
                            acquisition_channel, device_type, customer_persona, kyc_completed, date_of_birth, birth_date_id, signup_date, signup_date_id, 
                            customer_behaviour_segment, last_login_at, created_at, last_updated_at
                            from dim_user )
                     TO '{USERS_PARQUET_PATH}' (FORMAT PARQUET) ''')

    conn.execute(f'''COPY DIM_WALLET TO '{WALLETS_PARQUET_PATH}' (FORMAT PARQUET)''')