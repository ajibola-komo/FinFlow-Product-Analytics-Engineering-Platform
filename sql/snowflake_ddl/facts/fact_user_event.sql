CREATE OR REPLACE TABLE FACT_USER_EVENT (
    event_id int primary key,
    user_id int,
    event_type_id int,
    investment_id int,
    wallet_id int,
    event_time timestamp,
    event_date_id int,
    foreign key(user_id) references dim_user(user_id),
    foreign key(event_type_id) references dim_event_type(event_type_id),
    --foreign key(investment_id) references dim_investment(investment_id),
    foreign key(wallet_id) references dim_wallet(wallet_id),
    foreign key(event_date_id) references dim_date(date_id)
);