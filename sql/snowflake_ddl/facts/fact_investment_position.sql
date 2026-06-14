CREATE OR REPLACE TABLE FACT_INVESTMENT_POSITION(
    investment_id int primary key,
    user_id bigint not null,
    wallet_id bigint not null,
    plan_id int not null,
    amount_invested decimal(18,2) not null,
    investment_start_date timestamp not null,
    investment_start_date_id int not null,
    investment_maturity_date timestamp not null,
    investment_maturity_date_id int not null,
    investment_status varchar(20) not null
);