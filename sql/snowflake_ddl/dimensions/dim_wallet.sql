CREATE OR REPLACE TABLE dim_wallet(
    wallet_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    wallet_currency varchar(50),
    created_at TIMESTAMP,
    activated_at TIMESTAMP,
    wallet_created_date_id INT,
    wallet_activated_date_id INT,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    foreign key (user_id) references dim_user(user_id)
);