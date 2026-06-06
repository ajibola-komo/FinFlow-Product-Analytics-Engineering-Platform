CREATE OR REPLACE TABLE FACT_USER_EVENT (
    event_id int primary key,
    user_id int not null,
    event_type_id int not null,
    investment_id int,
    wallet_id int not null,
    event_time timestamp not null,
    event_date_id int not null,
    foreign key(user_id) references dim_user(user_id),
    foreign key(event_type_id) references dim_event_type(event_type_id),
    foreign key(wallet_id) references dim_wallet(wallet_id),
    foreign key(event_date_id) references dim_date(date_id)
);