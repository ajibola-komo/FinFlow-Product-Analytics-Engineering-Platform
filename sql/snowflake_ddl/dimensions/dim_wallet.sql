CREATE OR REPLACE TABLE dim_wallet(
    wallet_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    wallet_currency varchar(50) NOT NULL,
    wallet_created_at TIMESTAMP_NTZ NOT NULL,
    wallet_activated_at TIMESTAMP_NTZ,
    wallet_created_date_id INT NOT NULL,
    wallet_activated_date_id INT
);