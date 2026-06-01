CREATE OR REPLACE TABLE FACT_INVESTMENT_POSITION(
    investment_id int primary key,
    user_id int not null,
    plan_id int not null,
    amount_invested decimal(18,2) not null,
    investment_start_date timestamp not null,
    investment_start_date_id int not null,
    investment_maturity_date timestamp not null,
    investment_maturity_date_id int not null,
    investment_status varchar(20) not null,
    event_id int not null,
    transaction_id int not null,
    foreign key(user_id) references dim_user(user_id),
    foreign key(plan_id) references dim_plan(plan_id),
    foreign key(event_id) references fact_event(event_id),
    foreign key(transaction_id) references fact_transaction(transaction_id),
    foreign key(investment_start_date_id) references dim_date(date_id),
    foreign key(investment_maturity_date_id) references dim_date(date_id)
);