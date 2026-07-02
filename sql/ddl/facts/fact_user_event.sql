CREATE OR REPLACE TABLE FACT_USER_EVENT (
    event_id bigint,
    user_id int,
    event_type_id int,
    wallet_id int,
    plan_id int,
    event_time timestamp,
    event_date_id int,
    device_type varchar(50),
    is_money_movement_activity boolean,
    transaction_type_id int,
    transaction_id bigint, -- degenerate key
    investment_id bigint --degenerate key
);