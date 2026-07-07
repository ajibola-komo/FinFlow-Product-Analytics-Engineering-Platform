CREATE OR REPLACE TABLE FACT_INVESTMENT_POSITION(
    investment_id bigint primary key,
    user_id bigint,
    wallet_id bigint,
    plan_id int,
    amount_invested decimal(18,2),
    investment_start_date timestamp,
    investment_start_date_id int,
    investment_maturity_date timestamp,
    investment_maturity_date_id int,
    investment_status varchar(20),
    is_withdrawn_early boolean,
    early_withdrawal_date timestamp,
    early_withdrawal_date_id int
);