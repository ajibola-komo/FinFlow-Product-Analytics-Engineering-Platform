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
    transaction_id int -- degenerate key
);