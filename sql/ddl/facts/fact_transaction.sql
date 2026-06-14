  CREATE OR REPLACE TABLE FACT_TRANSACTION( 
    transaction_id BIGINT,
    wallet_id INT NOT NULL,
    transaction_type_id INT,
    transaction_amount DECIMAL(18,2),
    transaction_status VARCHAR(20),
    transaction_timestamp TIMESTAMP,
    transaction_date_id	INT
      );