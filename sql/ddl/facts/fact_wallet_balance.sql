create table fact_wallet_balance(
    wallet_id int primary key,
    user_id int not null unique,
    current_balance decimal(15,2) not null default 0.00,
    last_updated_date timestamp not null,
    last_updated_date_id int,
    last_transaction_id int, -- degenerate key
    created_at timestamp not null,
    updated_at timestamp not null
);