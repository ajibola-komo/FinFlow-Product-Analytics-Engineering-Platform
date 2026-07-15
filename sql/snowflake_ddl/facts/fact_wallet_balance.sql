create table fact_wallet_balance(
    wallet_id int primary key,
    user_id int not null unique,
    current_balance decimal(15,2) not null default 0.00,
    updated_at timestamp not null,
    last_transaction_id int,
    last_event_id int,
    foreign key(wallet_id) references dim_wallet(wallet_id),
    foreign key(user_id) references dim_user(user_id),
    foreign key(last_transaction_id) references fact_transaction(transaction_id),
    foreign key(last_event_id) references fact_user_event(event_id)
);