CREATE OR REPLACE TABLE dim_wallet(
    wallet_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    wallet_currency varchar(50),
    wallet_created_at TIMESTAMP,
    wallet_activated_at TIMESTAMP,
    wallet_created_date_id INT,
    wallet_activated_date_id INT,
    foreign key (user_id) references dim_user(user_id),
    foreign key (wallet_created_date_id) references dim_date(date_id),
    foreign key (wallet_activated_date_id) references dim_date(date_id)
);