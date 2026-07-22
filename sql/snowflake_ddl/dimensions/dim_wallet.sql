CREATE OR REPLACE TABLE dim_wallet(
    wallet_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    wallet_currency varchar(50) NOT NULL,
    wallet_created_at TIMESTAMP NOT NULL,
    wallet_activated_at TIMESTAMP,
    wallet_created_date_id INT NOT NULL,
    wallet_activated_date_id INT,
    created_at timestamp not null,
    last_updated_at timestamp not null
);