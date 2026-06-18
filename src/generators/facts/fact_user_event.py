import numpy as np
import pandas as pd
from src.config.paths import (DDL_FACT_USER_EVENT_PATH, FACT_USER_EVENT_PARQUET_PATH)
from src.config.constants import (DEFAULT_TRANSACTION_START_TIMESTAMP,DEFAULT_TRANSACTION_START_DATE,
                                  IMMEDIATE_LOGINS_TIME_FRAME, KYC_ACTIVATION_TIMEFRAME, USERS_MAKES_FIRST_INVESTMENT_AFTER_FUNDING,
                                  CUSTOMER_BEHAVIOUR_SEGMENT_MAP, FIRST_INVESTMENT_TYPE
                                  )
from datetime import timedelta


def generate_fact_events(conn, num_of_events):

    create_db = DDL_FACT_USER_EVENT_PATH.read_text()

    conn.execute(create_db)

    #populate all possible signups within the project duration
    users_data = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, wallet_activation_timeframe, customer_behaviour_segment, device_type FROM dim_user
     where signup_date >= '{DEFAULT_TRANSACTION_START_DATE}' order by signup_date''').df()
    
    user_wallet_data = conn.execute(f'''SELECT user_id, wallet_id, wallet_activated_at from dim_wallet''').df()

    plans_data = conn.execute('''
        SELECT * FROM dim_plan
    ''').df()

    device_type_map = dict(
        zip(
            users_data["user_id"],
            users_data["device_type"]
        )
    )

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

    plan_id_map = dict(zip(
        plans_data["plan_id"],
        plans_data["tenure_days"]
    ))

    #event_id (PK), user_id, event_type_id, wallet_id, plan_id,event_time ,event_date_id,device_type,is_money_movement_activity
    #transaction_type_id, transaction_id, investment_id

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

    event_date_ids = np.empty(num_of_events, dtype=object)


    # new user signups
    total_signups = len(users_data)

    user_ids[:total_signups] = users_data["user_id"]
    event_time[:total_signups] = users_data["signup_date"]
    event_type_ids[:total_signups] = event_type_map.get("signup_completed")
    device_types[:total_signups] = np.array([device_type_map.get(uid) for uid in users_data["user_id"]])

    #new user logins
    new_users_logins = conn.execute(f'''SELECT user_id, signup_date, kyc_completed, is_activated_user, customer_behaviour_segment FROM dim_user
     where signup_date >= '{DEFAULT_TRANSACTION_START_DATE}' AND is_immediate_login = True order by signup_date''').df()
    
    immediate_login_timeframe = np.random.randint(IMMEDIATE_LOGINS_TIME_FRAME[0],IMMEDIATE_LOGINS_TIME_FRAME[1], size=len(new_users_logins))
    
    total_new_users = len(new_users_logins)

    start_immediate_logins = total_signups
    end_immediate_logins = start_immediate_logins + total_new_users

    user_ids[start_immediate_logins:end_immediate_logins] = new_users_logins["user_id"]
    event_time[start_immediate_logins:end_immediate_logins] = [pd.Timestamp(sd) + timedelta(seconds=int(ro)) for sd, ro in zip(new_users_logins["signup_date"], immediate_login_timeframe)]
    event_type_ids[start_immediate_logins:end_immediate_logins] = event_type_map.get("app_login")
    device_types[start_immediate_logins:end_immediate_logins] = np.array([device_type_map.get(uid) for uid in new_users_logins["user_id"]])

    #kyc_completed_users
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
    device_types[start_kyc_activations:end_kyc_activations] = np.array([device_type_map.get(uid) for uid in kyc_completed_users["user_id"]])

    start_kyc_activation_completion = end_kyc_activations
    end_kyc_activation_completion = start_kyc_activation_completion + len(kyc_completed_users)

    user_ids[start_kyc_activation_completion:end_kyc_activation_completion] = kyc_completed_users["user_id"]
    event_time[start_kyc_activation_completion:end_kyc_activation_completion] = [last_login_map.get(uid,signup_map.get(uid)) + timedelta(minutes=int(ro)) for uid, ro in zip(kyc_completed_users["user_id"], kyc_activation_timeframe)]
    event_type_ids[start_kyc_activation_completion:end_kyc_activation_completion] = event_type_map.get("kyc_completed")
    device_types[start_kyc_activation_completion:end_kyc_activation_completion] = np.array([device_type_map.get(uid) for uid in kyc_completed_users["user_id"]])

    kyc_completion_time = event_time[start_kyc_activation_completion:end_kyc_activation_completion]

    #wallet activation
    kyc_dict = dict(zip(kyc_completed_users["user_id"], kyc_completion_time))
    
    wallet_activated_users = kyc_completed_users[~pd.isna(kyc_completed_users["wallet_activation_timeframe"])].copy()

    segment_customers = dict(zip(
        users_data["user_id"],
        users_data["customer_behaviour_segment"]
    ))

    wallet_activated_users["customer_behaviour_segment"] = wallet_activated_users["user_id"].map(segment_customers)

    wallet_activated_users["amount_invested"] = np.array([
        np.random.randint(CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["average_investment_amount"][0],
            CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["average_investment_amount"][1]
            
        )
        for bh in wallet_activated_users["customer_behaviour_segment"]
    ])

    total_wallet_activated_users = len(wallet_activated_users)

    start_wallet_activations = end_kyc_activation_completion
    end_wallet_activations = start_wallet_activations + total_wallet_activated_users

    user_ids[start_wallet_activations:end_wallet_activations] = wallet_activated_users["user_id"]
    event_time[start_wallet_activations:end_wallet_activations] = [kyc_dict.get(uid,None) + timedelta(minutes=int(ro)) for uid, ro in zip(wallet_activated_users["user_id"], wallet_activated_users["wallet_activation_timeframe"])]
    event_type_ids[start_wallet_activations:end_wallet_activations] = event_type_map.get("wallet_funded")
    is_money_movement_activities[start_wallet_activations:end_wallet_activations] = True
    wallet_ids[start_wallet_activations:end_wallet_activations] = [wallet_id_map.get(uid) for uid in wallet_activated_users["user_id"]]
    transaction_type_ids[start_wallet_activations:end_wallet_activations] = [transaction_type_map.get("wallet_funding") for _ in range(len(wallet_activated_users))]
    transaction_ids[start_wallet_activations:end_wallet_activations] = np.arange(1, total_wallet_activated_users + 1)
    amount_invested[start_wallet_activations:end_wallet_activations] = wallet_activated_users["amount_invested"]
    last_transaction_id = transaction_ids[start_wallet_activations:end_wallet_activations].max()
    device_types[start_wallet_activations:end_wallet_activations] = np.array([device_type_map.get(uid) for uid in wallet_activated_users["user_id"]])

    wallet_activated_users_df = pd.DataFrame(
        {
            "user_id": user_ids[start_wallet_activations:end_wallet_activations],
            "last_login_time": event_time[start_wallet_activations:end_wallet_activations],
            "current_wallet_balance": amount_invested[start_wallet_activations:end_wallet_activations]
        }
    )

    #let's create the initial investment -- login, review_plan_options then drop off for some users, and for others, they will make an investment after reviewing the plan options. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.

    wallet_activated_users_df = pd.DataFrame({
        "user_id": wallet_activated_users_df["user_id"],
        "customer_behaviour_segment": wallet_activated_users_df["user_id"].map(segment_customers),
        "last_login_time": wallet_activated_users_df["last_login_time"],
        "current_wallet_balance":wallet_activated_users_df["current_wallet_balance"]
        })
    
    customer_subset_1 = wallet_activated_users_df.sample(frac = 0.55, random_state=1)

    total_customer_subset_1 = len(customer_subset_1)

    #these users will just login and review plan options, but will not make an investment. We will create a new dataframe to hold the users who made an investment and their corresponding investment details.

    start_position = end_wallet_activations
    end_position = start_position + total_customer_subset_1

    user_ids[start_position:end_position] = customer_subset_1["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(5, 80)) for last_login in customer_subset_1["last_login_time"]]
    event_type_ids[start_position:end_position] = event_type_map.get("app_login")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_1["user_id"]])

    login_time_for_review_plan_options = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_1

    user_ids[start_position:end_position] = customer_subset_1["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(2, 5)) for last_login in login_time_for_review_plan_options]
    event_type_ids[start_position:end_position] = event_type_map.get("review_plan_options")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_1["user_id"]])

    customer_behaviour_segment_wallet_activated_users = wallet_activated_users_df['customer_behaviour_segment']

    probability_of_making_first_investment = [
    np.random.choice(
        USERS_MAKES_FIRST_INVESTMENT_AFTER_FUNDING,
        p=CUSTOMER_BEHAVIOUR_SEGMENT_MAP[cp][
            'wallet_to_investment_conversion_probability'
        ]
    )
    for cp in customer_behaviour_segment_wallet_activated_users
]

    mins_to_first_investment = [
    np.random.randint(
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[cp]['days_to_first_investment'][0],
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[cp]['days_to_first_investment'][1] + 1
    )
    for cp in customer_behaviour_segment_wallet_activated_users
]

    first_investment_type = [np.random.choice(
        FIRST_INVESTMENT_TYPE,
        p= CUSTOMER_BEHAVIOUR_SEGMENT_MAP[cp][
            'first_investment_type_probability'
        ]
    )
    for cp in customer_behaviour_segment_wallet_activated_users]

    wallet_activated_users_df['makes_first_investment'] = probability_of_making_first_investment

    wallet_activated_users_df['mins_to_first_investment'] = mins_to_first_investment

    wallet_activated_users_df['first_investment_type'] = first_investment_type

    customer_subset_2 = wallet_activated_users_df[wallet_activated_users_df['makes_first_investment'] == True]

    customer_subset_2 = customer_subset_2.copy().reset_index(drop=True)

    total_customer_subset_2 = len(customer_subset_2)

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(0, mtft)) for last_login,mtft in zip(customer_subset_2["last_login_time"],customer_subset_2["mins_to_first_investment"])]
    event_type_ids[start_position:end_position] = event_type_map.get("app_login")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])

    login_time_for_review_plan_options_2 = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_login + timedelta(minutes=np.random.randint(2, 5)) for last_login in login_time_for_review_plan_options_2]
    event_type_ids[start_position:end_position] = event_type_map.get("review_plan_options")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])

    last_review_time_for_investment = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_review + timedelta(minutes=np.random.randint(1, 3)) for last_review in last_review_time_for_investment]
    event_type_ids[start_position:end_position] = event_type_map.get("plan_selected")
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])


    last_plan_selected_time = event_time[start_position:end_position]

    start_position = end_position
    end_position = start_position + total_customer_subset_2

    user_ids[start_position:end_position] = customer_subset_2["user_id"]
    event_time[start_position:end_position] = [last_review + timedelta(minutes=np.random.randint(3,5)) for last_review in last_plan_selected_time]
    device_types[start_position:end_position] = np.array([device_type_map.get(uid) for uid in customer_subset_2["user_id"]])

    investment_type_event_type = [
    "savings_plan_created"
    if inv == "Savings"
    else "investment_plan_created"
    for inv in customer_subset_2["first_investment_type"]
    ]
    
    event_type_ids[start_position:end_position] = [event_type_map.get(inv) for inv in investment_type_event_type]
    is_money_movement_activities[start_position:end_position] = True
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, last_transaction_id +  len(customer_subset_2) + 1)
    transaction_type_ids[start_position:end_position] = [transaction_type_map.get("investment_funding") for _ in range(len(customer_subset_2))]
    investment_ids[start_position:end_position] = np.arange(1000, 1000 + len(customer_subset_2))
    last_investment_id = investment_ids[start_position:end_position].max()

    select_plan_ids = np.empty(len(customer_subset_2),dtype=object)

    savings_plans = conn.execute('''SELECT * FROM dim_plan WHERE plan_category = 'Savings' ''').df()
    investment_plans = conn.execute('''SELECT * FROM dim_plan WHERE plan_category = 'Investments' ''').df()

    savings_mask = np.where(customer_subset_2["first_investment_type"] == 'Savings')[0]
    investments_mask = np.where(customer_subset_2["first_investment_type"] == 'Investments')[0]

    select_plan_ids[savings_mask] = [np.random.choice(savings_plans["plan_id"], 
                                            p = savings_plans["plan_weight"] / savings_plans["plan_weight"].sum())
                                     for _ in range(len(savings_mask))]
    select_plan_ids[investments_mask] = [np.random.choice(investment_plans["plan_id"], 
                                        p = investment_plans["plan_weight"] / investment_plans["plan_weight"].sum())
                                         for _ in range(len(investments_mask))]

    plan_ids[start_position:end_position] = select_plan_ids
    wallet_ids[start_position:end_position] = [wallet_id_map.get(uid) for uid in customer_subset_2["user_id"]]
    investment_pct = np.random.uniform(
    0.5,
    0.95,
    len(customer_subset_2)
)
    amount_invested[start_position:end_position] = (
    customer_subset_2["current_wallet_balance"].values
    * investment_pct
)

    last_transaction_id = transaction_ids[start_position:end_position].max()

    customers_who_have_invested_df = pd.DataFrame({
        "user_id": user_ids[start_position:end_position],
        "last_login_time":event_time[start_position:end_position],
        "customer_behaviour_segment":customer_subset_2["customer_behaviour_segment"]
    })

    avg_number_of_logins_per_month = np.array([
    np.random.randint(
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_logins"][0],
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_logins"][1] + 1
    )
    for bh in customers_who_have_invested_df["customer_behaviour_segment"]
])
    

    customers_who_have_invested_df["monthly_logins"] = avg_number_of_logins_per_month

    monthly_portfolio_reviews = np.array([
    np.random.randint(
        max(1, int(logins * 0.3)),
        max(2, int(logins * 0.7))
    )
    for logins in avg_number_of_logins_per_month
])

    customers_who_have_invested_df["monthly_portfolio_reviews"] = monthly_portfolio_reviews

    monthly_wallet_fundings = np.array([
        np.random.randint(
           CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_wallet_fundings"][0],
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_wallet_fundings"][1] + 1
    )
    for bh in customers_who_have_invested_df["customer_behaviour_segment"]
    ])

    monthly_investment_position_creation = np.array([
        np.random.randint(
           CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_investment_position_creation"][0],
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_investment_position_creation"][1] + 1
    )
    for bh in customers_who_have_invested_df["customer_behaviour_segment"]
    ])

    monthly_savings_position_creation = np.array([
        np.random.randint(
           CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_savings_position_creation"][0],
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["monthly_savings_position_creation"][1] + 1
    )
    for bh in customers_who_have_invested_df["customer_behaviour_segment"]
    ])
    
    customers_who_have_invested_df["monthly_wallet_fundings"] = monthly_wallet_fundings

    customers_who_have_invested_df["monthly_plan_fundings"] = np.maximum(monthly_wallet_fundings - 2, 0)

    customers_who_have_invested_df["monthly_investment_position_creation"] = monthly_investment_position_creation

    customers_who_have_invested_df["monthly_savings_position_creation"] = monthly_savings_position_creation

    customers_who_have_invested_df["investment_low_bound"] = np.array([
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["average_investment_amount"][0]
        for bh in customers_who_have_invested_df["customer_behaviour_segment"]
    ])

    customers_who_have_invested_df["investment_high_bound"] = np.array([
        CUSTOMER_BEHAVIOUR_SEGMENT_MAP[bh]["average_investment_amount"][1]
        for bh in customers_who_have_invested_df["customer_behaviour_segment"]
    ])


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

    engagement_events = []

    for _, customer in active_users_sample.iterrows():

        monthly_logins = customer["monthly_logins"]
        monthly_reviews = customer["monthly_portfolio_reviews"]

    # simulate one month after investment creation
        month_start = customer["last_login_time"]

    # Login events
        login_times = sorted([
        month_start + timedelta(
            days=np.random.randint(0, 30),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        for _ in range(monthly_logins)
    ])

        for login_time in login_times:
            engagement_events.append({
            "user_id": customer["user_id"],
            "event_time": login_time,
            "event_type": "app_login"
        })

    # Portfolio reviews must happen after a login
        if len(login_times) > 0:

            review_login_times = np.random.choice(
            login_times,
            size=min(monthly_reviews, len(login_times)),
            replace=False
        )

            for login_time in review_login_times:

                review_time = login_time + timedelta(
                minutes=np.random.randint(1, 30)
            )

                engagement_events.append({
                "user_id": customer["user_id"],
                "event_time": review_time,
                "event_type": "review_current_investment"
            })

    engagement_events_df = pd.DataFrame(engagement_events)

    start_position = end_position
    end_position = start_position + len(engagement_events_df)

    user_ids[start_position:end_position] = (engagement_events_df["user_id"].values)

    event_time[start_position:end_position] = (engagement_events_df["event_time"].values)

    event_type_ids[start_position:end_position] = [event_type_map.get(event_type)for event_type in engagement_events_df["event_type"]]

    device_types[start_position:end_position] = [device_type_map.get(uid)for uid in engagement_events_df["user_id"]]
    
    #portfolio reviews for low activity users
    low_engagement_events = []


    for _, customer in low_activity_users_sample.iterrows():

        monthly_logins = customer["monthly_logins"]
        monthly_reviews = customer["monthly_portfolio_reviews"]

    # simulate one month after investment creation
        month_start = customer["last_login_time"]

    # Login events
        login_times = sorted([
        month_start + timedelta(
            days=np.random.randint(0, 30),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        for _ in range(monthly_logins)
    ])

        for login_time in login_times:
            low_engagement_events.append({
            "user_id": customer["user_id"],
            "event_time": login_time,
            "event_type": "app_login"
        })

    # Portfolio reviews must happen after a login
        if len(login_times) > 0:

            review_login_times = np.random.choice(
            login_times,
            size=min(monthly_reviews, len(login_times)),
            replace=False
        )

            for login_time in review_login_times:

                review_time = login_time + timedelta(
                minutes=np.random.randint(1, 30)
            )

                low_engagement_events.append({
                "user_id": customer["user_id"],
                "event_time": review_time,
                "event_type": "review_current_investment"
            })

    low_engagement_events_df = pd.DataFrame(low_engagement_events)

    
    start_position = end_position
    end_position = start_position + len(low_engagement_events_df)



    user_ids[start_position:end_position] = (low_engagement_events_df["user_id"].values)

    event_time[start_position:end_position] = (low_engagement_events_df["event_time"].values)

    event_type_ids[start_position:end_position] = [event_type_map.get(event_type)for event_type in low_engagement_events_df["event_type"]]

    device_types[start_position:end_position] = [device_type_map.get(uid)for uid in low_engagement_events_df["user_id"]]


    # let's simulate new investment creation

    wallet_funding_events = []
    new_investment_events = []
    new_investment_creation = []

    for _, customer in customers_who_have_invested_df.iterrows():

        num_wallet_fundings = customer["monthly_wallet_fundings"]

        for _ in range(num_wallet_fundings):

            funding_time = customer["last_login_time"] + timedelta(
            days=np.random.randint(1, 31),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )

            funding_amount = np.random.lognormal(
            customer["investment_low_bound"],
            customer["investment_high_bound"] + 1
        )

        # Wallet funding event
            wallet_funding_events.append({
            "user_id": customer["user_id"],
            "event_time": funding_time,
            "event_type": "wallet_funded",
            "amount": funding_amount
        })

        # Decide whether funding converts into an investment
            segment = customer["customer_behaviour_segment"]

            makes_investment = np.random.choice([True, False], p=CUSTOMER_BEHAVIOUR_SEGMENT_MAP[segment]["wallet_to_investment_conversion_probability"])

            if not makes_investment:
                continue

        # Review plans
            review_time = funding_time + timedelta(
            minutes=np.random.randint(5, 60)
        )

        # Plan selected
            selection_time = review_time + timedelta(
            minutes=np.random.randint(1, 30)
        )
            
            total_positions = (customer["monthly_savings_position_creation"]+customer["monthly_investment_position_creation"])

            if total_positions == 0:
                continue

        # Savings or Investment
            investment_type = np.random.choice(
            ["Savings", "Investment"],
            p=[
                customer["monthly_savings_position_creation"] /
                (
                    customer["monthly_savings_position_creation"]
                    +
                    customer["monthly_investment_position_creation"]
                    + 0.0001
                ),

                customer["monthly_investment_position_creation"]
                /
                (
                    customer["monthly_savings_position_creation"]
                    +
                    customer["monthly_investment_position_creation"]
                    + 0.0001
                )
            ]
        )

            creation_time = selection_time + timedelta(
            minutes=np.random.randint(1, 15)
        )

            if investment_type == "Savings":

                plan_id = np.random.choice(
                savings_plans["plan_id"],
                p=savings_plans["plan_weight"] / savings_plans["plan_weight"].sum()
            )

                event_type = "savings_plan_created"
            else:

                plan_id = np.random.choice(
                investment_plans["plan_id"],
                p=investment_plans["plan_weight"] / investment_plans["plan_weight"].sum()
            )

                event_type = "investment_plan_created"

            new_investment_events.extend([
            {
                "user_id": customer["user_id"],
                "event_time": review_time,
                "event_type": "review_plan_options"
            },
            {
                "user_id": customer["user_id"],
                "event_time": selection_time,
                "event_type": "plan_selected"
            }
            ])


            new_investment_creation.extend([{
                "user_id": customer["user_id"],
                "event_time": creation_time,
                "event_type": event_type,
                "plan_id": plan_id,
                "amount_invested": funding_amount
            }
        ])



    wallet_funding_events_df = pd.DataFrame(wallet_funding_events)
    new_investment_events_df = pd.DataFrame(new_investment_events)

    new_investment_creation_df = pd.DataFrame(new_investment_creation)

    #get app logins first
    start_position = end_position
    end_position = start_position + len(wallet_funding_events_df)

    
    user_ids[start_position:end_position] = (wallet_funding_events_df["user_id"].values)

    login_times = wallet_funding_events_df["event_time"].values - timedelta(minutes=5)

    event_time[start_position:end_position] = login_times
    event_type_ids[start_position:end_position] = [event_type_map.get("app_login") for _ in range(len(wallet_funding_events_df))]
    device_types[start_position:end_position] = [device_type_map.get(uid) for uid in wallet_funding_events_df["user_id"]]

    #now fund the wallets
    start_position = end_position
    end_position = start_position + len(wallet_funding_events_df)

    
    user_ids[start_position:end_position] = (wallet_funding_events_df["user_id"].values)

    login_times = wallet_funding_events_df["event_time"].values

    event_time[start_position:end_position] = login_times
    event_type_ids[start_position:end_position] = [event_type_map.get("wallet_funded") for _ in range(len(wallet_funding_events_df))]
    wallet_ids[start_position:end_position] = [wallet_id_map.get(uid) for uid in wallet_funding_events_df["user_id"].values]
    is_money_movement_activities[start_position:end_position] = True
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, last_transaction_id + len(wallet_funding_events_df) + 1)
    transaction_type_ids[start_position:end_position] = [transaction_type_map.get("wallet_funding") for _ in range(len(wallet_funding_events_df))]
    last_transaction_id = transaction_ids[start_position:end_position].max()
    amount_invested[start_position:end_position] = wallet_funding_events_df["amount"]
    device_types[start_position:end_position] = [device_type_map.get(uid) for uid in wallet_funding_events_df["user_id"]]
    


    #plan selections
    start_position = end_position
    end_position = start_position + len(new_investment_events_df)
    
    user_ids[start_position:end_position] = (new_investment_events_df["user_id"].values)

    event_time[start_position:end_position] = (new_investment_events_df["event_time"].values)

    event_type_ids[start_position:end_position] = [event_type_map.get(event_type)for event_type in new_investment_events_df["event_type"]]

    device_types[start_position:end_position] = [device_type_map.get(uid)for uid in new_investment_events_df["user_id"]]

    #plan_ids[start_position:end_position] = (new_investment_events_df["plan_id"].values) #??


    start_position = end_position
    end_position = start_position + len(new_investment_creation_df)

    user_ids[start_position:end_position] = (new_investment_creation_df["user_id"].values)

    event_time[start_position:end_position] = (new_investment_creation_df["event_time"].values)

    event_type_ids[start_position:end_position] = [event_type_map.get(event_type)for event_type in new_investment_creation_df["event_type"]]

    device_types[start_position:end_position] = [device_type_map.get(uid)for uid in new_investment_creation_df["user_id"]]

    plan_ids[start_position:end_position] = (new_investment_creation_df["plan_id"].values)

    wallet_ids[start_position:end_position] = [wallet_id_map.get(uid) for uid in new_investment_creation_df["user_id"].values]

    amount_invested[start_position:end_position] = (new_investment_creation_df["amount_invested"].values)

    is_money_movement_activities[start_position:end_position] = True
    transaction_ids[start_position:end_position] = np.arange(last_transaction_id + 1, last_transaction_id + len(new_investment_creation_df) + 1)
    transaction_type_ids[start_position:end_position] = [transaction_type_map.get("investment_funding") for _ in range(len(new_investment_creation_df))]
    last_transaction_id = transaction_ids[start_position:end_position].max()
    investment_ids[start_position:end_position] = np.arange(last_investment_id + 1, len(new_investment_creation_df) + last_investment_id + 1)
    last_investment_id = investment_ids[start_position:end_position].max()

    main_df = pd.DataFrame({
        "user_id":user_ids[:end_position],
        "event_type_id":event_type_ids[:end_position],
        "wallet_id":wallet_ids[:end_position],
        "plan_id":plan_ids[:end_position],
        "event_time":event_time[:end_position],
        "investment_id":investment_ids[:end_position],
        "transaction_id":transaction_ids[:end_position]
    })

    investments_subset_df = main_df[~pd.isna(main_df["investment_id"])]

    

    event_date_ids = np.array([
    int(pd.Timestamp(ts).strftime('%Y%m%d'))
    for ts in event_time
    ], dtype=np.int32)
    

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