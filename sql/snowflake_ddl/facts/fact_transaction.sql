CREATE OR REPLACE TABLE  FACT_TRANSACTION( 
    transaction_id INT primary key,
    wallet_id INT NOT NULL,
    transaction_type_id INT NOT NULL,
    transaction_amount DECIMAL(18,2) NOT NULL,
    transaction_status VARCHAR(20) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_date_id	INT NOT NULL
);