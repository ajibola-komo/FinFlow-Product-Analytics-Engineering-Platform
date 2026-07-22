create table fact_wallet_balance(
    wallet_id int primary key,
    user_id int not null unique,
    current_balance decimal(15,2) not null default 0.00,
    created_at timestamp not null,
    last_updated_at timestamp not null,
    last_updated_date_id int,
    last_transaction_id int, -- degenerate key
    last_event_id int, -- degenerate key
    foreign key(wallet_id) references dim_wallet(wallet_id),
    foreign key(user_id) references dim_user(user_id),
    foreign key(last_updated_date_id) references dim_date(date_id)
);