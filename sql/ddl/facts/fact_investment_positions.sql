CREATE OR REPLACE TABLE FACT_INVESTMENT_POSITIONS(
    investment_id int primary key,
    user_id int,
    plan_id int,
    amount_invested decimal(10,2),
    start_date timestamp,
    maturity_date timestamp,
    tenure_days int,
    transaction_id int,
    wallet_id int
);