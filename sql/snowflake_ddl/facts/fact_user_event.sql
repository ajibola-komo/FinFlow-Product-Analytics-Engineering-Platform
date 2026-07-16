CREATE OR REPLACE TABLE FACT_USER_EVENT (
    event_id bigint primary key,
    user_id bigint not null,
    event_type_id int not null,
    wallet_id bigint,
    plan_id int,
    event_time timestamp not null,
    event_date_id bigint not null,
    device_type varchar(50),
    is_money_movement_activity boolean,
    transaction_type_id int,
    transaction_id bigint, -- degenerate key
    investment_id bigint --degenerate key
);