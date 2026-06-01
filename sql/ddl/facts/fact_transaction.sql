  CREATE OR REPLACE TABLE  FACT_TRANSACTION( 
    transaction_id INT primary key,
    wallet_id INT NOT NULL,
    event_id INT NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    transaction_amount DECIMAL(18,2) NOT NULL,
    transaction_fee_amount DECIMAL(18,2) NOT NULL,
    transaction_direction VARCHAR(10) NOT NULL,
    transaction_status VARCHAR(20) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_date_id	INT NOT NULL,
    foreign key(wallet_id) references dim_wallet(wallet_id),
    foreign key(event_id) references fact_event(event_id),
    foreign key(transaction_date_id) references dim_date(date_id)
      );