CREATE OR REPLACE TABLE dim_wallet(
    wallet_id INT,
    user_id INT,
    wallet_currency varchar(50),
    wallet_created_at TIMESTAMP_NTZ,
    wallet_activated_at TIMESTAMP_NTZ,
    wallet_created_date_id INT,
    wallet_activated_date_id INT
);