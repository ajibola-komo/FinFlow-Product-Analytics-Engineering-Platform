  CREATE OR REPLACE TABLE FACT_TRANSACTION( 
    transaction_id INT primary key,
    wallet_id INT NOT NULL,
    transaction_type_id INT NOT NULL,
    transaction_amount DECIMAL(18,2) NOT NULL,
    transaction_status VARCHAR(20) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_date_id	INT NOT NULL
    foreign key(wallet_id) references dim_wallet(wallet_id),
    foreign key(transaction_type_id) references dim_transaction_type(transaction_type_id),
    foreign key(transaction_date_id) references dim_date(date_id)
      );