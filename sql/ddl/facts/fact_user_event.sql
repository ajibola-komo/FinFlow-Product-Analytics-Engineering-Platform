CREATE OR REPLACE TABLE FACT_USER_EVENT (
    event_id int primary key,
    user_id int not null,
    event_type_id int not null,
    wallet_id int,
    plan_id int,
    event_time timestamp not null,
    event_date_id int not null,
    device_type varchar(50),
    is_money_movement_activity boolean,
    transaction_type_id int,
    investment_id int, --degenerate key
    transaction_id int, -- degenerate key
    foreign key(user_id) references dim_user(user_id),
    foreign key(event_type_id) references dim_event_type(event_type_id),
    foreign key(wallet_id) references dim_wallet(wallet_id),
    foreign key(event_date_id) references dim_date(date_id),
    foreign key(transaction_type_id) references dim_transaction_type(transaction_type_id)
);